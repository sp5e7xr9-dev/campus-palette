#!/bin/bash
set -e
cd "$(dirname "$0")"
echo 'Campus Palette: http://127.0.0.1:4173/ をブラウザで開いてください。'
echo '終了するには Control+C を押してください。'
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
