from flask import Flask, request
from word_clip_maker import word_clip_maker
import os
import traceback

app = Flask(__name__)

@app.route('/',  methods=['GET'])
def hello_world():
    return 'Word clip maker is live :)'

@app.route('/', methods=['POST'])
def kickoff_word_clip_maker():
    data = request.get_json()
    try:
        return str(word_clip_maker(**data))
    except Exception as e:
        tb = traceback.format_exc()
        raise e

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
