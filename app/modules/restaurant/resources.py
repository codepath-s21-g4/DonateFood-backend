from flask import g, request, make_response
from flask_restplus import Resource\

from app.extensions import db
from app.extensions.api import abort

from . import restaurant_api
from .models import Restaurant
from app.modules.driver.models import Driver
from app.decorators import requires_auth

from app.modules.food_request.models import FoodRequest
from app.modules.food_request.schemas import FoodRequestSchema

from .schemas import RestaurantSchema

import json


@restaurant_api.route("/create-new-restaurant")
class CreateRestaurant(Resource):

    def post(self):
        """Add new Restaurant object to database"""

        data = request.get_json(force=True)
        print("request", request.get_json(force=True))
        print("data: ", data)
        if 'email' in data.keys():
            email = data['email']
            if Driver.query.filter_by(email=email).scalar():
                abort(400, f"Driver with email '{email}' already exists")
            if Restaurant.query.filter_by(email=email).scalar():
                abort(400, f"Restaurant with email '{email}' already exists")
            else:
                new_user = Restaurant(**data)
                db.session.add(new_user)
                db.session.commit()

                print(f"Restaurant '{email}' successfully created")

        else:
            abort(400, 'Missing email')

        return make_response(f"Restaurant {email} account successfully created", 200)


@restaurant_api.route("/info")
class GetRestaurantObject(Resource):

    decorators = [requires_auth]
    restaurant_schema = RestaurantSchema()
    food_request_schema = FoodRequestSchema()

    def get(self):
        """Get Restaurant Object"""

        user = g.user

        user_schema = self.restaurant_schema.dump(user).data

        food = FoodRequest.query.filter_by(restaurant_id=user.id).first()

        user_schema["food_request"] = {}

        if food:
            food_request = self.food_request_schema.dump(food).data

            user_schema["food_request"] = food_request

        print(f"Restaurant Schema: {user_schema}")
        print(json.dumps(user_schema, indent=4))

        return user_schema


@restaurant_api.route("/update-info")
class UpdateRestaurantInfo(Resource):

    decorators = [requires_auth]

    def put(self):
        """Update restaurant data"""

        data = request.get_json()
        print("update restaurant: ", data)

        if not data:
            abort(400, "Missing restaurant data")

        user = g.user

        try:

            if data["name"] != "":
                user.name = data["name"]
            if data["phone_number"] != "":
                user.phone_number = data["phone_number"]
            if data["address"] != "":
                user.address = data["address"]

        except KeyError:
            abort(400, "Missing restaurant data")

        db.session.commit()

        return make_response(f"Restaurant {user.name} successfully updated info", 200)
