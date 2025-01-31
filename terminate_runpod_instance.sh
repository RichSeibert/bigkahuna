#!/bin/bash

pod_id=$(runpodctl get pod | awk 'NR==2 {print $1}')
if [ -z "$pod_id" ]; then
    echo "No runpod instance running"
    exit
fi
runpodctl remove pod $pod_id
