from flask import Flask, render_template, request
import asyncio
import websockets

app = Flask(__name__)
app.config['TESTING'] = True

global nodes

@app.route("/")
def index():
    global nodes
    return render_template("index.html", posts=nodes)

async def handler(websocket):
    global nodes
    while True:
        try:
            message = await websocket.recv()
            layer, layerPort, node, versions = message.split('\n')
            layerPort = int(layerPort)
            node = int(node)
            nodes[layerPort + node].layer = layer
            nodes[layerPort + node].node = node
            nodes[layerPort + node].versions = versions
        except websockets.ConnectionClosedOK:
            break
        print("SOCKET CONNECTION CLOSED")

async def main():
    global nodes
    nodes = []
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())