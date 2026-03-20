from flask import Blueprint, request, jsonify, render_template
from services.transcript_service import process_transcript_pipeline
from utils.session_utils import get_session_id
import uuid

transcript_bp = Blueprint("transcript", __name__)

@transcript_bp.route("/transcript", methods=["GET"])
def page():
    return render_template("transcript.html")

@transcript_bp.route("/transcript", methods=["POST"])
def save():
    session_id = get_session_id()
    url = request.form.get("url")

    if not url:
        return jsonify({"error": "URL required"}), 400

    try:
        process_transcript_pipeline(session_id, url)
        return jsonify({"message": "Transcript Loaded Successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500