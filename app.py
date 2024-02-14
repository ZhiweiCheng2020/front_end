from flask import Flask, request, render_template
from flask_socketio import SocketIO
from data_analysis import process_data  # Make sure this is adapted to use SocketIO for updates
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Assuming the file is received as part of the form data
        file = request.files['file']
        file_path = 'path/to/save/' + file.filename
        file.save(file_path)
        
        # Process data in a separate thread to not block the main thread
        # This allows the server to respond to other requests and emit updates via SocketIO
        thread = threading.Thread(target=process_data_with_socketio, args=(file_path,))
        thread.start()

        # You might want to return a response that acknowledges the upload and processing initiation
        return 'File uploaded and processing started.', 202

def process_data_with_socketio(file_path):
    # This function wraps your original process_data function
    # and provides the socketio instance for emitting updates
    output_path = process_data(file_path, socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True)



def process_data(socketio):
    # Example data analysis steps
    analysis_steps = range(10)  # Placeholder for actual analysis steps
    for step in analysis_steps:
        # Replace this with actual analysis code
        update_message = f'Processing step {step+1}/10'
        socketio.emit('analysis_update', {'data': update_message})
        # Assuming each step takes some time
        socketio.sleep(1)


