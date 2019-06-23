import json
from flask import Flask
from flask_cors import CORS
from mock import hdfs
app = Flask(__name__)
CORS(app)

@app.route("/")
def helloworld():
    return "hello world"

@app.route("/api/getfuncfeature")
def get_func_feature():
    return json.dumps(hdfs.func_feature)

@app.route("/api/gettimeline")
def get_time_line():
    return json.dumps(hdfs.time_line)

@app.route("/api/getcalltree")
def get_call_tree():
    return json.dumps(hdfs.call_tree)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
