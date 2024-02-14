from flask import Flask, request, render_template, Response
import json
import threading
from queue import Queue
from process_data import process_data as imported_process_data
import io
from contextlib import redirect_stdout

app = Flask(__name__)

progress_updates = Queue()

def capture_prints_and_process_data(file_path):
    with io.StringIO() as buf, redirect_stdout(buf):
        imported_process_data(file_path)  # Call the imported function
        for line in buf.getvalue().splitlines():
            progress_updates.put(json.dumps({"message": line, "complete": "100%" in line}))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Start the data processing in a background thread
    threading.Thread(target=capture_prints_and_process_data, args=(file.filename,)).start()
    
    return 'File is being processed'

@app.route('/progress')
def progress():
    def generate():
        while not progress_updates.empty():
            message = progress_updates.get()
            yield f"data:{message}\n\n"
            if json.loads(message).get("complete"):
                break
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
