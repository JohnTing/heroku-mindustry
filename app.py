#!/usr/bin/env python
import subprocess
from flask import Flask
import os


subprocess.run(["localtonet udptcp 6567"])
subprocess.run(["echo host | java -jar mindustry-server/server.jar"])

port = int(os.environ.get('PORT', 17995))

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)


