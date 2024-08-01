from flask import Flask, jsonify, request
import subprocess
import threading
import queue

app = Flask(__name__)

# Create a queue to manage incoming requests
auth_queue = queue.Queue()
processing_lock = threading.Lock()

def run_mc_auth():
    """Run the mc-auth.py script."""
    try:
        result = subprocess.run(
            ["python3", "mc-auth.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"

def process_queue():
    """Process requests from the queue."""
    while True:
        request_data = auth_queue.get()
        if request_data is None:
            break

        with processing_lock:
            output = run_mc_auth()
            request_data['response'].set_result(output)
        auth_queue.task_done()

# Start the queue processing thread
threading.Thread(target=process_queue, daemon=True).start()

@app.route('/auth/minecraft', methods=['POST'])
def authenticate():
    """Endpoint to start the authentication process."""
    response_future = threading.local()
    response = threading.Event()
    response_future.response = response

    # Add request to the queue
    auth_queue.put({"response": response_future})

    # Wait for the response
    response.wait()

    return jsonify({"output": response_future.response.result()}), 202

if __name__ == '__main__':
    app.run(port=5000)
