from flask import Blueprint, render_template, request
from repositories.transcript_repository import get_latest_transcript
from services.quiz_service import process_quiz
from utils.session_utils import get_session_id
import uuid

quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():
    session_id = get_session_id()
    transcript = get_latest_transcript(session_id)

    if not transcript:
        return render_template("quiz.html",
                               error="⚠ Please load transcript first.")

    if request.method == "POST":
        try:
            lang = request.form.get("language")
            difficulty = request.form.get("difficulty")
            number = int(request.form.get("number"))

            questions, answers = process_quiz(
                transcript, number, difficulty, lang, session_id
            )

            return render_template("quiz.html",
                                   questions=questions,
                                   answers=answers)

        except Exception:
            return render_template("quiz.html",
                                   error="⚠ Failed to generate quiz.")

    return render_template("quiz.html")