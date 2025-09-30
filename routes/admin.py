from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, User, Business, Card, Membership, Transaction
from modules.security import hashpwd
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

# Users
@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    users = User.query.filter(User.role != "admin").all()
    return jsonify([{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role
    } for u in users]), 200

@admin_bp.route("/users", methods=["POST"])
@admin_required
def add_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    role = data.get("role", "customer")

    if role not in ["customer", "business"]:
        return jsonify({"error": "Role must be customer or business"}), 400

    if User.query.filter_by(email=email.lower()).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(email=email.lower(), password=hashpwd(password), full_name=full_name, role=role)
    db.session.add(user)
    db.session.commit()

    card_number = None
    if role == "customer":
        card_number = f"CARD{user.id:06d}"
        card = Card(card_number=card_number, user_id=user.id)
        db.session.add(card)
        db.session.commit()

    return jsonify({
        "message": "User added",
        "user_id": user.id,
        "card_number": card_number
    }), 201

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role == "admin":
        return jsonify({"error": "Cannot delete admin"}), 403
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# Businesses
@admin_bp.route("/businesses", methods=["GET"])
@admin_required
def list_businesses():
    businesses = Business.query.all()
    return jsonify([{
        "id": b.id,
        "name": b.name,
        "category": b.category,
        "contact_email": b.contact_email,
        "contact_phone": b.contact_phone
    } for b in businesses]), 200

@admin_bp.route("/businesses", methods=["POST"])
@admin_required
def add_business():
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

    business = Business(name=name, category=category, contact_email=contact_email.lower(),
                        contact_phone=contact_phone, password=hashpwd(password))
    db.session.add(business)
    db.session.commit()
    return jsonify({"message": "Business added"}), 201

@admin_bp.route("/businesses/<int:business_id>", methods=["DELETE"])
@admin_required
def delete_business(business_id):
    business = Business.query.get(business_id)
    if not business:
        return jsonify({"error": "Business not found"}), 404
    db.session.delete(business)
    db.session.commit()
    return jsonify({"message": "Business deleted"}), 200

# Admin adjust points
@admin_bp.route("/memberships/<int:membership_id>/adjust_points", methods=["PATCH"])
@admin_required
def admin_adjust_points(membership_id):
    data = request.get_json()
    delta = data.get("points")
    description = data.get("description", "Adjusted by admin")
    if delta is None:
        return jsonify({"error": "Points delta required"}), 400

    membership = Membership.query.get(membership_id)
    if not membership:
        return jsonify({"error": "Membership not found"}), 404

    membership.points_balance += delta
    if membership.points_balance < 0:
        membership.points_balance = 0

    now = datetime.now()
    txn = Transaction(
        membership_id=membership.id,
        points_earned=delta if delta > 0 else 0,
        points_redeemed=-delta if delta < 0 else 0,
        description=f"[Admin] {description}",
        txn_date=now.date(),
        txn_time=now.time()
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Points updated successfully",
        "membership_id": membership.id,
        "new_points_balance": membership.points_balance
    }), 200

# Admin view all transactions
@admin_bp.route("/transactions", methods=["GET"])
@admin_required
def view_all_transactions():
    transactions = Transaction.query.all()
    result = []
    for t in transactions:
        card = t.membership.card
        user = card.user if card else None
        business = t.membership.business if t.membership else None
        result.append({
            "transaction_id": t.id,
            "customer_name": user.full_name if user else "Unknown",
            "customer_email": user.email if user else "Unknown",
            "business_name": business.name if business else "Unknown",
            "membership_id": t.membership_id,
            "tier": t.membership.membership_tier if t.membership else None,
            "txn_date": t.txn_date.isoformat() if t.txn_date else None,
            "txn_time": t.txn_time.strftime("%H:%M:%S") if t.txn_time else None,
            "amount": t.amount,
            "points_earned": t.points_earned,
            "points_redeemed": t.points_redeemed,
            "description": t.description
        })
    return jsonify(result), 200
