#!/bin/bash
# Avvia server web
python server.py &
# Aspetta e avvia bot
sleep 10
python main.py
