from flask import Flask, render_template
from flask_socketio import SocketIO
import pyaudio
import sys

app = Flask(__name__)
# Enable SocketIO for real-time WebSocket communication
# cors_allowed_origins="*" allows your zrok URL to connect seamlessly
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Audio Settings ---
# We force the same configuration as the browser's raw audio output.
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 16000  # 16kHz sample rate (same as we set in JavaScript)
CHUNK = 4096  # Chunk size

print("Initializing PyAudio...")
try:
    audio = pyaudio.PyAudio()
    
    # Open PyAudio Stream for Output
    audio_stream = audio.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              output=True,
                              frames_per_buffer=CHUNK)
    print("Audio stream successfully opened on Default Speakers.")
except Exception as e:
    print(f"Failed to open PyAudio stream. Please check if speakers are connected. Error: {e}")
    sys.exit(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listener')
def listener():
    return render_template('receiver.html')

@socketio.on('audio_stream')
def handle_audio_stream(audio_bytes):
    # Broadcast the audio to all connected clients (the new website)
    socketio.emit('audio_broadcast', audio_bytes, broadcast=True, include_self=False)
    
    # PyAudio directly accepts the raw binary data (Float32Array) from the browser
    # and instantly pushes it to the server's local speakers.
    if audio_stream.is_active():
        try:
            audio_stream.write(audio_bytes)
        except Exception as e:
            # Skip if there's a tiny buffer underrun/issue, keeps it real-time
            print(f"Audio buffer skip: {e}")

if __name__ == '__main__':
    print("=====================================")
    print("Starting Live Intercom Server...")
    print("Listening on http://0.0.0.0:5000")
    print("You can now connect to this port via zrok.")
    print("=====================================")
    socketio.run(app, host='0.0.0.0', port=5600)
