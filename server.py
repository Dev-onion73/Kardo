from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from models import db, User, Business, Card
from modules.security import hashpwd
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.customer import customer_bp
from routes.business import business_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB + JWT
    db.init_app(app)
    JWTManager(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(business_bp, url_prefix="/business")

    # Create DB + default admin
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email="admin@kardo.com").first()
        if not admin:
            new_admin = User(
                email="admin@kardo.com",
                password=hashpwd("admin"),
                role="admin",
                full_name="Admin User"
            )
            db.session.add(new_admin)
            db.session.commit()
            print("✅ Default admin created")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
