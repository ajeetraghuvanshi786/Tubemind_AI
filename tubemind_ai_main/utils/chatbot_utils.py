from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from repositories.transcript_repository import is_faiss_ready, mark_faiss_ready
import os

VECTOR_STORE = {}

# ------------------------- CHUNKING -------------------------
def get_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)


# ------------------------- VECTOR DB (CACHED) -------------------------
import os
from repositories.transcript_repository import mark_faiss_ready

def build_vector_db(chunks, session_id):
    path = f"faiss_store/{session_id}"
    embeddings = OpenAIEmbeddings()

    # 🔥 LOAD EXISTING INDEX
    if os.path.exists(path):
        try:
            db = FAISS.load_local(
                path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            return db.as_retriever()
        except Exception:
            pass  # fallback to rebuild

    # 🔥 CREATE NEW INDEX
    db = FAISS.from_texts(chunks, embeddings)
    db.save_local(path)

    mark_faiss_ready(session_id)

    return db.as_retriever()

# ------------------------- ANSWER -------------------------
def generate_answer(chunks, question, lang, session_id):
    retriever = build_vector_db(chunks, session_id)

    docs = retriever.invoke(question)
    context = " ".join(d.page_content for d in docs)

    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = f"""
    Answer based ONLY on the transcript.
    Language: {lang}

    CONTEXT:
    {context}

    QUESTION:
    {question}
    """

    return llm.invoke(prompt).content


# ------------------------- QUIZ -------------------------
def generate_quiz(chunks, num_q, difficulty, lang, session_id):
    retriever = build_vector_db(chunks, session_id)

    docs = retriever.invoke("quiz")
    context = " ".join(d.page_content for d in docs)

    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = f"""
    Create EXACTLY {num_q} questions.

    <quiz>
        <question id="1" type="mcq">
            Question text
            A) Option
            B) Option
            C) Option
            D) Option
        </question>

        <answer id="1">
            C
            Explanation: short explanation
        </answer>
    </quiz>

    Language: {lang}
    Difficulty: {difficulty}

    TRANSCRIPT:
    {context}
    """

    return llm.invoke(prompt).content

def generate_notes(chunks, session_id, lang="English"):
    retriever = build_vector_db(chunks, session_id)
    docs = retriever.invoke("summary notes key points")
    context = " ".join(d.page_content for d in docs)

    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = f"""
    Create structured notes from the transcript.

    Include:
    - Headings
    - Bullet points
    - Key concepts
    - Summary

    Language: {lang}

    CONTENT:
    {context}
    """

    return llm.invoke(prompt).content