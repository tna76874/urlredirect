#!/bin/sh
gunicorn -w 3 -b 0.0.0.0:5000 main:app