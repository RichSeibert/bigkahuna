from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging
from datetime import datetime
import subprocess


# Set up logging
year_month_date = datetime.now().strftime("%Y_%m_%d")
logging.basicConfig(
    level=logging.INFO,
    filename = 'logs/bigkahuna' + year_month_date + '.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logging.info("\n-------------------------------------------------\n")

# WARNING - This will not working multiple gunicorn instances. You cannot use global variables like this
workers = {}
with open("token.txt") as file:
    token = file.read().split("\n")[0]

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# TODO each job/process that runs on runpod should use a client lib to send a
# request to this server telling it when it started, and when it finished.
# Currently only rooporter has the client code

# TODO the client should not be sending a uuid to the server. The server
# should make a uuid, record it here, and send it back to the client

# TODO scheduler doesn't seem to work. I want to use this instead of
# cron jobs. Check "scheduler" branch for last attempt

def run_runpod_command(command, run_attempt=1):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        logging.info(f"Ran command '{command}' at {current_time}")
        if result.returncode:
            logging.error(f"Failed to run '{command}'")
            logging.error(f"stdout='{result.stdout.strip()}', stderr='{result.stderr.strip()}'")
    except Exception as e:
        logging.error(f"Failed to run command '{command}': {e}")
        return 1

# Middleware to check token
@app.before_request
def verify_token():
    request_token = request.headers.get("Authorization")
    if not request_token or request_token != token:
        return jsonify({"status": "Unauthorized"}), 401

@app.route('/register-worker', methods=['POST'])
@limiter.limit("10 per minute")
def register_worker():
    data = request.json
    worker_id = data.get("worker_id")
    if worker_id:
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        workers[worker_id] = {"start_time": current_time}
        logging.info(f"Registered worker {worker_id} at {current_time}")
        return jsonify({"status": "Worker registered"}), 200
    return jsonify({"status": "Worker ID required"}), 400

@app.route('/task-completed', methods=['POST'])
@limiter.limit("10 per minute")
def task_completed():
    data = request.json
    worker_id = data.get("worker_id")
    if worker_id not in workers:
        return jsonify({"status": "Unknown worker"}), 400
    try:
        # TODO this only works with one pod max. The script will just
        # terminate the least recently started pod (I'm assuming).
        # The worker id I use should be the runpod id instead of a UUID
        result = run_runpod_command("./terminate_runpod_instance.sh")
        if not result:
            worker_info = workers.pop(worker_id)
            current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            logging.info(f"Terminated worker {worker_id} at {current_time}")
    except Exception as e:
        logging.info(f"Subprocess failed for terminating instance: {e}")
    return jsonify({"status": "Task completed"}), 200

@app.route('/status', methods=['GET'])
@limiter.limit("5 per minute")
def get_status():
    return jsonify(workers)

@app.route('/clear-workers', methods=['POST'])
@limiter.limit("5 per minute")
def clear_workers():
    logging.info(f"Clearing workers - {workers}")
    workers.clear()
    return jsonify({"status": "Cleared workers"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
