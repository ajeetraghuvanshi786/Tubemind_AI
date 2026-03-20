from flask import Blueprint, request, jsonify, render_template, Response
from langchain_openai import ChatOpenAI
from repositories.transcript_repository import get_latest_transcript, is_faiss_ready
from services.ask_service import ask_question, ask_question_stream
from utils.chatbot_utils import get_chunks, generate_notes
from utils.session_utils import get_session_id
import logging

ask_bp = Blueprint("ask", __name__)


# =========================================================
# ASK ROUTE (MAIN Q&A)
# =========================================================
@ask_bp.route("/ask", methods=["GET", "POST"])
def ask():
    session_id = get_session_id()

    # ------------------------------
    # GET → LOAD PAGE
    # ------------------------------
    if request.method == "GET":
        return render_template("ask.html")

    try:
        question = None

        # ------------------------------
        # INPUT HANDLING (JSON + FORM)
        # ------------------------------
        if request.is_json:
            data = request.get_json()
            question = data.get("question")
        else:
            question = request.form.get("question")

        # ------------------------------
        # VALIDATION
        # ------------------------------
        if not question or not question.strip():
            return jsonify({"error": "Question is required"}), 400

        # ------------------------------
        # CHECK TRANSCRIPT EXISTS
        # ------------------------------
        transcript = get_latest_transcript(session_id)
        if not transcript:
            return jsonify({
                "error": "No transcript found. Please process a video first."
            }), 400

        # ------------------------------
        # CHECK FAISS READY
        # ------------------------------
        if not is_faiss_ready(session_id):
            return jsonify({
                "error": "Transcript is still processing. Please wait a few seconds."
            }), 400

        logging.info(f"[ASK] Question: {question}")

        # ------------------------------
        # SERVICE CALL
        # ------------------------------
        answer = ask_question(session_id, question)

        # ------------------------------
        # RESPONSE
        # ------------------------------
        if request.is_json:
            return jsonify({"answer": answer})
        else:
            return render_template(
                "ask.html",
                answer=answer,
                question=question
            )

    except Exception as e:
        logging.error(f"[ASK ERROR]: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# =========================================================
# STREAMING ANSWERS (CHATGPT STYLE)
# =========================================================
@ask_bp.route("/ask-stream", methods=["POST"])
def ask_stream():
    session_id = get_session_id()

    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "Question required"}), 400

        # FAISS READY CHECK
        if not is_faiss_ready(session_id):
            return jsonify({
                "error": "Transcript still processing"
            }), 400

        def generate():
            try:
                for chunk in ask_question_stream(session_id, question):
                    yield chunk
            except Exception as e:
                logging.error(f"[STREAM ERROR]: {str(e)}")
                yield "Error generating response."

        return Response(generate(), content_type="text/plain")

    except Exception as e:
        logging.error(f"[ASK STREAM ERROR]: {str(e)}")
        return jsonify({"error": "Streaming failed"}), 500


# =========================================================
# GENERATE NOTES
# =========================================================
@ask_bp.route("/notes", methods=["POST"])
def generate_notes_api():
    session_id = get_session_id()

    try:
        transcript = get_latest_transcript(session_id)

        if not transcript:
            return jsonify({"error": "No transcript available"}), 400

        chunks = get_chunks(transcript)

        notes = generate_notes(chunks, session_id)

        return jsonify({"notes": notes})

    except Exception as e:
        logging.error(f"[NOTES ERROR]: {str(e)}")
        return jsonify({"error": "Failed to generate notes"}), 500


# =========================================================
# COMPARE VIDEOS
# =========================================================
@ask_bp.route("/compare", methods=["POST"])
def compare_videos():
    try:
        data = request.get_json()

        urls = data.get("videos")
        question = data.get("question")

        if not urls or len(urls) < 2:
            return jsonify({"error": "Provide at least 2 video URLs"}), 400

        if not question:
            return jsonify({"error": "Question required"}), 400

        from utils.youtube_utils import load_transcript_as_text

        transcripts = []

        for url in urls:
            text = load_transcript_as_text(url)

            if not text:
                return jsonify({
                    "error": f"Failed to load transcript for {url}"
                }), 400

            transcripts.append(text)

        video1, video2 = transcripts[:2]

        llm = ChatOpenAI(model="gpt-4o-mini")

        prompt = f"""
        Compare the following two videos clearly and structurally.

        VIDEO 1:
        {video1[:3000]}

        VIDEO 2:
        {video2[:3000]}

        QUESTION:
        {question}

        Provide:
        - Key Differences
        - Similarities
        - Summary
        """

        response = llm.invoke(prompt)

        return jsonify({"answer": response.content})

    except Exception as e:
        logging.error(f"[COMPARE ERROR]: {str(e)}")
        return jsonify({"error": "Comparison failed"}), 500