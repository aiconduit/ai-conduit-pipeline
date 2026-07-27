#!/bin/bash
echo "=== AI Conduit セットアップ開始 ==="

# システム依存関係
sudo apt-get update -q
sudo apt-get install -y ffmpeg fonts-noto-cjk fonts-noto-cjk-extra

# Python依存関係
pip install requests pillow numpy google-auth google-auth-oauthlib google-api-python-client requests-oauthlib tweepy

# OpenCodeインストール
npm install -g opencode-ai

# 環境変数設定
cat >> ~/.bashrc << 'ENVEOF'
export DEEPSEEK_API_KEY="${DEEPSEEK_KEY}"
export PATH="/usr/local/bin:$PATH"
ENVEOF

echo "=== セットアップ完了 ==="
