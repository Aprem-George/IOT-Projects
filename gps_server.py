from flask import Flask
import subprocess
import json

app = Flask(__name__)

@app.route('/get_gps', methods=['GET'])
def get_gps():
    try:
        # No --provider or --request
        result = subprocess.check_output(["termux-location"], stderr=subprocess.STDOUT)
        location = json.loads(result)
        return location, 200
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}:\n{e.output.decode()}", 500
    except Exception as e:
        return f"General error: {str(e)}", 500

@app.route('/')
def index():
    return 'GPS Server running. Use /get_gps to fetch location.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
