"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
import datetime
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Location, Media, Like, Comment, Follower, Feed, Post
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
import cloudinary
import cloudinary.uploader
#from models import Person

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ModelesDB.db"
app.config['UPLOAD_FOLDER'] = "instance/photos"
db.init_app(app)
CORS(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
expires_jwt = datetime.timedelta(days=5)

          
cloudinary.config( 
  cloud_name = "dp1nq9zvq", 
  api_key = "678483169239916", 
  api_secret = "1_8mRP83pNvQNQVqpu8j5hQyv6Q" 
)

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

@app.route('/feed/new_post', methods=['POST'])
def new_post():
    if 'post_data' not in request.form or 'source_url' not in request.files:
        return jsonify({'error': 'Invalid request'}), 400
    data = request.form['post_data']
    file = request.files['source_url']
    try:
        data = json.loads(data)
    except ValueError:
        return jsonify({'error': 'Invalid JSON'}), 400
    
  
    new_post = Post()
    new_post.description = data["description"]
    new_post.user_id = 1
    new_post.likecount = 0
    new_post.location = 0
    new_post.feed_id = 1
    new_post.date = datetime.datetime.now()

    
    try:
        upload_result = cloudinary.uploader.upload(file)
        new_post.source_url = upload_result['secure_url']
    except Exception as e:
        return jsonify({'error': 'Error uploading to Cloudinary', 'details': str(e)}), 500

    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully'}), 201

@app.route('/feed', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    post_list = [post.serialize() for post in posts]
    return jsonify(post_list), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
