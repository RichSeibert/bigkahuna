#!/bin/bash

if [ ! -d "logs" ]; then
    mkdir logs
fi

sudo dnf install cronie tmux rsync vim -y

launch_cron_job="0 14 * * launch_runpod_instance.sh"
(crontab -l 2>/dev/null; echo "$launch_cron_job") | crontab -
terminate_cron_job="0 18 * * terminate_runpod_instance.sh"
(crontab -l 2>/dev/null; echo "$terminate_cron_job") | crontab -

export EDITOR=vim

wget -qO- cli.runpod.net | sudo bash
runpod_api_key=$(<runpod_api_key.txt)
runpodctl config --apiKey $runpod_api_key

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
