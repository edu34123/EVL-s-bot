#!/bin/bash

# Avvia il server health check in background
python health_server.py &

# Aspetta che il server si avvii
sleep 5

# Avvia il bot Discord principale
python main.py
