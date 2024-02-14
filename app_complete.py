from flask import Flask, request, render_template, Response, send_from_directory
import json
import threading
from queue import Queue
from process_data import process_data as imported_process_data
import io
from contextlib import redirect_stdout
import os

app = Flask(__name__)

progress_updates = Queue()

def capture_prints_process_data_and_return_path(file_path):
    with io.StringIO() as buf, redirect_stdout(buf):
        # Call the imported function and get the output path
        output_path = imported_process_data(file_path)
        for line in buf.getvalue().splitlines():
            progress_updates.put(json.dumps({"message": line, "complete": "100%" in line}))
        # After processing is complete, put a final message with the output path
        progress_updates.put(json.dumps({"message": "Processing complete", "complete": True, "output_path": output_path}))

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

    # You might want to save the file before processing
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Start the data processing in a background thread
    threading.Thread(target=capture_prints_process_data_and_return_path, args=(file_path,)).start()
    
    return 'File is being processed'

@app.route('/progress')
def progress():
    def generate():
        while True:
            message = progress_updates.get()  # This now blocks until a message is available
            yield f"data:{message}\n\n"
            if json.loads(message).get("complete"):
                break
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    directory = os.getcwd()  # Adjust if your output files are in a specific directory
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
