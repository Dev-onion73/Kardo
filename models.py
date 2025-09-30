from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / customer / business
    full_name = db.Column(db.String(100))
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    cards = db.relationship("Card", backref="user", lazy=True)

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    contact_email = db.Column(db.String(100), unique=True, nullable=False)
    contact_phone = db.Column(db.String(15))
    password = db.Column(db.String(256), nullable=False)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    memberships = db.relationship("Membership", backref="business", lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issued_on = db.Column(db.DateTime, default=datetime.utcnow)
    memberships = db.relationship("Membership", backref="card", lazy=True)

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    membership_tier = db.Column(db.String(50))
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    points_balance = db.Column(db.Integer, default=0)
    transactions = db.relationship("Transaction", backref="membership", lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    txn_date = db.Column(db.Date, default=datetime.utcnow)
    txn_time = db.Column(db.Time, default=datetime.utcnow)
    amount = db.Column(db.Float, default=0)
    points_earned = db.Column(db.Integer, default=0)
    points_redeemed = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255))
