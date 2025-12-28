#!/bin/bash
echo "[SYSTEM] Initiating Cleanup Sequence..."

# 1. Stop the Scouter (Server on Port 8000)
echo "[TASK] Stopping Scouter..."
pid=$(netstat -ano | findstr :8000 | grep LISTENING | awk '{print $5}')
if [ -n "$pid" ]; then
    echo " - Found existing signal on PID $pid. Terminating..."
    taskkill //PID $pid //F > /dev/null 2>&1
    echo " - Scouter Offline."
else
    echo " - Scouter was not running."
fi

# 2. Remove temporary logs
rm -f debug_*.txt
rm -f *.log
echo "- Logs purged."

# 3. Remove Python cache directories
rm -rf __pycache__
rm -rf core/__pycache__
rm -rf miners/__pycache__
rm -rf web/__pycache__
rm -rf ui/__pycache__
echo "- Cache cleared."

echo "[OK] ZeroCrate environment is clean."
