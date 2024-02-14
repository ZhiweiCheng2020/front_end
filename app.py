class ProgressReporter:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def report(self, message):
        for callback in self.subscribers:
            callback(message)


def process_data(data, progress_reporter=None):
    # Example processing step
    for step in range(10):
        # Process step...
        if progress_reporter:
            progress_reporter.report(f"Processing step {step}/10")



from flask import Flask, Response, render_template
import threading
import queue

app = Flask(__name__)
progress_reporter = ProgressReporter()
messages = queue.Queue()

def message_handler(message):
    messages.put(message)

progress_reporter.subscribe(message_handler)

@app.route('/progress')
def progress():
    def generate():
        while True:
            message = messages.get()  # Blocking until a message is available
            yield f"data:{message}\n\n"
    return Response(generate(), mimetype='text/event-stream')
