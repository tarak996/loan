def calculate_credit_score(user_data, loan_data):
    """
    Calculate credit score based on predefined criteria.
    This is a simplified version for demonstration.
    """
    income = user_data.get('income', 0)
    existing_loans = user_data.get('existing_loans', 0)
    repayment_history = user_data.get('repayment_history', 0)  # Out of 100

    # Credit score calculation logic
    score = (
        (income / 1000) * 0.4 +         # 40% weight to income
        (100 - existing_loans) * 0.3 + # 30% weight to fewer existing loans
        repayment_history * 0.3        # 30% weight to repayment history
    )
    return min(100, max(0, round(score)))  # Ensure score is between 0 and 100
