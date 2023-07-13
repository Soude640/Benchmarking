#!/bin/bash

# Install Python 3.8
sudo apt update
sudo apt install python3.8 python3.8-venv -y

# Create virtual environment
python3.8 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Start Django server on port 8000
python3 manage.py migrate
python manage.py runserver 8000
