#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):

        data = request.get_json()

        if data.get('username') is not None:
            new_user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio'),
            )
            new_user.password_hash=data.get('password')
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        else:
            return {"message": "Entry could not be processed"}, 422

class CheckSession(Resource):

    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        else:
            return {"message": "Unauthorized log in"}, 401

class Login(Resource):
    
    def post(self):

        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()

        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {"message": "User not found"}, 401

class Logout(Resource):
    
    def delete(self):
        if not session['user_id']:
            return {"message": "Unauthorized access"}, 401
        else:
            session['user_id'] = None
            return {}, 204

class RecipeIndex(Resource):
    
    def get(self):
        
        if session['user_id']:
            user_id = session['user_id']
            recipes = [recipe.to_dict() for recipe in Recipe.query.filter(Recipe.user_id == user_id)]
            return make_response(jsonify(recipes), 200)
        else:
            return {"message": "Unauthorized log in"}, 401

    def post(self):

        if session['user_id']:
            data = request.get_json()

            new_recipe = Recipe(
                title=data.get('title'),
                instructions=data.get('instructions'),
                minutes_to_complete=data.get('minutes_to_complete')
            )
            new_recipe.user_id = session['user_id']

            if new_recipe.instructions is not None:
                db.session.add(new_recipe)
                db.session.commit()

                return new_recipe.to_dict(), 201
            else:
                return {"message": "Could not add recipe"}, 422
        else:
            return {"message": "User not logged in"}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)