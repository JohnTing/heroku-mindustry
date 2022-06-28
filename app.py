#!/usr/bin/env python

from gevent import monkey
#gevent
monkey.patch_all()

from socket import SocketIO
import subprocess
import threading
import time
from flask import Flask, render_template, request, send_file
import os
import psutil

from flask_socketio import SocketIO, emit, send



async_mode = 'gevent'
# async_mode = 'threading'
# async_mode = 'eventlet'
# async_mode = 'gevent'


port = int(os.environ.get('PORT', 17995))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, logger=True)


mindustryProcess = subprocess.Popen("java -jar server-release.jar", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
mindustryProcess.stdin.write("host\n")
mindustryProcess.stdin.flush()

token = os.environ.get("token")
if token:
    subprocess.Popen(["./localtonet authtoken ${token}"], shell=True)
    subprocess.Popen(["./localtonet udptcp 6567"], shell=True)
logs = []

thread = None
thread_lock = threading.Lock()

@socketio.on('connect')
def test_connect(auth):
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('logEvent', {'data': 'Connected', 'count': 0})



def background_thread():
    line = 'start:\n'
    while line:
        line = mindustryProcess.stdout.readline()
        socketio.emit('logEvent', {'data': line})
        print(line)

def readLog():
    line = mindustryProcess.stdout.readline()
    logs.append(line)
    while line:
        line = mindustryProcess.stdout.readline()
        logs.append(line)
        print(line)
    print("line end")

# readLogThread = threading.Thread(target = readLog)
# readLogThread.start()

@app.route("/")
def hello_world():
    datastrs = [
        psutil.cpu_percent(interval=1, percpu=True), 
        psutil.virtual_memory(), 
        psutil.swap_memory()
    ]
    # return "<p>Hello, World!</p>" + "<br/>".join([str(i) for i in datastrs])
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/i")
def write():
    myinput = request.args.get("input")
    print("myinput = " + myinput)
    if myinput:
        mindustryProcess.stdin.write(myinput + "\n")
        mindustryProcess.stdin.flush()
    out = "<br>".join(logs)
    
    return out 

if __name__ == "__main__":
    socketio.run(app, port=port)


