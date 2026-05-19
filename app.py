from flask import Flask, request, jsonify, send_file
import io
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'SpotIt BG Removal'})

@app.route('/health', methods=['GET'])
def health2():
    return jsonify({'status': 'ok'})

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    api_key = request.headers.get('X-API-Key', '')
    expected_key = os.environ.get('SPOTIT_API_KEY', 'spotit-rembg-secret')
    if api_key != expected_key:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'image_file' not in request.files:
        return jsonify({'error': 'No image_file'}), 400

    try:
        input_bytes = request.files['image_file'].read()

        # Import inside function — loads only when called, not on startup
        from rembg import remove, new_session
        import numpy as np
        from PIL import Image

        # Use u2netp — smallest useful model, only 4MB
        session = new_session('u2netp')
        output_bytes = remove(input_bytes, session=session)

        return send_file(
            io.BytesIO(output_bytes),
            mimetype='image/png'
        )

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
