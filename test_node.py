import socketio

# Create socket io client instance
sio = socketio.Client()
version = ('A1', [1,2,3,4,5,6,7,8,9,10])

# Define event handlers
@sio.on('version')
def on_version():
    print(f'connection established')

def main():
    sio.connect('http://localhost:5000')
    sio.emit('version', version)
    sio.sleep(10)
    sio.disconnect()

if __name__ == '__main__':
    main()