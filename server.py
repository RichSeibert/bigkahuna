from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import logging

app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])
workers = {}
with open("token.txt") as file:
    token = file.read() # Replace with your actual secret token

# Set up logging
log_level = getattr(logging, args.log.upper(), logging.INFO)
year_month_date = datetime.now().strftime("%Y_%m_%d")
logging.basicConfig(
    level=log_level,
    filename = 'logs/bigkahuna' + year_month_date + '.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logging.info("\n-------------------------------------------------\n")

# Middleware to check token
@app.before_request
def verify_token():
    token = request.headers.get("Authorization")
    if not token or token != token:
        return jsonify({"status": "Unauthorized"}), 401

@app.route('/register-worker', methods=['POST'])
@limiter.limit("10 per minute")
def register_worker():
    data = request.json
    worker_id = data.get("worker_id")
    if worker_id:
        workers[worker_id] = {"start_time": ""}
        logging.info(f"Worker {worker_id} registered")
        return jsonify({"status": "Worker registered"}), 200
    return jsonify({"status": "Worker ID required"}), 400

@app.route('/task-completed', methods=['POST'])
@limiter.limit("10 per minute")
def task_completed():
    data = request.json
    worker_id = data.get("worker_id")
    if worker_id in workers:
        workers.pop(worker_id)
        logging.info(f"Worker {worker_id} completed task, terminating instance")
        return jsonify({"status": "Task completed"}), 200
    return jsonify({"status": "Unknown worker"}), 400

@app.route('/status', methods=['GET'])
@limiter.limit("5 per minute")
def get_status():
    return jsonify(workers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
