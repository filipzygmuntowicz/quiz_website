
from setup import api
from routing import app
from api_endpoints import Logging, Registering, Quizing, Reset_Quiz,\
    Weather_Data


api.add_resource(Logging, "/api/login")
api.add_resource(Registering, "/api/register")
api.add_resource(Quizing, "/api/quiz")
api.add_resource(Reset_Quiz, "/api/reset_quiz")
api.add_resource(Weather_Data, "/api/weather")


if __name__ == '__main__':
    app.run()
