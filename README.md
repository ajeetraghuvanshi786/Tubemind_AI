# 🚀 TubeMind AI – Intelligent YouTube Learning Assistant

An end-to-end AI-powered web application that transforms any YouTube video into **interactive learning content** including transcripts, Q&A, quizzes, notes, and voice-based interaction.

---

## 📌 Overview

TubeMind AI is designed to **enhance learning efficiency** by converting video content into structured, queryable knowledge. It combines:

* ⚡ Fast transcript extraction (YouTube captions + Whisper fallback)
* 🧠 Retrieval-Augmented Generation (RAG)
* 🔊 Voice interaction (Speech-to-Text + Text-to-Speech)
* 📊 Quiz & notes generation
* 💬 Conversational AI interface

---

## ✨ Key Features

### 🎥 1. Smart Transcript Extraction

* Extracts captions instantly using `yt-dlp`
* Falls back to `Faster-Whisper` for videos without subtitles
* Optimized pipeline for speed and accuracy

---

### 💬 2. AI-Powered Q&A (RAG)

* Ask questions based on video content
* Uses FAISS vector database for semantic retrieval
* Powered by OpenAI GPT models

---

### 🧠 3. Quiz Generation

* Auto-generates MCQs from video transcript
* Supports:

  * Difficulty levels (Easy / Medium / Hard)
  * Multiple languages

---

### 📝 4. Notes Generation

* Structured notes with:

  * Headings
  * Bullet points
  * Key concepts
  * Summaries

---

### 🔊 5. Voice Assistant (Advanced UX)

* 🎤 Speech-to-text input (Web Speech API)
* 🔊 Text-to-speech responses
* Works in:

  * Floating chatbot
  * Ask page

---

### 🔄 6. Multi-Video Comparison

* Compare 2+ videos using AI
* Extract similarities and differences

---

## 🏗️ Architecture

```
User Input (URL / Voice / Text)
        ↓
Transcript Pipeline
 ├── YouTube Captions (Fast Path ⚡)
 └── Whisper Fallback (Slow Path 🐢)
        ↓
Text Chunking
        ↓
FAISS Vector Store
        ↓
RAG (OpenAI GPT)
        ↓
Response (Text + Voice)
```

---

## 🧰 Tech Stack

### 🔹 Backend

* Python (Flask)
* LangChain
* OpenAI API
* FAISS (Vector DB)
* Faster-Whisper

### 🔹 Frontend

* HTML, CSS (Glass UI)
* Vanilla JavaScript
* Web Speech API (STT + TTS)

### 🔹 Data & Storage

* MySQL (Session + Chat + Transcripts)
* Local FAISS index storage

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ajeetraghuvanshi786/tubemind-ai.git
cd tubemind-ai
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create `.env` file:

```env
OPENAI_API_KEY=your_api_key
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
```

---

### 5️⃣ Install System Dependencies

#### ✅ Node.js (Required for yt-dlp)

```bash
winget install OpenJS.NodeJS
```

#### ✅ FFmpeg (Required for audio processing)

```bash
winget install ffmpeg
```

---

### 6️⃣ Run Application

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
tubemind_ai/
│
├── app.py
├── routes/
│   ├── transcript_routes.py
│   ├── ask_routes.py
│   ├── chat_routes.py
│   └── quiz_routes.py
│
├── services/
│   ├── transcript_service.py
│   ├── chatbot_service.py
│   ├── ask_service.py
│   └── quiz_service.py
│
├── utils/
│   ├── youtube_utils.py
│   ├── chatbot_utils.py
│   └── session_utils.py
│
├── repositories/
│   ├── transcript_repository.py
│   └── chat_repository.py
│
├── templates/
├── static/
└── faiss_store/
```

---

## 🚀 Performance Optimization

* ⚡ Captions-first strategy (1–2 sec response)
* 🔄 Whisper fallback only when needed
* 🧠 FAISS caching for faster retrieval
* 🚫 Duplicate API call prevention
* 🔊 Optimized voice processing

---

## 🧪 Example Use Cases

* 📚 Students learning from lectures
* 🎓 Exam preparation (quiz + notes)
* 🎥 Content summarization
* 🧠 Knowledge extraction from long videos
* 💼 EdTech SaaS applications

---

## 🔐 Future Enhancements

* 🔄 Async processing (Celery / Redis)
* 📊 User analytics dashboard
* 🌍 Multi-language speech detection
* 🎙️ Full voice assistant mode
* ☁️ Cloud deployment (AWS / GCP)

---

## 👨‍💻 Author

**Ajeet Raghuvanshi**
Data Scientist | AI Engineer | Full Stack Developer

📧 Email: [ajeetraghuvanshi786@gmail.com](mailto:ajeetraghuvanshi786@gmail.com)

---

## ⭐ Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 💡 Final Note

TubeMind AI demonstrates a **production-ready AI system** combining:

* RAG architecture
* Real-time interaction
* Voice-enabled UX
* Scalable backend design

---

🔥 *If you found this useful, consider giving it a star!*
