"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from admin import setup_admin
from datetime import timedelta
from flask import Flask, request, jsonify, url_for
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_migrate import Migrate
from flask_swagger import swagger
from models import db, User, Location, Media, Like, Comment, Follower, Feed
from utils import APIException, generate_sitemap 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ModelesDB.db"
app.config["SECRET_KEY"] = "MY_SECRET_KEY"
app.config["JWT_SECRET_KEY"] = "MY_SECRET_KEY_JWT"
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
expires_jwt = timedelta(days=1)

@app.route('/', methods=['GET'])
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify(users_list), 200

@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = User()
    new_user.username = data['username']
    new_user.email = data['email']
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf8')
    new_user.password = password_hash
    new_user.name = data['name']
    new_user.lastname = data['lastname']
    new_user.age = data['age']

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created sucessfully'}), 201

@app.route('/users/<int:user_id>', methods=['PUT', 'DELETE']) # type: ignore
def update_or_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'PUT':
        user_data = request.get_json()

        #Esto se asegura de que user_data es un diccionario
        if not isinstance(user_data, dict):
            return jsonify({'error': 'Invalid data format'}), 400
        
        user.username = user_data.get('username', user.username) # type: ignore
        user.email = user_data.get('email', user.email) # type: ignore

        #Esto hashea las nuevas contraseñas
        if 'password' in user_data:
            user.password = bcrypt.generate_password_hash(user_data['password']).decode('utf8')

        user.name = user_data.get('name', user.name) # type: ignore
        user.lastname = user_data.get('lastname', user.lastname) # type: ignore
        user.age = user_data.get('age', user.age) # type: ignore
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'id': user.id, 'email': user.email}, expires_delta=expires_jwt)
        return jsonify({'message': 'Login successful', 'data': user.serialize(), 'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401    

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
