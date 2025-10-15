#!/bin/bash

NETWORK_INTERFACE="Wi-Fi"

# プロキシを無効化
networksetup -setwebproxystate "$NETWORK_INTERFACE" off
networksetup -setsecurewebproxystate "$NETWORK_INTERFACE" off

echo "✅ プロキシを無効化しました"
