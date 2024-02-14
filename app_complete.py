from flask import Flask, request, render_template, Response
import time
import json
import threading
from queue import Queue

app = Flask(__name__)

# This queue will hold progress messages
progress_updates = Queue()

def process_data(file_path):
    # Placeholder for your data analysis process
    # Simulate progress with sleep
    for i in range(1, 101):
        progress_updates.put(json.dumps({"message": f"Processing {i}%", "complete": i == 100}))
        time.sleep(0.1)  # Simulate work being done

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
    
    # Save the file to a secure location before processing
    # For simplicity, we're skipping saving and directly processing
    # You should use something like `file.save(os.path.join('/path/to/save', filename))`

    # Start the data processing in a background thread to not block the Flask main thread
    threading.Thread(target=process_data, args=(file.filename,)).start()
    
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
