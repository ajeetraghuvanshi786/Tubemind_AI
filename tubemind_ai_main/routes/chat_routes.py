from flask import Blueprint, request, jsonify, session
from services.chatbot_service import generate_chat_reply
from utils.session_utils import get_session_id
import uuid

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    session_id = get_session_id()

    data = request.json
    msg = data.get("message")
    lang = data.get("language", "English")

    if not msg:
        return jsonify({"error": "Message required"}), 400

    try:
        reply = generate_chat_reply(session_id, msg, lang)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500