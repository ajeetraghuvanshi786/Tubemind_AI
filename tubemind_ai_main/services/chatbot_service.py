from repositories.chat_repository import save_chat, get_chat_history
from langchain_openai import ChatOpenAI

def generate_chat_reply(session_id, user_msg, lang):
    save_chat(session_id, "user", user_msg)

    history = get_chat_history(session_id)

    conversation = ""
    for role, msg in history:
        conversation += f"{role.capitalize()}: {msg}\n"

    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = f"""
    You are Tubemind AI.
    Language: {lang}

    Conversation:
    {conversation}

    Reply to last message.
    """

    try:
        reply = llm.invoke(prompt).content
    except Exception:
        reply = "⚠️ AI service temporarily unavailable."

    save_chat(session_id, "assistant", reply)

    return reply