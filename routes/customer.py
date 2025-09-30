from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import User, Card, Membership, Transaction

customer_bp = Blueprint("customer", __name__)

def customer_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "customer":
            return jsonify({"error": "Customer access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@customer_bp.route("/card", methods=["GET"])
@customer_required
def get_card():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email, role="customer").first()
    if not user:
        return jsonify({"error": "Customer not found"}), 404

    card = Card.query.filter_by(user_id=user.id).first()
    if not card:
        return jsonify({"error": "Card not assigned yet"}), 404

    return jsonify({
        "card_id": card.id,
        "card_number": card.card_number,
        "issued_on": card.issued_on
    }), 200

@customer_bp.route("/memberships", methods=["GET"])
@customer_required
def get_memberships():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email, role="customer").first()
    card = Card.query.filter_by(user_id=user.id).first()
    if not card:
        return jsonify({"error": "No card assigned"}), 404

    memberships = Membership.query.filter_by(card_id=card.id).all()
    return jsonify([{
        "membership_id": m.id,
        "business_id": m.business_id,
        "tier": m.membership_tier,
        "points_balance": m.points_balance
    } for m in memberships]), 200

@customer_bp.route("/transactions", methods=["GET"])
@customer_required
def get_transactions():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email, role="customer").first()
    if not user:
        return jsonify({"error": "Customer not found"}), 404

    card = Card.query.filter_by(user_id=user.id).first()
    if not card:
        return jsonify({"error": "No card assigned"}), 404

    memberships = Membership.query.filter_by(card_id=card.id).all()
    membership_ids = [m.id for m in memberships]

    transactions = Transaction.query.filter(Transaction.membership_id.in_(membership_ids)).all()
    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "membership_id": t.membership_id,
            "txn_date": t.txn_date.isoformat() if t.txn_date else None,
            "txn_time": t.txn_time.strftime("%H:%M:%S") if t.txn_time else None,
            "amount": t.amount,
            "points_earned": t.points_earned,
            "points_redeemed": t.points_redeemed,
            "description": t.description
        })

    return jsonify(result), 200
