#!/usr/bin/env python3
"""
Instagram Bot Web Dashboard
"""
from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)

def load_data():
    """Load bot data files"""
    data = {
        'follows': {},
        'action_log': [],
        'stats': {}
    }
    
    # Load follows data
    follows_file = Path('instagram_data/follows.json')
    if follows_file.exists():
        try:
            with open(follows_file, 'r') as f:
                data['follows'] = json.load(f)
        except:
            pass
    
    # Load action log
    log_file = Path('instagram_data/action_log.json')
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                data['action_log'] = json.load(f)
        except:
            pass
    
    # Calculate stats
    now = datetime.now()
    following = [u for u, d in data['follows'].items() if d.get('status') == 'following']
    unfollowed = [u for u, d in data['follows'].items() if d.get('status') == 'unfollowed']
    
    # Recent actions (last 24 hours)
    recent_actions = [
        a for a in data['action_log'] 
        if datetime.fromisoformat(a['timestamp']) > now - timedelta(days=1)
    ]
    
    data['stats'] = {
        'total_following': len(following),
        'total_unfollowed': len(unfollowed),
        'recent_actions': len(recent_actions),
        'recent_follows': len([a for a in recent_actions if a['action'] == 'follow']),
        'recent_unfollows': len([a for a in recent_actions if a['action'] == 'unfollow']),
        'last_updated': now.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return data

@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = load_data()
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instagram Bot Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background-color: #f5f5f5; 
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
            }
            .header { 
                text-align: center; 
                margin-bottom: 30px; 
            }
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }
            .stat-card { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 8px; 
                text-align: center; 
                border-left: 4px solid #007bff; 
            }
            .stat-number { 
                font-size: 2em; 
                font-weight: bold; 
                color: #007bff; 
            }
            .stat-label { 
                color: #666; 
                margin-top: 5px; 
            }
            .section { 
                margin-bottom: 30px; 
            }
            .section h3 { 
                border-bottom: 2px solid #007bff; 
                padding-bottom: 10px; 
            }
            .activity-item { 
                padding: 10px; 
                border: 1px solid #eee; 
                margin-bottom: 5px; 
                border-radius: 4px; 
                background: #fafafa; 
            }
            .timestamp { 
                color: #666; 
                font-size: 0.9em; 
            }
            .action-follow { 
                border-left: 4px solid #28a745; 
            }
            .action-unfollow { 
                border-left: 4px solid #dc3545; 
            }
            .refresh-btn { 
                background: #007bff; 
                color: white; 
                border: none; 
                padding: 10px 20px; 
                border-radius: 4px; 
                cursor: pointer; 
                margin-bottom: 20px; 
            }
            .refresh-btn:hover { 
                background: #0056b3; 
            }
        </style>
        <script>
            function refreshData() {
                location.reload();
            }
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Instagram Bot Dashboard</h1>
                <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
                <p class="timestamp">Last Updated: {{ data.stats.last_updated }}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ data.stats.total_following }}</div>
                    <div class="stat-label">Currently Following</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.stats.total_unfollowed }}</div>
                    <div class="stat-label">Total Unfollowed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.stats.recent_follows }}</div>
                    <div class="stat-label">Follows (24h)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.stats.recent_unfollows }}</div>
                    <div class="stat-label">Unfollows (24h)</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📋 Recent Activity</h3>
                {% for action in data.action_log[-20:] %}
                <div class="activity-item action-{{ action.action }}">
                    <strong>{{ action.action.title() }}</strong>: {{ action.target }}
                    <div class="timestamp">{{ action.timestamp }}</div>
                    {% if action.details %}
                    <div style="font-size: 0.9em; color: #666;">{{ action.details }}</div>
                    {% endif %}
                </div>
                {% endfor %}
                
                {% if not data.action_log %}
                <p style="color: #666; text-align: center;">No activity recorded yet</p>
                {% endif %}
            </div>
            
            <div class="section">
                <h3>👥 Current Follows (Last 10)</h3>
                {% set recent_follows = [] %}
                {% for username, info in data.follows.items() %}
                    {% if info.status == 'following' %}
                        {% set _ = recent_follows.append((username, info)) %}
                    {% endif %}
                {% endfor %}
                
                {% for username, info in recent_follows[-10:] %}
                <div class="activity-item">
                    <strong>@{{ username }}</strong>
                    <div class="timestamp">Followed: {{ info.followed_at }}</div>
                </div>
                {% endfor %}
                
                {% if not recent_follows %}
                <p style="color: #666; text-align: center;">No users currently being followed</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, data=data)

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    data = load_data()
    return jsonify(data['stats'])

@app.route('/api/activity')
def api_activity():
    """API endpoint for recent activity"""
    data = load_data()
    return jsonify(data['action_log'][-50:])  # Last 50 actions

if __name__ == '__main__':
    # Create instagram_data directory if it doesn't exist
    Path('instagram_data').mkdir(exist_ok=True)
    
    print("🌐 Starting Instagram Bot Dashboard...")
    print("🔗 Access at: http://localhost:5000")
    print("🔗 AWS Access at: http://your-ec2-public-ip:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 