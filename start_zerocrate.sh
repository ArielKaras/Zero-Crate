#!/bin/bash

# ZeroCrate System Control (Bash)

# Configuration
BRAVE_PATH="/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

while true; do
    clear
    echo "================================================="
    echo "  ZERO CRATE - OPERATOR TERMINAL"
    echo "================================================="
    echo "  1. [IGNITION] Start Discovery Server"
    echo "  2. [UI]       Open Dashboard (Brave)"
    echo "  3. [CLEANUP]  Wipe Logs and Cache"
    echo "  4. [TEST]     Run System Doctor"
    echo "  5. [EXIT]     Close Terminal"
    echo "================================================="
    read -p "Select option (1-5): " choice

    case $choice in
        1)
            clear
            echo "[SYSTEM] Starting ZeroCrate Discovery Server..."
            echo "[INFO] Access the UI at: http://127.0.0.1:8000"
            
            # Offer Auto-Launch
            read -p "Launch Brave Browser now? (y/n): " launch_opt
            if [[ "$launch_opt" == "y" || "$launch_opt" == "Y" ]]; then
                "$BRAVE_PATH" http://127.0.0.1:8000 &
            fi
            
            # Using python -m uvicorn to ensure path resolution works
            python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 --log-level info
            read -p "Press Enter to return to menu..."
            ;;
        2)
            echo "[SYSTEM] Launching Brave..."
            "$BRAVE_PATH" http://127.0.0.1:8000 &
            read -p "Press Enter to return to menu..."
            ;;
        3)
            clear
            echo "[SYSTEM] Purging temporary files..."
            rm -f debug_*.txt *.log
            rm -rf __pycache__ core/__pycache__ miners/__pycache__ backend/__pycache__ ui/__pycache__ frontend/__pycache__
            echo "[OK] Systems Clean."
            read -p "Press Enter to return to menu..."
            ;;
        4)
            clear
            echo "[SYSTEM] Running Diagnostics..."
            python tests/verify_system.py
            read -p "Press Enter to return to menu..."
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option."
            sleep 1
            ;;
    esac
done
