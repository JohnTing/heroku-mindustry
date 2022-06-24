#!/usr/bin/env python
import subprocess
from flask import Flask
import os

import psutil

token = os.environ.get("token")


subprocess.Popen(["echo host | java -jar server-release.jar"], shell=True)
subprocess.Popen(["./localtonet authtoken ${token}"], shell=True)
subprocess.Popen(["./localtonet udptcp 6567"], shell=True)

port = int(os.environ.get('PORT', 17995))

app = Flask(__name__)


@app.route("/")
def hello_world():

    datastrs = [
        psutil.cpu_percent(interval=1, percpu=True), 
        psutil.virtual_memory(), 
        psutil.swap_memory()
    ]

    return "<p>Hello, World!</p>" + "<br/>".join([str(i) for i in datastrs])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)


