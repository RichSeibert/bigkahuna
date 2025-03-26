#!/bin/bash

# TODO fix workers variable in server.py so I can run more instances of gunicorn.
# There should be an external datasource like redis or a db instead of a global
source .venv/bin/activate
gunicorn --workers 1 --bind 0.0.0.0:8080 server:app
