# from flask import Blueprint, request, jsonify
# from app.models import applications_collection, users_collection
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.credit_score import calculate_credit_score
# from bson import ObjectId
# from bson.errors import InvalidId 

# loan_bp = Blueprint('loan', __name__)

# @loan_bp.route('/apply-loan', methods=['POST'])
# @jwt_required()
# def apply_loan():
#     user_identity = get_jwt_identity()
#     user_id = user_identity['id']
    
#     data = request.json
#     required_fields = ['amount', 'tenure', 'purpose']
#     if not all(field in data for field in required_fields):
#         return jsonify({'error': 'Missing required fields'}), 400

#     # Fetch user data
#     user = users_collection.find_one({'_id': ObjectId(user_id)})
#     if not user:
#         return jsonify({'error': 'User not found'}), 404

#     # Simulate user financial data for credit scoring
#     user_data = {
#         'income': user.get('income', 5000),  # Default income
#         'existing_loans': user.get('existing_loans', 1),
#         'repayment_history': user.get('repayment_history', 80)  # Default history
#     }

#     # Calculate credit score
#     credit_score = calculate_credit_score(user_data, data)

#     # Loan application status based on credit score
#     status = 'Rejected' if credit_score < 50 else 'Pending'

#     # Insert loan application
#     loan_application = {
#         'user_id': user_id,
#         'amount': data['amount'],
#         'tenure': data['tenure'],
#         'purpose': data['purpose'],
#         'credit_score': credit_score,
#         'status': status,
#         'timestamp': request.date
#     }
#     result = applications_collection.insert_one(loan_application)

#     return jsonify({
#         'message': 'Loan application submitted',
#         'application_id': str(result.inserted_id),
#         'credit_score': credit_score,
#         'status': status
#     }), 201
# @loan_bp.route('/loan-status/<loan_id>', methods=['GET'])
# @jwt_required()
# def loan_status(loan_id):
#     user_identity = get_jwt_identity()
#     user_id = user_identity['id']  # This is a string

#     try:
#         # Convert loan_id to ObjectId
#         loan_object_id = ObjectId(loan_id)
#     except InvalidId:
#         return jsonify({'error': 'Invalid loan ID format'}), 400  # Handle invalid ID format

#     # Fetch loan application
#     application = applications_collection.find_one({
#         '_id': loan_object_id,
#         'user_id': user_id  # Match string with string
#     })

#     if not application:
#         return jsonify({'error': 'Loan application not found'}), 404

#     return jsonify({
#         'application_id': str(application['_id']),
#         'amount': application['amount'],
#         'tenure': application['tenure'],
#         'purpose': application['purpose'],
#         'credit_score': application['credit_score'],
#         'status': application['status']
#     }), 200


from flask import Blueprint, request, jsonify
from app.models import applications_collection, users_collection
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.credit_score import calculate_credit_score
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime

loan_bp = Blueprint('loan', __name__)

# Route to handle loan application
@loan_bp.route('/apply-loan', methods=['POST'])
@jwt_required()  # This decorator requires a valid JWT token
def apply_loan():
    user_identity = get_jwt_identity()  # Get user info from the token
    user_id = user_identity['id']

    # Parse JSON data from the request
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ['amount', 'tenure', 'purpose']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Fetch user data from the database
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Simulate user financial data for credit scoring
    user_data = {
        'income': user.get('income', 5000),  # Default income
        'existing_loans': user.get('existing_loans', 1),
        'repayment_history': user.get('repayment_history', 80)  # Default history
    }

    # Calculate credit score based on user data and application
    credit_score = calculate_credit_score(user_data, data)

    # Determine loan application status based on credit score
    status = 'Rejected' if credit_score < 50 else 'Pending'

    # Insert loan application into the database
    loan_application = {
        'user_id': user_id,
        'amount': data['amount'],
        'tenure': data['tenure'],
        'purpose': data['purpose'],
        'credit_score': credit_score,
        'status': status,
        'timestamp': datetime.utcnow()  # Use current UTC time
    }
    result = applications_collection.insert_one(loan_application)

    # Respond with the loan application details
    return jsonify({
        'message': 'Loan application submitted',
        'application_id': str(result.inserted_id),
        'credit_score': credit_score,
        'status': status
    }), 201


# Route to check the status of a loan application by its ID
@loan_bp.route('/loan-status/<loan_id>', methods=['GET'])
@jwt_required()  # This decorator requires a valid JWT token
def loan_status(loan_id):
    user_identity = get_jwt_identity()
    user_id = user_identity['id']

    try:
        loan_object_id = ObjectId(loan_id)  # Convert loan_id to ObjectId
    except InvalidId:
        return jsonify({'error': 'Invalid loan ID format'}), 400

    # Fetch loan application from the database
    application = applications_collection.find_one({
        '_id': loan_object_id,
        'user_id': user_id  # Ensure that the loan belongs to the authenticated user
    })

    if not application:
        return jsonify({'error': 'Loan application not found'}), 404

    # Return the loan application details
    return jsonify({
        'application_id': str(application['_id']),
        'amount': application['amount'],
        'tenure': application['tenure'],
        'purpose': application['purpose'],
        'credit_score': application['credit_score'],
        'status': application['status']
    }), 200
