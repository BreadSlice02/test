from flask import Flask, render_template_string
import requests
import threading
import time
from datetime import datetime

# Flask app initialization
app = Flask(__name__)

# YouTube API Configuration
API_KEY = "AIzaSyAde_WpqhSD-H21dDKZSNq89e3xrkuN8WI"
CHANNELS = {
    "main": {
        "id": "UC7KFjkgBWBUnjWwAk-xixCg",
        "view_count": 0,
        "top_videos": [],
        "all_videos": []
    },
    "second": {
        "id": "UCdOLoz3Dpg20bflecytUD0g",
        "view_count": 0,
        "top_videos": [],
        "all_videos": []
    }
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Channel Analytics</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1c2c 0%, #2a2d3e 100%);
            color: #ffffff;
            padding: 2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .youtube-icon {
            width: 80px;
            height: 80px;
            margin-bottom: 1rem;
            animation: pulse 2s infinite;
        }
        
        .total-stats {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-bottom: 3rem;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .channels-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .channel-card {
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        h1, h2 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #ffffff;
            font-weight: 600;
        }
        
        .stats-container {
            display: flex;
            justify-content: space-around;
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .stat-box {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff0000 0%, #ff6b6b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
            animation: countUp 1s ease-out;
        }
        
        .revenue {
            background: linear-gradient(135deg, #00ff87 0%, #60efff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        @keyframes countUp {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
        .subtitle {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .divider {
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.1), transparent);
            margin: 2rem 0;
        }
        
        .top-videos {
            display: grid;
            gap: 1rem;
        }
        
        .video-card {
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.2s, background 0.2s;
            text-decoration: none;
            color: inherit;
        }
        
        .video-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .thumbnail {
            width: 120px;
            height: 68px;
            border-radius: 8px;
            object-fit: cover;
        }
        
        .video-info {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .video-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            font-size: 0.875rem;
        }
        
        .video-stats {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.75rem;
            display: flex;
            gap: 1rem;
        }
        
        .video-revenue {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-end;
            padding-left: 1rem;
            border-left: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .revenue-amount {
            font-weight: 600;
            font-size: 1rem;
            background: linear-gradient(135deg, #00ff87 0%, #60efff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .revenue-label {
            font-size: 0.625rem;
            color: rgba(255, 255, 255, 0.5);
        }
        
        .update-time {
            text-align: center;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 3rem;
        }

        .channel-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .subscriber-count {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
        }

        .engagement-stats {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.6);
        }

        .stat-icon {
            display: inline-block;
            width: 16px;
            height: 16px;
            margin-right: 0.25rem;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <svg class="youtube-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z" fill="#ff0000"/>
                <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" fill="white"/>
            </svg>
            <h1>YouTube Channel Analytics</h1>
        </div>

        <div class="total-stats">
            <div class="stat-box">
                <div class="subtitle">Total Views</div>
                <div class="stat-value">{{ "{:,}".format(total_views) }}</div>
            </div>
            <div class="stat-box">
                <div class="subtitle">Total Revenue</div>
                <div class="stat-value revenue">${{ "{:.2f}".format(total_revenue) }}</div>
            </div>
            <div class="stat-box">
                <div class="subtitle">Total Videos</div>
                <div class="stat-value">{{ total_videos }}</div>
            </div>
            <div class="stat-box">
                <div class="subtitle">Total Engagement</div>
                <div class="stat-value">{{ "{:,}".format(total_likes + total_comments) }}</div>
            </div>
        </div>

        <div class="channels-grid">
            {% for key, channel in channels.items() %}
            <div class="channel-card">
                <div class="channel-header">
                    <h2>{{ channel.get('title', 'Channel ' + key.title()) }}</h2>
                    <div class="subscriber-count">{{ "{:,}".format(channel.get('subscriber_count', 0)) }} subscribers</div>
                </div>
                
                <div class="stats-container">
                    <div class="stat-box">
                        <div class="subtitle">Views</div>
                        <div class="stat-value">{{ "{:,}".format(channel['view_count']) }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="subtitle">Revenue</div>
                        <div class="stat-value revenue">${{ "{:.2f}".format(channel.get('revenue', 0)) }}</div>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <h3>Top Videos</h3>
                <div class="top-videos">
                    {% for video in channel['top_videos'] %}
                    <a href="https://youtube.com/watch?v={{ video.id }}" target="_blank" class="video-card">
                        <img src="{{ video.thumbnail }}" alt="{{ video.title }}" class="thumbnail">
                        <div class="video-info">
                            <div class="video-title">{{ video.title }}</div>
                            <div class="video-stats">
                                <span>{{ "{:,}".format(video.views) }} views</span>
                                <span>{{ "{:,}".format(video.likes) }} likes</span>
                                <span>{{ "{:,}".format(video.comments) }} comments</span>
                            </div>
                        </div>
                        <div class="video-revenue">
                            <div class="revenue-amount">${{ "{:.2f}".format(video.views / 1000 * 0.1) }}</div>
                            <div class="revenue-label">Est. Revenue</div>
                        </div>
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="update-time">Last updated: {{ update_time }}</div>
    </div>
</body>
</html>
"""

def fetch_channel_data(channel_key):
    try:
        channel_id = CHANNELS[channel_key]["id"]
        
        # Get channel's uploads playlist ID and channel info
        channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails,snippet,statistics&id={channel_id}&key={API_KEY}"
        channel_response = requests.get(channel_url)
        channel_response.raise_for_status()
        channel_data = channel_response.json()['items'][0]
        
        uploads_playlist_id = channel_data['contentDetails']['relatedPlaylists']['uploads']
        channel_title = channel_data['snippet']['title']
        subscriber_count = int(channel_data['statistics'].get('subscriberCount', 0))
        
        CHANNELS[channel_key].update({
            "title": channel_title,
            "subscriber_count": subscriber_count
        })
        
        # Get all videos from uploads playlist
        playlist_items = []
        next_page_token = None
        
        while True:
            playlist_url = (
                f"https://www.googleapis.com/youtube/v3/playlistItems"
                f"?part=snippet&playlistId={uploads_playlist_id}&maxResults=50&key={API_KEY}"
            )
            if next_page_token:
                playlist_url += f"&pageToken={next_page_token}"
                
            playlist_response = requests.get(playlist_url)
            playlist_response.raise_for_status()
            playlist_data = playlist_response.json()
            
            playlist_items.extend(playlist_data['items'])
            
            next_page_token = playlist_data.get('nextPageToken')
            if not next_page_token:
                break
        
        # Get video IDs
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items]
        
        # Get video statistics in batches
        all_videos = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i + 50]
            videos_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={','.join(batch_ids)}&key={API_KEY}"
            videos_response = requests.get(videos_url)
            videos_response.raise_for_status()
            
            for item in videos_response.json()['items']:
                video_stats = item['statistics']
                all_videos.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'views': int(video_stats.get('viewCount', 0)),
                    'likes': int(video_stats.get('likeCount', 0)),
                    'comments': int(video_stats.get('commentCount', 0)),
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'publishedAt': item['snippet']['publishedAt']
                })
        
        # Sort videos by views and update channel data
        sorted_videos = sorted(all_videos, key=lambda x: x['views'], reverse=True)
        
        CHANNELS[channel_key].update({
            "all_videos": all_videos,
            "top_videos": sorted_videos[:3],
            "view_count": sum(video['views'] for video in all_videos),
            "video_count": len(all_videos),
            "total_likes": sum(video['likes'] for video in all_videos),
            "total_comments": sum(video['comments'] for video in all_videos),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        print(f"Updated {channel_key} channel ({channel_title})")
        print(f"Total videos: {len(all_videos)}")
        print(f"Total views: {CHANNELS[channel_key]['view_count']}")
        
    except Exception as e:
        print(f"Error fetching {channel_key} channel: {e}")
        CHANNELS[channel_key]["error"] = str(e)

def fetch_all_channels():
    for channel_key in CHANNELS.keys():
        fetch_channel_data(channel_key)
        time.sleep(1)  # Small delay between channel requests to avoid rate limiting

def calculate_revenue(views):
    # Estimated revenue calculation (CPM = $0.1 per 1000 views)
    return (views / 1000) * 0.1

def background_updater():
    while True:
        try:
            fetch_all_channels()
            time.sleep(600)  # Update every 10 minutes
        except Exception as e:
            print(f"Error in background updater: {e}")
            time.sleep(60)  # Wait a minute before retrying if there's an error

@app.route('/yt')
def display_views():
    try:
        # Calculate total statistics
        total_views = sum(channel["view_count"] for channel in CHANNELS.values())
        total_videos = sum(channel["video_count"] for channel in CHANNELS.values())
        total_likes = sum(channel.get("total_likes", 0) for channel in CHANNELS.values())
        total_comments = sum(channel.get("total_comments", 0) for channel in CHANNELS.values())
        total_revenue = calculate_revenue(total_views)
        
        # Add revenue calculations to each channel
        for channel in CHANNELS.values():
            channel["revenue"] = calculate_revenue(channel["view_count"])
        
        # Get current time for last updated
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template_string(HTML_TEMPLATE,
            channels=CHANNELS,
            total_views=total_views,
            total_videos=total_videos,
            total_likes=total_likes,
            total_comments=total_comments,
            total_revenue=total_revenue,
            update_time=update_time
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    # Start the background thread
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()

    # Fetch initial data
    fetch_all_channels()

    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)