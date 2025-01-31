#!/bin/bash

if [ ! -d "logs" ]; then
    mkdir logs
fi

wget -qO- cli.runpod.net | sudo bash
runpod_api_key=$(<runpod_api_key)
runpodctl config --apiKey $runpod_api_key

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
