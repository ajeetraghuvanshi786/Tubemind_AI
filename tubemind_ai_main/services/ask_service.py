import logging
from utils.chatbot_utils import build_vector_db, get_chunks
from repositories.transcript_repository import get_latest_transcript
from langchain_openai import ChatOpenAI


def ask_question(session_id, question):

    try:
        
        print("DEBUG SESSION:", session_id)
        
        transcript = get_latest_transcript(session_id)
        
        print("DEBUG TRANSCRIPT:", "FOUND" if transcript else "NOT FOUND")

        if not transcript:
            return "⚠️ Please generate transcript first."

        chunks = get_chunks(transcript)

        retriever = build_vector_db(chunks, session_id)

        docs = retriever.invoke(question)

        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
        Answer clearly based on context:

        {context}

        Question: {question}
        """

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        try:
            answer = llm.invoke(prompt).content
        except Exception:
            answer = "⚠️ AI service temporarily unavailable."

        return answer

    except Exception as e:
        logging.error(f"Ask Service Error: {str(e)}")
        return "Error processing question."
    
def stream_answer(context, question):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True
    )

    prompt = f"""
    Answer clearly based on context:

    {context}

    Question: {question}
    """

    stream = llm.stream(prompt)

    for chunk in stream:
        yield chunk.content
        
def ask_question_stream(session_id, question):

    transcript = get_latest_transcript(session_id)
    if not transcript:
        yield "⚠️ No transcript found"
        return

    chunks = get_chunks(transcript)
    retriever = build_vector_db(chunks, session_id)

    docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in docs])

    yield from stream_answer(context, question)
    
    