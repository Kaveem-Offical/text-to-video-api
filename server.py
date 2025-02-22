from flask import Flask, request, send_file
import os
import subprocess
import threading
import time

app = Flask(__name__)
UPLOAD_FOLDER = "videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def delete_file_after_delay(file_path, delay=3600):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route("/generate_video", methods=["POST"])
def generate_video():
    data = request.json
    title = data.get("title", "Default Title")
    description = data.get("description", "")
    id_no = data.get("id", "12345")
    image_url = data.get("image")
    
    if not image_url:
        return {"error": "Image URL is required"}, 400
    
    image_path = os.path.join(UPLOAD_FOLDER, f"{id_no}.png")
    video_path = os.path.join(UPLOAD_FOLDER, f"{id_no}.mp4")
    
    os.system(f"wget {image_url} -O {image_path}")
    
    if not os.path.exists(image_path):
        return {"error": "Failed to download image"}, 400
    
    ffmpeg_cmd = (
        f"ffmpeg -loop 1 -i {image_path} -vf \"drawtext=text='{title}':fontcolor=white:fontsize=40:x=10:y=50\" "
        f"-t 90 -c:v libx264 -pix_fmt yuv420p {video_path}"
    )
    subprocess.run(ffmpeg_cmd, shell=True)
    
    if not os.path.exists(video_path):
        return {"error": "Video generation failed"}, 500
    
    threading.Thread(target=delete_file_after_delay, args=(video_path,)).start()
    return send_file(video_path, mimetype="video/mp4", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
