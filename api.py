

from flask_restful import Resource
from functions import *
from routing import app
from flask import jsonify
from db_model import db
from setup import api
import requests
import json
import random

quiz_questions = open('questions.json', encoding="UTF8")
quiz_questions = json.load(quiz_questions)


class Registering(Resource):
    def post(self):
        response, email, username, password, repassword = check_if_values_are_empty(
            "email", "username", "password", "repassword")
        if response.status == "200 OK":
            response = register_user(email, username, password, repassword)
        return response


class Logging(Resource):
    #   returns jwt token for the user if the credentials are correct,
    #   the token stores user's uuid, email, creation and expiration date
    #   and is used with every single request for user authenthication
    def post(self):
        response, email, password = check_if_values_are_empty(
            "email", "password")
        try:
            never_expire = is_str_true(request.json['never_expire'])
        except KeyError:
            never_expire = False
        if response.status == "200 OK":
            response = login_user(email, password, never_expire)
        return response


class Quizing(Resource):

    def get(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            user = User.query.filter_by(
                user_id=user_id).first()
            answered_questions = json.loads(user.answered_questions)
            available_questions = []
            for i in range(len(quiz_questions)):
                if i not in answered_questions:
                    available_questions.append(i)
            if available_questions == []:
                #user.answered_questions = "[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]"
                #db.session.commit()
                response = Response(
                    json.dumps(
                        {
                            "error": "No questions left.",
                            "score": user.score
                        }),
                    status=200, mimetype='application/json')
                return response
            generated_id = random.choice(available_questions)
            user.last_generated_question = generated_id
            question = quiz_questions[generated_id]
            db.session.commit()
            response = Response(
                json.dumps(
                    {
                        "question": question,
                        "score": user.score
                    }),
                status=200, mimetype='application/json')
        return response

    def post(self):
        response, chosen = check_if_values_are_empty(
            "chosen")
        if response.status == "200 OK":   
            response, user_id = verify_jwt()
        else:
            return response
        if response.status == "200 OK":   
            user = User.query.filter_by(
                user_id=user_id).first()
            generated_id = user.last_generated_question
            question = quiz_questions[generated_id]
            correct_answer = question["options"][question["correct_option"]]
            response = Response(
                    json.dumps({"result": "incorrect"}),
                    status=200, mimetype='application/json')
            if correct_answer == chosen:
                user.score += 1
                response = Response(
                    json.dumps({"result": "correct"}),
                    status=200, mimetype='application/json')
            answered_questions = json.loads(user.answered_questions)
            answered_questions.append(generated_id)
            user.answered_questions = json.dumps(answered_questions)
            db.session.commit()
        return response


api.add_resource(Logging, "/api/login")
api.add_resource(Registering, "/api/register")
api.add_resource(Quizing, "/api/quiz")


#with app.app_context():
#    User.__table__.drop(db.engine)
#    db.create_all()

if __name__ == '__main__':

    app.run(debug=True)
