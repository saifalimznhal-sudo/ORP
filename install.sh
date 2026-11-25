#!/bin/bash
set -e
cd "$(dirname "$0")"

if command -v pkg >/dev/null 2>&1; then
    pkg install python -y
elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

python3 -m pip install --user -r requirements.txt

echo "ORP installed successfully!"
