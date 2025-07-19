from flask import Flask, request, jsonify
from threading import Thread
import json


app = Flask(__name__)

def your_meeting_assistant(data): 
    # Has to be implemented
    pass

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    print(f"\n Received: {json.dumps(data, indent=2)}")
    new_data = your_meeting_assistant(data)
    print(f"\n\n\n Sending:\n {json.dumps(new_data, indent=2)}")
    return jsonify(new_data)

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    Thread(target=run_flask).start()