#!/bin/bash

# TODO figure out how to make `bash run.sh ...` command non continue in the background so start.sh doesn't get blocked
runpodctl create pod --args "bash -c 'cd /workspace/roobot; python bot.py; cd /workspace/rooporter; bash run.sh 2>&1 | tee last_run_output.txt; /start.sh'" \
                     --secureCloud \
                     --containerDiskSize 20 \
                     --gpuCount 1 \
                     --gpuType "NVIDIA A40" \
                     --templateId "runpod-torch-v240" \
                     --imageName "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04" \
                     --name "rooporter_pod" \
                     --volumePath "/workspace" \
                     --ports "22/tcp" \
                     --networkVolumeId "ys3y7qzc5y"
