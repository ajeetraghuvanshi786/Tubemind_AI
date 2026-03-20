import os
import yt_dlp
import tempfile
import subprocess
import logging
from utils.youtube_utils import load_transcript_as_text

# 🔥 FIX OpenMP crash
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from faster_whisper import WhisperModel
from repositories.transcript_repository import save_transcript, mark_faiss_ready


# =========================================================
# DOWNLOAD AUDIO (FORCE WAV)
# =========================================================
def download_audio(url):
    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{temp_dir}/audio.%(ext)s',
    'quiet': True,
    'noplaylist': True,

    # 🔥 ADD THIS
    "js_runtimes": ["node:C:/Program Files/nodejs/node.exe"],

    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        # After conversion → always wav
        file_path = os.path.join(temp_dir, "audio.wav")

        if not os.path.exists(file_path):
            raise Exception("Audio download failed")

        return file_path


# =========================================================
# SPLIT AUDIO (SAFE WAV CHUNKS)
# =========================================================
def split_audio(file_path):
    temp_dir = tempfile.mkdtemp()

    output_pattern = os.path.join(temp_dir, "chunk_%03d.wav")

    command = [
        "ffmpeg",
        "-i", file_path,
        "-f", "segment",
        "-segment_time", "60",
        "-ar", "16000",
        "-ac", "1",
        "-vn",
        output_pattern
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    chunks = sorted([
        os.path.join(temp_dir, f)
        for f in os.listdir(temp_dir)
        if f.endswith(".wav")
    ])

    if not chunks:
        raise Exception("Audio splitting failed")

    return chunks


# =========================================================
# TRANSCRIBE USING FASTER-WHISPER (CPU SAFE)
# =========================================================
def transcribe_audio(file_path):
    logging.info("Loading Faster-Whisper model...")

    model = WhisperModel(
        "base",
        device="cpu",         
        compute_type="int8"    
    )

    logging.info("Splitting audio...")
    chunks = split_audio(file_path)

    full_text = []

    for i, chunk in enumerate(chunks):
        logging.info(f"Processing chunk {i+1}/{len(chunks)}")

        segments, _ = model.transcribe(chunk)

        text = " ".join([seg.text for seg in segments])
        full_text.append(text)

    logging.info("Transcription completed")

    return " ".join(full_text)


# =========================================================
# MAIN PIPELINE
# =========================================================
def process_transcript_pipeline(session_id, url):
    try:
        logging.info("[PIPELINE] Trying YouTube captions (FAST)...")

        transcript = load_transcript_as_text(url)

        if transcript:
            logging.info("[PIPELINE] Using fast captions ")

            save_transcript(session_id, url, transcript)
            mark_faiss_ready(session_id)

            return transcript

        # ---------------- FALLBACK ----------------
        logging.info("[PIPELINE] Falling back to Whisper...")

        audio_path = download_audio(url)

        transcript = transcribe_audio(audio_path)

        if not transcript:
            raise Exception("Empty transcript generated")

        save_transcript(session_id, url, transcript)
        mark_faiss_ready(session_id)

        return transcript

    except Exception as e:
        logging.error(f"[PIPELINE ERROR] {str(e)}")
        raise


# =========================================================
# BACKWARD COMPATIBILITY (IMPORTANT)
# =========================================================
def process_transcript(session_id, url):
    return process_transcript_pipeline(session_id, url)