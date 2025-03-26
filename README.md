# bigkahuna
Host to control workers.

# TODO
1. Replace `workers` global variable in server.py with external data source. You can't run multiple instances of gunicorn, there will be data inconsistency accross the threads
2. Get APS scheduler working, so I don't have to use cron anymore

## Setup
0. Make an AWS EC2 instance and clone this repo in it. Add an inbound rule for custom TCP port 8080, all IPs
1. Run `bash setup.sh` to install and setup everything that's needed
2. Start the server with `nohup bash run_server.sh &` to run in the background.
3. To kill it, find it using `ps aux | grep python` and kill the instance
4. Transfer the runpod_api_key.txt and the flask secret token.txt files to the repo
