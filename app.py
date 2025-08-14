from flask import Flask, render_template, request, redirect, url_for
import os
import yt_dlp
import whisper

app = Flask(__name__)
UPLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper model once
model = whisper.load_model("small")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form["video_url"]

        # Download audio from video
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(UPLOAD_FOLDER, "audio.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }],
        }

        audio_path = None
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            audio_path = os.path.join(UPLOAD_FOLDER, "audio.mp3")

        # Transcribe audio
        result = model.transcribe(audio_path, language="en")
        transcription = result["text"]

        return redirect(url_for("preview", text=transcription))

    return render_template("index.html")

@app.route("/preview")
def preview():
    text = request.args.get("text", "")
    return render_template("preview.html", transcription=text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
