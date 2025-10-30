from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date # Added 'date' for Transaction model

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / customer / business
    full_name = db.Column(db.String(100))
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    # Updated relationship with cascade: deleting a User will delete its Cards,
    # and deleting a Card will remove it from this list (orphan)
    cards = db.relationship("Card", backref="user", lazy=True, cascade="all, delete-orphan")

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    contact_email = db.Column(db.String(100), unique=True, nullable=False)
    contact_phone = db.Column(db.String(15))
    password = db.Column(db.String(256), nullable=False)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    # Updated relationship: deleting a Business will delete its Memberships
    memberships = db.relationship("Membership", backref="business", lazy=True, cascade="all, delete-orphan")

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), unique=True, nullable=False)
    # The ForeignKey definition remains the same
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issued_on = db.Column(db.DateTime, default=datetime.utcnow)
    # Updated relationship: deleting a Card will delete its Memberships
    memberships = db.relationship("Membership", backref="card", lazy=True, cascade="all, delete-orphan")

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # ForeignKeys remain the same
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    membership_tier = db.Column(db.String(50))
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    points_balance = db.Column(db.Integer, default=0)
    # Updated relationship: deleting a Membership will delete its Transactions
    transactions = db.relationship("Transaction", backref="membership", lazy=True, cascade="all, delete-orphan")

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    # Using date() for Date column and time() for Time column
    txn_date = db.Column(db.Date, default=date.today) # Use date.today() for Date
    txn_time = db.Column(db.Time, default=datetime.now().time) # Use datetime.now().time() for Time
    amount = db.Column(db.Float, default=0)
    points_earned = db.Column(db.Integer, default=0)
    points_redeemed = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255))
    # No further relationships defined for Transaction, so no cascade needed here