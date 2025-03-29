from decimal import Decimal

from flask import Blueprint, current_app, jsonify, redirect, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from backend.extensions import create_logger, db
from backend.models import (
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
    UserBalance,
)
from backend.src.OAuthSignIn import OAuthSignIn

logger = create_logger(__name__, level="DEBUG")

base_bp = Blueprint("base", __name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


@base_bp.route("/")
def index():
    return jsonify({"message": "Hello, World!"})


@billing_bp.route("/balance", methods=["GET"])
@jwt_required()
def get_balance():
    """Get current user's balance"""
    user_id = get_jwt_identity()
    balance = UserBalance.query.filter_by(user_id=user_id).first()

    if not balance:
        # Create initial balance with $5.00 for new users
        balance = UserBalance(user_id=user_id)
        db.session.add(balance)
        db.session.commit()

    return jsonify(balance.to_dict())


@billing_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    user_id = get_jwt_identity()
    application = request.args.get("application")  # Optional filter by application

    query = Transaction.query.filter_by(user_id=user_id)
    if application:
        query = query.filter_by(application=application)

    transactions = query.order_by(Transaction.created_at.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


@billing_bp.route("/balance/add", methods=["POST"])
@jwt_required()
def add_funds():
    """Add funds to user's balance"""
    user_id = get_jwt_identity()
    data = request.get_json()
    amount = Decimal(str(data.get("amount", 0)))

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    balance = UserBalance.query.filter_by(user_id=user_id).first()
    if not balance:
        balance = UserBalance(user_id=user_id)
        db.session.add(balance)

    # Create transaction record
    transaction = Transaction(
        user_id=user_id,
        balance_id=balance.id,
        application=data.get(
            "application", "platform"
        ),  # Track which app initiated the purchase
        amount=amount,
        transaction_type=TransactionType.PURCHASE,
        status=TransactionStatus.COMPLETED,
        transaction_metadata=data.get("metadata"),
    )
    db.session.add(transaction)

    # Update balance
    balance.credit(amount)
    db.session.commit()

    return jsonify({"balance": balance.to_dict(), "transaction": transaction.to_dict()})


@auth_bp.route("/authorize/<provider>")
@jwt_required(optional=True)
def oauth_authorize(provider):

    user_id = get_jwt_identity()
    if user_id:
        return redirect(f"{current_app.config['FRONTEND_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize(next_path=request.args.get("next", "/"))


@auth_bp.route("/callback/<provider>")
@jwt_required(optional=True)
def oauth_callback(provider):

    user_id = get_jwt_identity()
    if user_id:
        return redirect(f"{current_app.config['FRONTEND_URL']}/")

    oauth = OAuthSignIn.get_provider(provider)
    try:
        social_id, name, email, picture = oauth.callback()
    except Exception as e:
        print(e)
        return jsonify({"error": "No social id found"}), 400

    if social_id is None:
        return jsonify({"error": "No social id found"}), 400

    if provider == "google":
        user = User.query.filter_by(google_id=social_id).first()
    elif provider == "apple":
        user = User.query.filter_by(apple_id=social_id).first()
    else:
        raise ValueError(f"Invalid provider: {provider}")
    # TODO: reconcile different emails
    if not user:
        if provider == "google":
            user = User(google_id=social_id, name=name, email=email, image=picture)
        elif provider == "apple":
            user = User(apple_id=social_id, name=name, email=email, image=picture)
        else:
            raise ValueError(f"Invalid provider: {provider}")
        db.session.add(user)
        db.session.commit()
    else:
        if name:
            user.name = name
        if email:
            user.email = email
        if picture:
            user.image = picture
        db.session.commit()

    # Get the next parameter from the OAuth state
    next_path = request.args.get("state", "/")

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "name": user.name,
            "email": user.email,
            "image": user.image,
        },
    )

    redirect_url = f"{current_app.config['FRONTEND_URL']}/auth?access_token={access_token}&next={next_path}"
    print(f"Redirecting to: {redirect_url}")
    return redirect(redirect_url)
