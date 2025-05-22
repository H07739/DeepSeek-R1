from flask import Flask, jsonify, request, Response, stream_with_context
from DeepSeek import sendMessage
import json

app = Flask(__name__)

@app.route('/sendMessage', methods=['POST'])
def handle_send_message():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "prompt is required"}), 400
    
    message_id = data.get('message_id', None)
    prompt = data['prompt']
    
    def generate():
        try:
            for message in sendMessage(prompt, message_id):
                yield f"data: {json.dumps(message)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)

