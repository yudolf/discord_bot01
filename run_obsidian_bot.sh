#!/bin/bash
echo "🚀 ObsidianBot起動中..."
cd "$(dirname "$0")"
source venv/bin/activate
pip install -r requirements_obsidian.txt
echo "📝 Obsidianノート記録Bot開始"
python3 obsidian_bot.py