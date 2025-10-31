from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import Business, User, Card, Membership, Transaction, db
from datetime import datetime

business_bp = Blueprint("business", __name__)

def business_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "business":
            return jsonify({"error": "Business access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@business_bp.route("/users", methods=["GET"])
def get_email():
    users = User.query.filter(User.role != "admin").all()
    return jsonify([{
        "email": u.email,
    } for u in users]), 200

@business_bp.route("/memberships", methods=["GET"])
@business_required
def view_memberships():
    email = get_jwt_identity()
    business = Business.query.filter_by(contact_email=email).first()
    memberships = Membership.query.filter_by(business_id=business.id).all()
    result = []
    for m in memberships:
        card = Card.query.filter_by(id=m.card_id).first()
        user = card.user if card else None
        result.append({
            "membership_id": m.id,
            "customer_name": user.full_name if user else "Unknown",
            "customer_email": user.email if user else "Unknown",
            "tier": m.membership_tier,
            "points_balance": m.points_balance
        })
    return jsonify(result), 200

@business_bp.route("/memberships", methods=["POST"])
@business_required
def add_membership():
    data = request.get_json()
    customer_email = data.get("customer_email")
    membership_tier = data.get("membership_tier", "Standard")

    if not customer_email:
        return jsonify({"error": "Customer email required"}), 400

    customer = User.query.filter_by(email=customer_email.lower(), role="customer").first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    card = Card.query.filter_by(user_id=customer.id).first()
    if not card:
        return jsonify({"error": "Customer has no card"}), 400

    email = get_jwt_identity()
    business = Business.query.filter_by(contact_email=email).first()
    existing = Membership.query.filter_by(card_id=card.id, business_id=business.id).first()
    if existing:
        return jsonify({"error": "Membership already exists"}), 409

    new_membership = Membership(card_id=card.id, business_id=business.id, membership_tier=membership_tier)
    db.session.add(new_membership)
    db.session.commit()
    return jsonify({"message": "Membership added successfully"}), 201

@business_bp.route("/memberships/<int:membership_id>/adjust_points", methods=["PATCH"])
@business_required
def business_adjust_points(membership_id):
    data = request.get_json()
    delta = data.get("points")
    description = data.get("description", "Adjusted by business")

    if delta is None:
        return jsonify({"error": "Points delta required"}), 400

    email = get_jwt_identity()
    business = Business.query.filter_by(contact_email=email).first()
    membership = Membership.query.get(membership_id)
    if not membership or membership.business_id != business.id:
        return jsonify({"error": "Membership not found for your business"}), 404

    membership.points_balance += delta
    if membership.points_balance < 0:
        membership.points_balance = 0

    now = datetime.now()
    txn = Transaction(
        membership_id=membership.id,
        points_earned=delta if delta > 0 else 0,
        points_redeemed=-delta if delta < 0 else 0,
        description=f"[Business] {description}",
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

@business_bp.route("/transactions", methods=["GET"])
@business_required
def view_transactions():
    email = get_jwt_identity()
    business = Business.query.filter_by(contact_email=email).first()
    memberships = Membership.query.filter_by(business_id=business.id).all()
    membership_ids = [m.id for m in memberships]

    transactions = Transaction.query.filter(Transaction.membership_id.in_(membership_ids)).all()
    result = []
    for t in transactions:
        card = t.membership.card
        user = card.user if card else None
        result.append({
            "transaction_id": t.id,
            "customer_name": user.full_name if user else "Unknown",
            "customer_email": user.email if user else "Unknown",
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
