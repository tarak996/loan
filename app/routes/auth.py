from flask import Blueprint, request, jsonify
from app.models import users_collection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409
    
    hashed_password = generate_password_hash(data['password'])
    users_collection.insert_one({
        'name': data.get('name', ''),
        'email': data['email'],
        'phone': data.get('phone', ''),
        'password': hashed_password,
        'role': 'user'
    })
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = users_collection.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = create_access_token(identity={'id': str(user['_id']), 'role': user['role']})
    return jsonify({'token': token}), 200
