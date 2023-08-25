
from flask import request, Response
import json
from exceptions import *
from db_model import User, db
from uuid import uuid4
from bcrypt import hashpw, gensalt, checkpw
import jwt
from setup import jwt_key
from datetime import datetime, timedelta


def is_str_true(string):
    if str(string).lower() == "true" or string is True:
        return True
    return False


def parse_args_from_body(*args):
    try:
        args_table = []
        for arg in args:
            args_table.append(request.json[str(arg)])
        response = Response(
            json.dumps({
                "success": "OK."}),
            status=200, mimetype='application/json')
#   KeyError happens when arg is not found in request.json
    except KeyError:
        args_table = list(args)
        response = Response(
            json.dumps({"error": """One or more neccessary \
values not provided in request body!"""}),
            status=400, mimetype='application/json')
    return response, args_table


def check_if_values_are_empty(*args):
    response, args_table = parse_args_from_body(*args)
    if response.status == "200 OK":
        for value in args_table:
            if value is None or value == "":
                response = Response(
                    json.dumps({
                        "error": "One or more fields are empty."}),
                    status=400, mimetype='application/json')
                break
    result_tuple = tuple([response] + args_table)
    return result_tuple


def register_user(email, username, password, repassword):
    try:
        if "@" not in email or "." not in email:
            raise InvalidEmailException
        user = User.query.filter_by(email=email).first()
        if user is not None:
            response = Response(
                json.dumps({"error": "Email alredy in use!"}),
                status=400, mimetype='application/json')
        elif password != repassword:
            response = Response(
                json.dumps({"error": "Passwords do not match!"}),
                status=400, mimetype='application/json')
        else:
            password = hashpw(
                password.encode("utf-8"),
                gensalt(14)).decode("utf-8")
            user_uuid = uuid4()
            user_uuid = str(user_uuid)
            new_user = User(user_uuid, username, email, password, "[]", 0, 0)
            db.session.add(new_user)
            db.session.commit()
            #new_user_id = new_user.user_id
            response = Response(
                json.dumps({"success": "Successfully created account."}),
                status=201, mimetype='application/json')
    except InvalidEmailException:
        response = Response(
                json.dumps({"error": "Invalid email."}),
                status=400, mimetype='application/json')
    return response


def login_user(email, password, never_expire, oauth=False):
    user = User.query.filter_by(email=email).first()
    if user is None:
        response = Response(
            json.dumps({"error": "User not found!"}),
            status=400, mimetype='application/json')
    elif checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        if never_expire is True:
            expiration_date = str(datetime.today() + timedelta(
                days=9999))
        else:
            expiration_date = str(datetime.today() + timedelta(
                hours=12))
        TOKEN = jwt.encode({'uuid': user.uuid,
                            'creation_date': str(datetime.today()),
                            'expiration_date': expiration_date
                            }, jwt_key)
        response = Response(
            json.dumps({'token': TOKEN,
                        'uuid': user.uuid,
                        'username': user.username}),
            status=202, mimetype='application/json')
    else:
        response = Response(
            json.dumps({"error": "Wrong password!"}), status=400,
            mimetype='application/json')
    return response


def verify_jwt(token=None):
    user_id = None
    try:
        if token is None:
            token = request.headers.get('Authorization')
        if token is None or token == "":
            response = Response(
                json.dumps(
                    {"error": "No token found in Authorization header."}),
                status=400, mimetype='application/json')
        else:
            token = token.replace("Bearer ", "")
            token = jwt.decode(token, jwt_key, 'HS256')
            uuid = token['uuid']
            user = User.query.filter_by(uuid=uuid).first()
            expiration_date = datetime.strptime(
                token['expiration_date'], "%Y-%m-%d %H:%M:%S.%f")
            creation_date = datetime.strptime(
                token['creation_date'], "%Y-%m-%d %H:%M:%S.%f")
            acceptable_creation_date = datetime.strptime(
                user.acceptable_token_creation_date, "%Y-%m-%d %H:%M:%S.%f")
            if expiration_date < datetime.today() or \
                    creation_date < acceptable_creation_date:
                raise WrongDateError
            if user is not None:
                user_id = user.user_id
                response = Response(
                        json.dumps({
                            "success": "Signature verification succeded."}),
                        status=200, mimetype='application/json')
            else:
                response = Response(
                        json.dumps({
                            "error": "User not found."}),
                        status=400, mimetype='application/json')
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError,
            AttributeError):
        response = Response(
                json.dumps({"error": "Signature verification failed."}),
                status=401, mimetype='application/json')
    except WrongDateError:
        response = Response(
            json.dumps({"error": "The token has expired!"}),
            status=401, mimetype='application/json')
    return response, user_id