#!/bin/bash
echo "🚀 ニュースBot起動中..."
cd "$(dirname "$0")"
source venv/bin/activate
pip install -r requirements_news.txt
echo "📰 ニュース配信Bot開始"
python3 news_bot.py