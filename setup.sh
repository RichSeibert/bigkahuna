#!/bin/bash

if [ ! -d "logs" ]; then
    mkdir logs
fi

sudo dnf install crontab tmux rsync vim -y

new_cron_job="0 3 * * * /path/to/your_script.sh"
(crontab -l 2>/dev/null; echo "$new_cron_job") | crontab -

wget -qO- cli.runpod.net | sudo bash
runpod_api_key=$(<runpod_api_key)
runpodctl config --apiKey $runpod_api_key

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
