from rembg import remove
from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "service": "SPOTIT FREE BG REMOVAL",
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:

        # API SECURITY
        api_key = request.headers.get("X-API-Key", "")
        expected_key = os.environ.get(
            "SPOTIT_API_KEY",
            "spotit-rembg-secret",
        )

        if api_key != expected_key:
            return jsonify({
                "error": "Unauthorized"
            }), 401

        # FILE CHECK
        if "image_file" not in request.files:
            return jsonify({
                "error": "No image_file uploaded"
            }), 400

        file = request.files["image_file"]

        input_bytes = file.read()

        if not input_bytes:
            return jsonify({
                "error": "Empty image"
            }), 400

        print("Starting FREE rembg process...")

        # REMOVE BG
        output_bytes = remove(input_bytes)

        print("Background removed successfully")

        return send_file(
            io.BytesIO(output_bytes),
            mimetype="image/png"
        )

    except Exception as e:
        print(f"REMOVE BG ERROR: {e}")

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
    )
