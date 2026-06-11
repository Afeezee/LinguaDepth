from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ml.classifier import ProficiencyClassifier
from models import User, db

ml_bp = Blueprint("ml", __name__)


@ml_bp.route("/classify", methods=["POST"])
@jwt_required()
def classify():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id") or int(get_jwt_identity())

    # Users may only classify themselves
    if user_id != int(get_jwt_identity()):
        return jsonify({"error": "Forbidden"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    classifier = ProficiencyClassifier()
    result = classifier.should_promote(user_id, db.session)
    return jsonify(result)
