import os
import yt_dlp
import ffmpeg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # ensures .env is loaded BEFORE key is used


# ---------------------- DOWNLOAD VIDEO ----------------------
def download_video(url, out_path="storage/video.mp4"):
    os.makedirs("storage", exist_ok=True)

    ydl_opts = {
        "format": "mp4/bestaudio/best",
        "outtmpl": out_path,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return out_path


# ---------------------- EXTRACT AUDIO ----------------------
def extract_audio(video_path, audio_path="storage/audio.wav"):
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar="16000")
        .overwrite_output()
        .run(quiet=True)
    )
    return audio_path


# ---------------------- TRANSCRIBE USING OPENAI (Lazy Initialization) ----------------------
def transcribe_audio(audio_path):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise Exception("OPENAI_API_KEY is missing or not loaded")

    # Initialize OpenAI client *here*, not globally
    client = OpenAI(api_key=api_key)

    audio_file = open(audio_path, "rb")

    transcript = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=audio_file
    )

    return transcript.text


# ---------------------- FULL PIPELINE ----------------------
def get_transcript_from_any_url(url):
    video_file = download_video(url)
    audio_file = extract_audio(video_file)
    text = transcribe_audio(audio_file)
    return text
