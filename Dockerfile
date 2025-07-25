FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ポートを公開（必要に応じて）
EXPOSE 8000

# アプリケーションを実行
CMD ["python3", "obsidian_bot.py"]