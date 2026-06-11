from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from llm.chatbox import chat_response
from models import User

llm_bp = Blueprint("llm", __name__)


@llm_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json(silent=True) or {}

    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    history = data.get("history") or []
    topic = data.get("topic") or "everyday conversation"

    reply = chat_response(history, message, user.level, topic)
    return jsonify({"reply": reply})
