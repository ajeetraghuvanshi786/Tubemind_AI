from flask import Flask, request, session
from datetime import timedelta
import logging
import time
import os
from logging.handlers import RotatingFileHandler

# ---------------- INIT ----------------
app = Flask(__name__)
app.secret_key = "super_secret_key"

# ---------------- SESSION ----------------
app.permanent_session_lifetime = timedelta(days=1)

@app.before_request
def make_session_permanent():
    session.permanent = True

# ---------------- LOGGING ----------------
if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

@app.before_request
def log_request():
    request.start_time = time.time()
    logger.info(f"Incoming {request.method} {request.path}")

@app.after_request
def log_response(response):
    duration = time.time() - request.start_time
    logger.info(f"{request.method} {request.path} -> {response.status_code} ({duration:.2f}s)")
    return response

# ---------------- ERROR HANDLER ----------------
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Error: {str(e)}")
    return {"error": "Internal Server Error"}, 500

# ---------------- FAVICON FIX ----------------
@app.route('/favicon.ico')
def favicon():
    return '', 204

# ---------------- ROUTES ----------------
from routes.home_routes import home_bp
from routes.transcript_routes import transcript_bp
from routes.chat_routes import chat_bp
from routes.ask_routes import ask_bp
from routes.quiz_routes import quiz_bp

app.register_blueprint(home_bp)
app.register_blueprint(transcript_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(ask_bp)
app.register_blueprint(quiz_bp)

# ---------------- HEALTH ----------------
@app.route("/health")
def health():
    return {"status": "ok"}

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    app.run(debug=False)