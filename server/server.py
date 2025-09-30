from flask import Flask, request, jsonify, Response,send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from ast import literal_eval
from datetime import datetime, timedelta
import pandas as pd
import os, sys, redis, time, io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setting Working Directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


# custom modules
import modules.dbmanage as dbm
import modules.security as sec
import modules.utilities as util

from modules.reminder import trigger_daily
from modules.utilities import apitools
from modules.caching import *

# Database objects
uobj = dbm.users()


######## START

app = Flask(__name__) # , static_folder="dist/assets", template_folder="dist") # Use after compiling frontend to serve with flask

print("Getting Secrets....")
secrets = sec.get_secrets()
if(secrets != None):
    app.config["JWT_SECRET_KEY"] = secrets["SECRET_KEY"]
else:
    print("Secrets Missing Exiting.....")
    exit()

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24) # increase hours
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"  # default
app.config["JWT_HEADER_TYPE"] = "Bearer"   

CORS(app, supports_credentials=True)
jwt = JWTManager(app)
api = Api(app)

# init_redis(host='localhost', port=6379, db=0)


# JWT Role Extraction code
def jwt_role():
    return get_jwt().get("role") 


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    valid = sec.verify_login(username, password)
    if not valid[0]:
        if valid[1] == "usr":
            return jsonify({"error": "Username does not exist"}), 404
        else:
            return jsonify({"error": "Wrong password"}), 401
    else:
        role = dbm.get_role(username)
        atok = create_access_token(
            identity=username,
            additional_claims={"role": role}
        )
        return jsonify({
            "message": "Login successful",
            "token": atok
        }), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    fullname = data.get("fullname", "").strip()
    qualification = data.get("qualification", "").strip()
    dob = data.get("dob", "").strip()

    if not util.valid_mail(username):
        return jsonify({"error": "Invalid email format"}), 400

    if not all([username, password, fullname, qualification, dob]):
        return jsonify({"error": "All fields are required"}), 400

    user_data = [username, password, fullname, qualification, dob]

    if uobj.add(user_data):
        return jsonify({"message": "Registration successful"}), 201
    else:
        return jsonify({"error": f"Username {username} already exists"}), 409



################################################################### API





#### Cache invalidator
@app.route("/inval/")
def inval():
    flush_cache()
    return {"msg":"ok"}


## Compile or bundle frontend into dist/ and uncomment

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve_vue(path):
#     return send_from_directory(app.template_folder, 'index.html')


if __name__ == '__main__':
    sec.start_checkup()
    app.run(debug=True)