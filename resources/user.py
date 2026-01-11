from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import  pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from flask import current_app
from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import UserSchema
from tasks import test_function

blp = Blueprint("Users", 'user', description="Operations on users")

@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        username = user_data.get('username')
        password = user_data.get('password')

        if UserModel.query.filter_by(username=username).first():
            abort(409, message="User already exists.")

        hashed_password = pbkdf2_sha256.hash(password)
        user = UserModel(username=username, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        current_app.queue.enqueue(test_function)
        return user

@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {'message': 'User deleted'}

@blp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        if not current_user:
            abort(401, message="Invalid or missing refresh token.")
        new_token = create_access_token(identity=current_user, fresh=False)
        jit = get_jwt()['jti']
        BLOCKLIST.add(jit)
        return {'access_token': new_token}, 200

@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {'message': 'User logged out successfully.'}, 200

@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        username = user_data.get('username')
        password = user_data.get('password')

        user = UserModel.query.filter_by(username=username).first()

        if user and pbkdf2_sha256.verify(password, user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {'access_token': access_token, "refresh_token": refresh_token}, 200
        abort(401, message="Invalid credentials.")