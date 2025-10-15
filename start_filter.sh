#!/bin/bash

echo "🔧 プロキシを設定中..."

# 使用しているネットワークインターフェースを確認
# Wi-Fiの場合は "Wi-Fi"、有線の場合は "Ethernet" など
NETWORK_INTERFACE="Wi-Fi"

# プロキシを有効化
networksetup -setwebproxy "$NETWORK_INTERFACE" 127.0.0.1 8080
networksetup -setsecurewebproxy "$NETWORK_INTERFACE" 127.0.0.1 8080
networksetup -setwebproxystate "$NETWORK_INTERFACE" on
networksetup -setsecurewebproxystate "$NETWORK_INTERFACE" on

echo "✅ プロキシを有効化しました"
echo ""
echo "📋 現在のフィルター設定:"
echo "   - YouTube: 特定チャンネルのみ許可"
echo ""
echo "🔍 フィルターを起動中..."
echo "   (終了するには 'q' を押してください)"
echo ""

# mitmproxyを起動（filter.pyを使用）
mitmproxy -s filter.py -p 8080 --set console_mouse=false
