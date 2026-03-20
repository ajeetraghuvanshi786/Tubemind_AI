from config.database import get_db

def save_chat(session_id, role, message):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO chats (session_id, role, message)
            VALUES (%s, %s, %s)
        """, (session_id, role, message))

        conn.commit()

    finally:
        cur.close()
        conn.close()


def get_chat_history(session_id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT role, message FROM chats
            WHERE session_id=%s ORDER BY id DESC LIMIT 10
        """, (session_id,))

        data = cur.fetchall()
        return data[::-1]

    finally:
        cur.close()
        conn.close()
        
def get_chat_history(session_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT role, message FROM chats
            WHERE session_id=%s ORDER BY id DESC LIMIT 10
        """, (session_id,))

        data = cur.fetchall()
        return list(reversed(data))

    finally:
        cur.close()
        conn.close()