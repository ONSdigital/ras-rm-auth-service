#!/bin/bash

gunicorn -b 0.0.0.0:8041 run:app
