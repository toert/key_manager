#!/bin/sh
cd /opt
source venv/bin/activate
cd isolated
gunicorn isolated.wsgi:application
