#!/bin/sh
cd /opt
source venv/bin/activate
cd key_manager
gunicorn isolated.wsgi:application
