#!/usr/bin/env python3
"""
Web Dashboard for Instagram Bot Remote Control
"""
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import json
import os
from pathlib import Path
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)

class BotDashboard:
    def __init__(self):
        self.config_file = Path('config.json')
        self.data_dir = Path('bot_data')
        self.data_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def get_stats(self):
        try:
            follows_file = self.data_dir / 'follows.json'
            action_log_file = self.data_dir / 'action_log.json'
            
            follows_data = {}
            action_log = []
            
            if follows_file.exists():
                with open(follows_file, 'r') as f:
                    follows_data = json.load(f)
                    
            if action_log_file.exists():
                with open(action_log_file, 'r') as f:
                    action_log = json.load(f)
            
            now = datetime.now()
            today = now.date()
            
            following = [u for u, d in follows_data.items() if d.get('status') == 'following']
            
            today_follows = len([
                a for a in action_log 
                if a.get('action') == 'follow' 
                and datetime.fromisoformat(a['timestamp']).date() == today
            ])
            
            return {
                'total_following': len(following),
                'today_follows': today_follows,
                'recent_actions': action_log[-10:] if action_log else [],
                'last_action': action_log[-1]['timestamp'] if action_log else None
            }
            
        except Exception as e:
            return {'error': str(e)}

dashboard = BotDashboard()

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Bot Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; }
        .stat { display: flex; justify-content: space-between; margin: 10px 0; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .form-group { margin-bottom: 15px; }
        .form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Instagram Bot Dashboard</h1>
        </div>
        
        {% if message %}
        <div class="success">{{ message }}</div>
        {% endif %}
        
        <div class="grid">
            <div class="card">
                <h3>📊 Statistics</h3>
                <div class="stat">
                    <span>Following:</span>
                    <span>{{ stats.total_following or 0 }}</span>
                </div>
                <div class="stat">
                    <span>Today's Follows:</span>
                    <span>{{ stats.today_follows or 0 }}</span>
                </div>
                <div class="stat">
                    <span>Status:</span>
                    <span>{% if config.instagram and config.instagram.username %}✅ Configured{% else %}❌ Not Configured{% endif %}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🔧 Configuration</h3>
                <form method="post" action="/update_config">
                    <div class="form-group">
                        <label>Instagram Username:</label>
                        <input type="text" name="username" value="{{ config.instagram.username if config.instagram else '' }}" placeholder="your_instagram_username" required>
                    </div>
                    <div class="form-group">
                        <label>Instagram Password:</label>
                        <input type="password" name="password" value="{{ config.instagram.password if config.instagram else '' }}" placeholder="your_instagram_password" required>
                    </div>
                    <div class="form-group">
                        <label>Target Accounts (comma separated):</label>
                        <textarea name="target_accounts" placeholder="deadmau5, skrillex, 1001tracklists" required>{{ config.instagram.target_accounts | join(', ') if config.instagram else 'deadmau5, skrillex, 1001tracklists' }}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Users per Account:</label>
                        <input type="number" name="users_per_account" value="{{ config.instagram.users_per_account if config.instagram else 5 }}" min="1" max="25">
                    </div>
                    <div class="form-group">
                        <label>Daily Follow Limit:</label>
                        <input type="number" name="daily_follow_limit" value="{{ config.instagram.daily_follow_limit if config.instagram else 15 }}" min="1" max="100">
                    </div>
                    <button type="submit" class="btn">Save Configuration</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    config = dashboard.load_config()
    stats = dashboard.get_stats()
    message = session.pop('message', None)
    return render_template_string(DASHBOARD_TEMPLATE, config=config, stats=stats, message=message)

@app.route('/update_config', methods=['POST'])
def update_config():
    config = dashboard.load_config()
    if 'instagram' not in config:
        config['instagram'] = {}
    
    # Update Instagram credentials and settings
    config['instagram']['username'] = request.form['username']
    config['instagram']['password'] = request.form['password']
    config['instagram']['target_accounts'] = [acc.strip() for acc in request.form['target_accounts'].split(',')]
    config['instagram']['users_per_account'] = int(request.form['users_per_account'])
    config['instagram']['daily_follow_limit'] = int(request.form['daily_follow_limit'])
    config['instagram']['unfollow_after_hours'] = config.get('instagram', {}).get('unfollow_after_hours', 48)
    
    dashboard.save_config(config)
    session['message'] = "✅ Configuration saved successfully!"
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
 