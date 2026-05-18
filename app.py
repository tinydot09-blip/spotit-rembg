"""
SpotIt Background Removal Server
Deploy this on Render.com free tier — zero cost.
Endpoint: POST /remove-bg  (multipart/form-data, field: "image_file")
Returns:  PNG bytes with transparent background
"""

from flask import Flask, request, jsonify, send_file
from rembg import remove
from PIL import Image
import io
import os

app = Flask(__name__)

# ── Health check — Render.com needs this to know the server is alive ──────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'SpotIt BG Removal'})

@app.route('/health', methods=['GET'])
def health2():
    return jsonify({'status': 'ok'})

# ── Main endpoint — called from Flutter app ───────────────────────────────────
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    # 1 — check API key (simple secret to prevent abuse)
    api_key = request.headers.get('X-API-Key', '')
    expected_key = os.environ.get('SPOTIT_API_KEY', 'spotit-rembg-secret')
    if api_key != expected_key:
        return jsonify({'error': 'Unauthorized'}), 401

    # 2 — get image from request
    if 'image_file' not in request.files:
        return jsonify({'error': 'No image_file in request'}), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # 3 — read image bytes
        input_bytes = file.read()

        # 4 — remove background using rembg (U2Net model by default)
        # For better quality use model='birefnet-general' but needs more RAM
        output_bytes = remove(
            input_bytes,
            # Uncomment below for better quality (needs 2GB+ RAM server):
            # model_name='birefnet-general',
        )

        # 5 — return PNG with transparent background
        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png',
            as_attachment=False,
            download_name='removed.png'
        )

    except Exception as e:
        print(f'BG removal error: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
