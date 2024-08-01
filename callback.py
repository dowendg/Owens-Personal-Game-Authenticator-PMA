from flask import Flask, request
import requests
import urllib.parse

app = Flask(__name__)

# Define the base URL where the callback should be forwarded
BASE_URL = 'http://localhost:18275/'

@app.route('/auth/callback', methods=['GET'])
def handle_callback():
    """Handle the callback from the authentication provider."""
    code = request.args.get('code')
    if code:
        # Forward the request to the base URL with the 'code' parameter
        forward_url = f"{BASE_URL}?{urllib.parse.urlencode({'code': code})}"
        print(f"Forwarding callback to: {forward_url}")
        try:
            response = requests.get(forward_url)
            if response.status_code == 200:
                return 'Callback successfully forwarded!', 200
            else:
                return 'Failed to forward callback.', 500
        except requests.RequestException as e:
            print(f"Error forwarding callback: {e}")
            return 'Error forwarding callback.', 500
    else:
        return 'No code parameter provided.', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # Ensure callback server runs on port 5001
