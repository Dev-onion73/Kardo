from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User, Business, Card
from modules.security import hashpwd, verify_hash
import random, string

auth_bp = Blueprint("auth", __name__)

def generate_card_number():
    return ''.join(random.choices(string.digits, k=12))

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not verify_hash(password, user.password):
        return jsonify({"error": "Invalid password"}), 401

    token = create_access_token(identity=email.lower(), additional_claims={"role": user.role})
    return jsonify({"message": "Login successful", "token": token})

@auth_bp.route("/login/business", methods=["POST"])
def login_business():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    business = Business.query.filter_by(contact_email=email.lower()).first()
    if not business:
        return jsonify({"error": "Business not found"}), 404
    if not verify_hash(password, business.password):
        return jsonify({"error": "Invalid password"}), 401

    token = create_access_token(identity=email.lower(), additional_claims={"role": "business"})
    return jsonify({"message": "Login successful", "token": token})

@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not all([email, password, full_name]):
        return jsonify({"error": "All fields required"}), 400

    if User.query.filter_by(email=email.lower()).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(
        email=email.lower(),
        password=hashpwd(password),
        role="customer",
        full_name=full_name
    )
    db.session.add(new_user)
    db.session.commit()

    # Create card automatically
    new_card = Card(card_number=generate_card_number(), user_id=new_user.id)
    db.session.add(new_card)
    db.session.commit()

    return jsonify({"message": "Customer registered successfully"}), 201

@auth_bp.route("/register/business", methods=["POST"])
def register_business():
    data = request.get_json()
    name = data.get("name")
    category = data.get("category")
    contact_email = data.get("contact_email")
    contact_phone = data.get("contact_phone")
    password = data.get("password")

    if not all([name, contact_email, password]):
        return jsonify({"error": "Name, email, and password required"}), 400

    if Business.query.filter_by(contact_email=contact_email.lower()).first():
        return jsonify({"error": "Business already exists"}), 409

    new_business = Business(
        name=name,
        category=category,
        contact_email=contact_email.lower(),
        contact_phone=contact_phone,
        password=hashpwd(password)
    )
    db.session.add(new_business)
    db.session.commit()
    return jsonify({"message": "Business registered successfully"}), 201
