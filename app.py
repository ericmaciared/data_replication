from flask import Flask, render_template
from flask_socketio import SocketIO
from ports import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

versions = {}
# Init version structure
for i in range(3):
    for j in range(nodes_per_layer(i+1)):
        versions[f'{id_for_layer(i+1)}{j+1}'] = str([0]*10)

@socketio.on('version')
def on_version(sid, version):
    versions[sid] = version
    print(versions)

@app.route('/')
def dashboard():
    return render_template('index.html', versions=versions)

if __name__ == '__main__':
    socketio.run(app, debug=True)