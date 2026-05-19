from flask import Flask, request, jsonify, send_file
import io
import os
import requests

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
        # Forward to remove.bg API
        removebg_key = os.environ.get('REMOVEBG_API_KEY', '')
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': ('image.jpg', input_bytes, 'image/jpeg')},
            data={'size': 'auto'},
            headers={'X-Api-Key': removebg_key},
            timeout=30
        )
        if response.status_code == 200:
            return send_file(io.BytesIO(response.content), mimetype='image/png')
        return jsonify({'error': f'removebg failed: {response.status_code}'}), 500
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
