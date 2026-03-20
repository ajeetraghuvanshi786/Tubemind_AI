import re
from tempfile import tempdir
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
import yt_dlp
import requests


# =====================================================
# 🔹 Extract Video ID
# =====================================================
def extract_video_id(url: str):
    pattern = r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


# =====================================================
# 🔹 MAIN TRANSCRIPT FETCH
# =====================================================
def fetch_transcript(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript

    except (TranscriptsDisabled, NoTranscriptFound):
        return fetch_using_ytdlp(video_id)

    except Exception as e:
        print("[ERROR API]:", e)
        return fetch_using_ytdlp(video_id)


# =====================================================
# 🔥 FIXED YT-DLP FALLBACK (NO URL BUG)
# =====================================================
def fetch_using_ytdlp(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "quiet": True,
            "skip_download": True,

            # 🔥 FIX 1: FORCE JS RUNTIME
            "js_runtimes": ["node:C:/Program Files/nodejs/node.exe"],

            # 🔥 FIX 2: FORCE CAPTIONS
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "json3",

            "extractor_args": {
                "youtube": {
                    "player_client": ["web"]
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get("automatic_captions") or info.get("subtitles")

            if not subtitles:
                print("[ERROR] No subtitles found")
                return None

            for lang in subtitles:
                for entry in subtitles[lang]:

                    if "url" in entry:
                        subtitle_url = entry["url"]

                        response = requests.get(subtitle_url)

                        if response.status_code != 200:
                            continue

                        data = response.json()

                        text = ""
                        for event in data.get("events", []):
                            if "segs" in event:
                                for seg in event["segs"]:
                                    text += seg.get("utf8", "") + " "

                        if text.strip():
                            return [{"text": text.strip()}]

        return None

    except Exception as e:
        print("[yt-dlp ERROR]:", e)
        return None

# =====================================================
# 🔹 FINAL TEXT OUTPUT
# =====================================================
def load_transcript_as_text(url: str):
    video_id = extract_video_id(url)

    if not video_id:
        print("[ERROR] Invalid URL")
        return None

    transcript = fetch_transcript(video_id)

    if not transcript:
        print("[ERROR] No transcript available")
        return None

    full_text = " ".join(entry["text"] for entry in transcript)

    print("[DEBUG] Transcript sample:", full_text[:300])

    return full_text
