from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "service": "SpotIt Free REMBG"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    api_key = request.headers.get("X-API-Key", "")
    expected_key = os.environ.get("SPOTIT_API_KEY", "spotit-rembg-secret")

    if api_key != expected_key:
        return jsonify({"error": "Unauthorized"}), 401

    if "image_file" not in request.files:
        return jsonify({"error": "No image_file uploaded"}), 400

    try:
        file = request.files["image_file"]
        input_image = Image.open(file.stream).convert("RGBA")

        output_image = remove(input_image)

        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return send_file(output_buffer, mimetype="image/png")

    except Exception as e:
        print("REMBG ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
