from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import time
import json
import os

app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/respond', methods=['POST'])
def respond():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')
    if not isinstance(prompt, str) or not prompt.strip():
        return jsonify({'error': 'prompt required'}), 400

    def gen(text: str):
        out = text.upper()
        words = out.split()
        for w in words:
            for ch in w:
                yield f"data: {json.dumps({'token': ch})}\n\n"
                time.sleep(0.03)
            yield f"data: {json.dumps({'token': ' '})}\n\n"
            time.sleep(0.06)
        time.sleep(0.3)
        yield "data: [DONE]\n\n"

    return Response(gen(prompt), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='127.0.0.1', port=port, debug=True, threaded=True)
