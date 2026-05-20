from flask import Flask, request, jsonify, send_file
import io
import os
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'ok',
        'service': 'SpotIt BG Removal'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/remove-bg', methods=['POST'])
def remove_bg():

    try:
        # API KEY CHECK
        api_key = request.headers.get('X-API-Key', '')

        expected_key = os.environ.get(
            'SPOTIT_API_KEY',
            'spotit-rembg-secret'
        )

        if api_key != expected_key:
            return jsonify({
                'error': 'Unauthorized'
            }), 401

        # IMAGE CHECK
        if 'image_file' not in request.files:
            return jsonify({
                'error': 'No image_file uploaded'
            }), 400

        uploaded_file = request.files['image_file']

        input_bytes = uploaded_file.read()

        if not input_bytes:
            return jsonify({
                'error': 'Empty image'
            }), 400

        # REMOVE.BG API KEY
        removebg_key = os.environ.get(
            'REMOVEBG_API_KEY',
            ''
        )

        if not removebg_key:
            return jsonify({
                'error': 'REMOVEBG_API_KEY missing'
            }), 500

        # CALL REMOVE.BG
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={
                'image_file': (
                    'image.jpg',
                    input_bytes,
                    'image/jpeg'
                )
            },
            data={
                'size': 'auto'
            },
            headers={
                'X-Api-Key': removebg_key
            },
            timeout=60
        )

        print('REMOVE.BG STATUS:', response.status_code)
        print('REMOVE.BG RESPONSE:', response.text)

        # SUCCESS
        if response.status_code == 200:

            return send_file(
                io.BytesIO(response.content),
                mimetype='image/png'
            )

        # FAILED
        return jsonify({
            'error': f'remove.bg failed',
            'status': response.status_code,
            'body': response.text
        }), 500

    except Exception as e:

        print('SERVER ERROR:', str(e))

        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
