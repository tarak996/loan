from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import applications_collection, logs_collection
from bson import ObjectId
from bson.errors import InvalidId

admin_bp = Blueprint('admin', __name__)

# Endpoint: View all loans
@admin_bp.route('/all-loans', methods=['GET'])
@jwt_required()
def all_loans():
    user_identity = get_jwt_identity()
    
    # Ensure only admins can access this endpoint
    if user_identity['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    # Optional: Filter by status
    status = request.args.get('status')
    query = {}
    if status:
        query['status'] = status

    # Fetch loans
    loans = applications_collection.find(query)
    loan_list = []
    for loan in loans:
        loan_list.append({
            'application_id': str(loan['_id']),
            'user_id': loan['user_id'],
            'amount': loan['amount'],
            'tenure': loan['tenure'],
            'purpose': loan['purpose'],
            'credit_score': loan['credit_score'],
            'status': loan['status']
        })
    
    return jsonify({'loans': loan_list}), 200

# Endpoint: Review a loan
@admin_bp.route('/review-loan/<loan_id>', methods=['POST'])
@jwt_required()
def review_loan(loan_id):
    user_identity = get_jwt_identity()

    # Ensure only admins can access this endpoint
    if user_identity['role'] != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        loan_object_id = ObjectId(loan_id)
    except InvalidId:
        return jsonify({'error': 'Invalid loan ID format'}), 400

    # Fetch loan application
    application = applications_collection.find_one({'_id': loan_object_id})
    if not application:
        return jsonify({'error': 'Loan application not found'}), 404

    # Get admin decision
    data = request.json
    decision = data.get('decision')  # 'Approved' or 'Rejected'
    if decision not in ['Approved', 'Rejected']:
        return jsonify({'error': 'Invalid decision'}), 400

    # Update loan status
    applications_collection.update_one(
        {'_id': loan_object_id},
        {'$set': {'status': decision}}
    )

    # Log the admin action
    logs_collection.insert_one({
        'admin_id': user_identity['id'],
        'loan_id': loan_id,
        'decision': decision,
        'timestamp': request.date
    })

    return jsonify({'message': f'Loan {decision} successfully'}), 200
