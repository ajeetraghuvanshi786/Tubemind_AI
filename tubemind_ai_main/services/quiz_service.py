from utils.chatbot_utils import get_chunks, generate_quiz
from bs4 import BeautifulSoup

def parse_quiz_output(raw):
    soup = BeautifulSoup(raw, "html.parser")
    questions = [q.get_text("\n").strip() for q in soup.find_all("question")]
    answers = [a.get_text("\n").strip() for a in soup.find_all("answer")]
    return questions, answers


def process_quiz(transcript, number, difficulty, lang, session_id):
    chunks = get_chunks(transcript)
    raw = generate_quiz(chunks, number, difficulty, lang, session_id)
    return parse_quiz_output(raw)