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

# Database objects
uobj = dbm.users()
vobj = dbm.vendors()

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
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    valid = sec.verify_login(email, password)
    if not valid[0]:
        if valid[1] == "usr":
            return jsonify({"error": "email does not exist"}), 404
        else:
            return jsonify({"error": "Wrong password"}), 401
    else:
        role = dbm.get_role(email)
        atok = create_access_token(
            identity=email,
            additional_claims={"role": role}
        )
        return jsonify({
            "message": "Login successful",
            "token": atok
        }), 200


@app.route("/register/user", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    fullname = data.get("fullname", "").strip()
    phone = data.get("phone", "").strip()

    if not util.valid_mail(email):
        return jsonify({"error": "Invalid email format"}), 400

    if not all([email, password, fullname, phone]):
        return jsonify({"error": "All fields are required"}), 400

    user_data = [fullname, phone, email, password]

    if uobj.add(user_data):
        return jsonify({"message": "Registration successful"}), 201
    else:
        return jsonify({"error": f"email {email} already exists"}), 409


@app.route("/register/vendor", methods=["POST"])
def register_vendor():
    data = request.get_json()
    business_name = data.get("business_name", "").strip()
    category = data.get("category", "").strip()
    contact_email = data.get("contact_email", "").strip()
    contact_phone = data.get("contact_phone", "").strip()

    # Validation
    if not all([business_name, contact_email, contact_phone]):
        return jsonify({"error": "Business name, email, and phone are required"}), 400

    if not util.valid_mail(contact_email):
        return jsonify({"error": "Invalid email format"}), 400

    vendor_data = [business_name, category, contact_email, contact_phone]

    if vobj.add(vendor_data):  # Vendor class instance (like uobj for Users)
        return jsonify({"message": "Vendor registration successful"}), 201
    else:
        return jsonify({"error": f"Vendor with email {contact_email} already exists"}), 409




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