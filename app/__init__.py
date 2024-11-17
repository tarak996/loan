from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import os

app = Flask(__name__)

# Load configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')

# Initialize MongoDB
mongo_client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
db = mongo_client['credit_scoring_db']

# Initialize JWT
jwt = JWTManager(app)

# Blueprint registration will go here
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.routes.loan import loan_bp
app.register_blueprint(loan_bp, url_prefix='/loan')

from app.routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')


from flask import render_template

@app.route('/')
def home():
    return render_template('/register.html')

@app.route('/login')
def login():
    return render_template('/login.html')

@app.route('/status')
def status():
    return render_template('/status.html')


@app.route('/apply-loan')
def apply_loan():
    return render_template('/application.html')

@app.route('/admin_dashboard')
def admin():
    return render_template('/admin_dashboard.html')
