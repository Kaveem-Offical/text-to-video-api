import os
import time
from flask import Flask, request, jsonify, send_file
import subprocess
import threading

app = Flask(__name__)

VIDEO_FOLDER = "videos"
if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)

# 🛠 Function to Delete Video After 1 Hour
def delete_video_after_1_hour(video_path):
    time.sleep(3600)  # 1 hour = 3600 seconds
    if os.path.exists(video_path):
        os.remove(video_path)

@app.route("/")
def home():
    return "FFmpeg API is running!"

@app.route("/generate", methods=["POST"])
def generate_video():
    data = request.json
    title = data.get("title", "Default Title")
    description = data.get("description", "Default Description")
    video_id = data.get("id", "00000")

    video_path = f"{VIDEO_FOLDER}/{video_id}.mp4"

    # 🎬 Generate Video with FFmpeg (No Image)
    ffmpeg_command = [
        "ffmpeg",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=90",  # Black background, 90 sec
        "-vf", f"drawtext=text='{title}':fontcolor=white:fontsize=40:x=10:y=50",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        video_path
    ]

    try:
        result = subprocess.run(ffmpeg_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        print("FFmpeg Output:", result.stdout)
        print("FFmpeg Error:", result.stderr)

        if result.returncode != 0:
            return jsonify({"error": "FFmpeg failed", "details": result.stderr}), 500

        # 🗑️ Auto-delete video after 1 hour
        threading.Thread(target=delete_video_after_1_hour, args=(video_path,)).start()

        return jsonify({"video_url": f"/download/{video_id}.mp4"}), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route("/download/<filename>")
def download_video(filename):
    file_path = os.path.join(VIDEO_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
