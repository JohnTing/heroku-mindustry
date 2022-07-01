#!/usr/bin/env python

from typing import Dict
from gevent import monkey
#gevent
monkey.patch_all()

import subprocess
import threading
import time
from flask import Flask, render_template, request
import os
import psutil

from flask_socketio import SocketIO, emit, send

maxLogLine = 1000
returnLogLine = 100

async_mode = 'gevent'
# async_mode = 'threading'
# async_mode = 'eventlet'
# async_mode = 'gevent'

port = int(os.environ.get('PORT', 17995))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!mindustry'
socketio = SocketIO(app, async_mode=async_mode, logger=True)


mindustryProcess = subprocess.Popen("java -jar server-release.jar", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
mindustryProcess.stdin.write("host\n")
mindustryProcess.stdin.flush()

token = os.environ.get("token")
if token:
    subprocess.Popen([f"./localtonet authtoken {token}"], shell=True)
else:
    subprocess.Popen(["./localtonet udptcp 6567"], shell=True)
logs = []

logFromStart = []

thread = None
thread_lock = threading.Lock()

@socketio.on('command')
def commandEvent(command: Dict):
    if 'text' in command:

        mindustryProcess.stdin.write(command["text"] + "\n")
        mindustryProcess.stdin.flush()
        emit('logEvent', {'text': f'{request.remote_addr}:${command["text"]}\n'})

@socketio.on('connect')
def test_connect(auth):
    
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

    emit('logEvent', {'text': f'{request.remote_addr} is connected.\n', 'count': 0})

def background_thread():
    line = 'start:\n'
    while line:
        line = mindustryProcess.stdout.readline()
        logFromStart.append(line)
        if len(logFromStart) > maxLogLine:
            logFromStart.pop()
        socketio.emit('logEvent', {'text': line})
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
    psutilText = ''
    """
    psutilData = [
        psutil.cpu_percent(interval=1, percpu=True), 
        psutil.virtual_memory(), 
        psutil.swap_memory()
    ]
    psutilText = '\n'.join([str(i) for i in psutilData])
    

    logText = 'logText\n'
    with open('./config/logs/log-0.txt') as f:
        logText = f.readlines()
    logText =  ''.join(logText[-10:])
    """
    logText =  ''.join(logFromStart[-returnLogLine:])
    

    # return "<p>Hello, World!</p>" + "<br/>".join([str(i) for i in datastrs])
    return render_template('index.html', async_mode=socketio.async_mode, logText=logText, psutilText=psutilText)

@app.route("/i")
def write():
    myinput = request.args.get("input")
    print("myinput = " + myinput)
    if myinput:
        mindustryProcess.stdin.write(myinput + "\n")
        mindustryProcess.stdin.flush()
    out = "<br>".join(logs)
    return out 

@app.route("/ping")
def ping():
    return 'pong'

if __name__ == "__main__":
    socketio.run(app, port=port)


