"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Location, Media, Like, Comment, Follower, Feed 
#from models import Person

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ModelesDB.db"
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    new_user = User(username=data['username'], email=data['email'], password=data['password'], name=data['name'], lastname=data['lastname'], age=data['age']) # type: ignore
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created sucessfully'}), 201


@app.route('/users/<int:user_id>', methods=['PUT', 'DELETE']) # type: ignore
def update_or_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'PUT':
        user_data = request.json
        user.username = user_data.get('username', user.username) # type: ignore
        user.email = user_data.get('email', user.email) # type: ignore
        user.password = user_data.get('password', user.password) # type: ignore
        user.name = user_data.get('name', user.name) # type: ignore
        user.lastname = user_data.get('lastname', user.lastname) # type: ignore
        user.age = user_data.get('age', user.age) # type: ignore
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
