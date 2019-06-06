#!/bin/bash

gunicorn -w $GUNICORN_WORKERS --worker-class gevent -b 0.0.0.0:5000 run:app
