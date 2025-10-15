from mitmproxy import http
import re

# ===== YouTube設定 =====
# 許可する動画ID
ALLOWED_VIDEO_IDS = [
    # ここに許可したい動画IDを追加
]

# 許可する再生リスト
ALLOWED_PLAYLISTS = [
    "PLLjZ3_QpCZfX4AZGuW7CgX4N3B7ydWf6W",  # ミュージックミックス
    # 他の再生リストを追加する場合はここに
]

# ===== ブロックページ =====
YOUTUBE_BLOCK_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YouTube Blocked</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #667eea;
            color: white;
            text-align: center;
            padding-top: 100px;
        }
    </style>
</head>
<body>
    <h1>&#x1F6AB; YouTube Blocked</h1>
    <p>Only whitelisted videos and playlists are allowed</p>
</body>
</html>
"""

TWITTER_BLOCK_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Twitter For You Blocked</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #1DA1F2;
            color: white;
            text-align: center;
            padding-top: 100px;
        }
    </style>
</head>
<body>
    <h1>&#x1F6AB; Twitter For You Blocked</h1>
    <p>Only Following timeline is allowed</p>
    <p><a href="https://x.com/home" style="color: white;">Go to Following →</a></p>
</body>
</html>
"""

def request(flow: http.HTTPFlow) -> None:
    """リクエスト時の処理"""
    url = flow.request.pretty_url
    host = flow.request.pretty_host
    path = flow.request.path
    
    # ===== YouTube処理 =====
    youtube_domains = ["youtube.com", "googlevideo.com", "ytimg.com", "youtu.be", "ggpht.com"]
    is_youtube = any(domain in host for domain in youtube_domains)
    
    if is_youtube:
        allowed = False
        
        # 再生リストのチェック（最優先）
        if "list=" in url:
            for playlist_id in ALLOWED_PLAYLISTS:
                if f"list={playlist_id}" in url:
                    allowed = True
                    print(f"[✓ ALLOWED] YouTube Playlist: {playlist_id}")
                    break
            
            # 許可されていない再生リストはブロック
            if not allowed:
                print(f"[✗ BLOCKED] YouTube Playlist not in whitelist")
        
        # 動画ページのチェック（再生リストがない場合のみ）
        elif "youtube.com/watch" in url and "?v=" in url:
            for video_id in ALLOWED_VIDEO_IDS:
                if f"v={video_id}" in url or f"v%3D{video_id}" in url:
                    allowed = True
                    print(f"[✓ ALLOWED] YouTube Video: {video_id}")
                    break
            
            if not allowed:
                print(f"[✗ BLOCKED] YouTube Video not in whitelist")
        
        # 動画ストリーム
        elif "googlevideo.com" in host:
            # 再生リストか許可された動画があれば許可
            if len(ALLOWED_VIDEO_IDS) > 0 or len(ALLOWED_PLAYLISTS) > 0:
                allowed = True
        
        # サムネイル
        elif "ytimg.com" in host or "ggpht.com" in host:
            allowed = True
        
        # その他
        elif "youtube.com" in host:
            allowed = False
        
        # ブロック
        if not allowed:
            flow.response = http.Response.make(
                403,
                YOUTUBE_BLOCK_PAGE.encode('utf-8'),
                headers={"Content-Type": "text/html; charset=utf-8"}
            )
        return
    
    # ===== Twitter処理 =====
    twitter_domains = ["twitter.com", "x.com"]
    is_twitter = any(domain in host for domain in twitter_domains)
    
    if is_twitter:
        print(f"[DEBUG] Twitter URL: {url}")
        print(f"[DEBUG] Path: {path}")
        
        # For You タブをブロック
        should_block = False
        
        # ホームページ（デフォルトはFor You）
        if path == "/home" or path == "/":
            # followingパラメータがあれば許可
            if "f=following" not in url and "following" not in url:
                should_block = True
                print(f"[✗ BLOCKED] Twitter For You (home page)")
        
        # For You APIリクエストをブロック
        if "/HomeTimeline" in url:
            should_block = True
            print(f"[✗ BLOCKED] Twitter For You API")
        
        # おすすめタブもブロック
        if "/Explore" in url or "explore" in path.lower():
            should_block = True
            print(f"[✗ BLOCKED] Twitter Explore")
        
        if should_block:
            flow.response = http.Response.make(
                403,
                TWITTER_BLOCK_PAGE.encode('utf-8'),
                headers={"Content-Type": "text/html; charset=utf-8"}
            )
            return
        
        # その他は許可
        print(f"[✓ ALLOWED] Twitter: {path}")
