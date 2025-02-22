from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "FFmpeg API is running!"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
