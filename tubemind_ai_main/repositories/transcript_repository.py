from config.database import get_db
import re

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def save_transcript(session_id, url, text):
    conn = get_db()
    cur = conn.cursor()

    video_id = extract_video_id(url)

    try:
        cur.execute("""
            INSERT INTO transcripts (session_id, source_url, transcript, video_id, faiss_ready)
            VALUES (%s, %s, %s, %s, FALSE)
        """, (session_id, url, text, video_id))

        conn.commit()

    finally:
        cur.close()
        conn.close()


def get_latest_transcript(session_id, video_id=None):
    conn = get_db()
    cur = conn.cursor()

    try:
        if video_id:
            cur.execute("""
            SELECT transcript FROM transcripts
            WHERE video_id=%s ORDER BY id DESC LIMIT 1
            """, (video_id,))
    
        else:
            cur.execute("""
            SELECT transcript FROM transcripts
            WHERE session_id=%s ORDER BY id DESC LIMIT 1
            """, (session_id,))

        result = cur.fetchone()
        return result[0] if result else None

    finally:
        cur.close()
        conn.close()
        
def mark_faiss_ready(session_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE transcripts 
            SET faiss_ready = TRUE
            WHERE session_id=%s
        """, (session_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def is_faiss_ready(session_id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT faiss_ready FROM transcripts
            WHERE session_id=%s ORDER BY id DESC LIMIT 1
        """, (session_id,))
        result = cur.fetchone()
        return result[0] if result else False
    finally:
        cur.close()
        conn.close()