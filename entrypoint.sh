#!/bin/bash
# Background process to fix ownership
fix_ownership() {
    while true; do
        find /vault/01_Inbox/Telegram -type f -name "*.md" -user root -exec chown 1000:1000 {} \;
        sleep 5
    done
}

# Start background process
fix_ownership &

# Start the Python bot
python main.py
