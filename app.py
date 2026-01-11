import os

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

import redis
from rq import Queue
from db import db
from blocklist import BLOCKLIST
from dotenv import load_dotenv
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_migrate import Migrate
from config import Config

# Load environment variables at module level for Flask CLI commands
load_dotenv()

def create_app(db_url=None):
    app = Flask(__name__)
    # Fix Redis connection with proper fallback
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        connection = redis.from_url(redis_url)
        app.queue = Queue("emails", connection=connection)
    except Exception as e:
        print(f"Redis connection failed: {e}")
        app.queue = None
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET"] = "my_secret_key_token"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has been revoked.", "error": "token_revoked"}, 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return {"message": "The token is not fresh.", "error": "fresh_token_required"}, 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # Check in the db if the user is admin or not in real life example
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has expired.", "error": "token_expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "Signature verification failed.", "error": "invalid_token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"message": "Request does not contain an access token.", "error": "authorization_required"}, 401

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
