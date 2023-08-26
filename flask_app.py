

from flask_restful import Resource
from functions import *
from routing import app
from db_model import db
from setup import api
import json
import random
import requests
from datetime import datetime

quiz_questions = open('questions.json', encoding="UTF8")
quiz_questions = json.load(quiz_questions)
weekdays = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday"]


class Registering(Resource):
    def post(self):
        response, email, username, password, repassword = \
            check_if_values_are_empty(
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
                response = Response(
                    json.dumps(
                        {
                            "error": "No questions left.",
                            "score": user.score
                        }),
                    status=200, mimetype='application/json')
                if user.high_score <= user.score:
                    user.high_score = user.score
                db.session.commit()
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


class Reset_Quiz(Resource):

    def post(self):
        response, user_id = verify_jwt()
        if response.status == "200 OK":
            user = User.query.filter_by(
                user_id=user_id).first()
            user.answered_questions = "[]"
            user.score = 0
            db.session.commit()
            response = Response(
                json.dumps({"success": "Succsefuly reset quiz for user."}),
                status=200, mimetype='application/json')
            return response
        else:
            return response


class Weather_Data(Resource):

    def get(self):
        city = request.args.get("city")
        try:
            with open("weather_api_key.txt", "r", encoding="utf-8") as file:
                api_key = file.read()
        except FileNotFoundError:
            print("You need to provide api key for weather data.")
            response = Response(
                json.dumps({"error": "Internal server error."}),
                status=500, mimetype='application/json')
            return response
        response = requests.get(
            f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}")
        try:
            data = response.json()[0]
        except IndexError:
            response = Response(
                json.dumps({"error": "Invalid city name."}),
                status=400, mimetype='application/json')
            return response
        lat = data["lat"]
        lon = data["lon"]
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}")
        data = response.json()["list"]
        weather_data = []
        for i in range(3):
            day_index = i*8 + 3
            night_index = i*8 + 7
            day_temp = data[day_index]["main"]["temp"]
            night_temp = data[night_index]["main"]["temp"]
            date = data[night_index]["dt_txt"]
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            weekday = date.weekday()
            date = datetime.strftime(date, "%Y-%m-%d")
            weather_data.append(
                {
                    "date": date,
                    "day_temp": day_temp,
                    "night_temp": night_temp,
                    "weekday": weekdays[weekday]
                })
        response = Response(
                    json.dumps(weather_data),
                    status=200, mimetype='application/json')
        return response


api.add_resource(Logging, "/api/login")
api.add_resource(Registering, "/api/register")
api.add_resource(Quizing, "/api/quiz")
api.add_resource(Reset_Quiz, "/api/reset_quiz")
api.add_resource(Weather_Data, "/api/weather")


#with app.app_context():
#    User.__table__.drop(db.engine)
#    db.create_all()

if __name__ == '__main__':

    app.run(debug=True)
