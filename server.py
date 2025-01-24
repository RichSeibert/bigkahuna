from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging
from datetime import datetime
import subprocess

app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])
workers = {}
with open("token.txt") as file:
    token = file.read().split("\n")[0]

# Set up logging
year_month_date = datetime.now().strftime("%Y_%m_%d")
logging.basicConfig(
    level=logging.INFO,
    filename = 'logs/bigkahuna' + year_month_date + '.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logging.info("\n-------------------------------------------------\n")

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
        start_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        workers[worker_id] = {"start_time": start_time}
        logging.info(f"Registered worker {worker_id} at {start_time}")
        return jsonify({"status": "Worker registered"}), 200
    return jsonify({"status": "Worker ID required"}), 400

@app.route('/task-completed', methods=['POST'])
@limiter.limit("10 per minute")
def task_completed():
    data = request.json
    worker_id = data.get("worker_id")
    if worker_id not in workers:
        return jsonify({"status": "Unknown worker"}), 400
    worker_info = workers.pop(worker_id)
    try:
        # TODO this only works with one pod max. The script will just
        # terminate the least recently started pod (I'm assuming).
        # The worker id I use should be the runpod id instead of a UUID
        subprocess.call("./terminate_runpod_instance.sh")
        logging.info(f"Terminated worker {worker_id} at {worker_info['start_time']}")
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
