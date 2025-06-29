#!/usr/bin/env python3
"""
Complete Web Dashboard for Instagram Bot Remote Control
"""
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
import json
import os
import subprocess
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
            
    def get_service_status(self, service_name):
        try:
            result = subprocess.run(['systemctl', 'is-active', service_name], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
            
    def control_service(self, service_name, action):
        try:
            result = subprocess.run(['systemctl', action, service_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
            
    def get_bot_stats(self):
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
                'last_action': action_log[-1]['timestamp'] if action_log else None,
            }
        except:
            return {'total_following': 0, 'today_follows': 0, 'last_action': None}
            
    def get_recent_logs(self, service_name, lines=20):
        try:
            result = subprocess.run(['journalctl', '-u', service_name, '-n', str(lines), '--no-pager'], 
                                  capture_output=True, text=True)
            return result.stdout
        except:
            return "Unable to fetch logs"

dashboard = BotDashboard()

@app.route('/')
def index():
    config = dashboard.load_config()
    stats = dashboard.get_bot_stats()
    
    # Check if bot is configured
    instagram_config = config.get('instagram', {})
    is_configured = bool(instagram_config.get('username') and instagram_config.get('password'))
    
    # Get service status
    bot_status = dashboard.get_service_status('instagram-bot')
    dashboard_status = dashboard.get_service_status('instagram-dashboard')
    
    template = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Instagram Bot Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white; 
            padding: 30px; 
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .content { padding: 30px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .card { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .card h3 { 
            color: #333; 
            margin-bottom: 20px; 
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat-item { 
            display: flex; 
            justify-content: space-between; 
            padding: 10px 0; 
            border-bottom: 1px solid #eee;
        }
        .stat-item:last-child { border-bottom: none; }
        .stat-value { font-weight: bold; color: #4CAF50; }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #555;
        }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus, .form-group textarea:focus { 
            outline: none; 
            border-color: #4CAF50; 
        }
        .form-group textarea { height: 80px; resize: vertical; }
        .btn { 
            background: #4CAF50; 
            color: white; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn:hover { background: #45a049; }
        .btn-danger { background: #f44336; }
        .btn-danger:hover { background: #da190b; }
        .btn-warning { background: #ff9800; }
        .btn-warning:hover { background: #f57c00; }
        .btn-info { background: #2196F3; }
        .btn-info:hover { background: #0b7dda; }
        .status-badge { 
            padding: 5px 12px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-configured { background: #d4edda; color: #155724; }
        .status-not-configured { background: #f8d7da; color: #721c24; }
        .status-active { background: #d1ecf1; color: #0c5460; }
        .status-inactive { background: #f8d7da; color: #721c24; }
        .alert { 
            padding: 15px; 
            margin-bottom: 20px; 
            border-radius: 8px; 
            font-weight: 500;
        }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .logs-container { 
            background: #1e1e1e; 
            color: #00ff00; 
            padding: 20px; 
            border-radius: 8px; 
            font-family: 'Courier New', monospace; 
            font-size: 14px;
            max-height: 400px; 
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .full-width { grid-column: 1 / -1; }
        .service-controls { display: flex; gap: 10px; flex-wrap: wrap; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Instagram Bot Dashboard</h1>
            <p>24/7 Autonomous Instagram Automation</p>
        </div>
        
        <div class="content">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-success">✅ {{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="grid">
                <!-- Statistics -->
                <div class="card">
                    <h3>📊 Statistics</h3>
                    <div class="stat-item">
                        <span>Following:</span>
                        <span class="stat-value">{{ stats.total_following }}</span>
                    </div>
                    <div class="stat-item">
                        <span>Today's Follows:</span>
                        <span class="stat-value">{{ stats.today_follows }}</span>
                    </div>
                    <div class="stat-item">
                        <span>Status:</span>
                        <span class="status-badge {% if is_configured %}status-configured{% else %}status-not-configured{% endif %}">
                            {% if is_configured %}✅ Configured{% else %}❌ Not Configured{% endif %}
                        </span>
                    </div>
                    {% if stats.last_action %}
                    <div class="stat-item">
                        <span>Last Action:</span>
                        <span class="stat-value">{{ stats.last_action[:19] }}</span>
                    </div>
                    {% endif %}
                </div>
                
                <!-- Service Status -->
                <div class="card">
                    <h3>⚙️ Service Status</h3>
                    <div class="stat-item">
                        <span>Instagram Bot:</span>
                        <span class="status-badge {% if bot_status == 'active' %}status-active{% else %}status-inactive{% endif %}">
                            {{ bot_status.upper() }}
                        </span>
                    </div>
                    <div class="stat-item">
                        <span>Web Dashboard:</span>
                        <span class="status-badge {% if dashboard_status == 'active' %}status-active{% else %}status-inactive{% endif %}">
                            {{ dashboard_status.upper() }}
                        </span>
                    </div>
                    <div style="margin-top: 20px;">
                        <h4>Service Controls:</h4>
                        <div class="service-controls" style="margin-top: 10px;">
                            <button onclick="controlService('instagram-bot', 'start')" class="btn btn-info">▶️ Start Bot</button>
                            <button onclick="controlService('instagram-bot', 'stop')" class="btn btn-danger">⏹️ Stop Bot</button>
                            <button onclick="controlService('instagram-bot', 'restart')" class="btn btn-warning">🔄 Restart Bot</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid">
                <!-- Configuration -->
                <div class="card">
                    <h3>🔧 Configuration</h3>
                    <form method="post" action="/update_config">
                        <div class="form-group">
                            <label>Instagram Username:</label>
                            <input type="text" name="username" value="{{ config.instagram.username if config.instagram else '' }}" required>
                        </div>
                        <div class="form-group">
                            <label>Instagram Password:</label>
                            <input type="password" name="password" value="{{ config.instagram.password if config.instagram else '' }}" required>
                        </div>
                        <div class="form-group">
                            <label>Target Accounts (comma separated):</label>
                            <textarea name="target_accounts">{{ config.instagram.target_accounts | join(', ') if config.instagram else '1001tracklists, housemusic.us, edm, housemusicnerds' }}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Users per Account:</label>
                            <input type="number" name="users_per_account" value="{{ config.instagram.users_per_account if config.instagram else 25 }}" min="1" max="50">
                        </div>
                        <div class="form-group">
                            <label>Daily Follow Limit:</label>
                            <input type="number" name="daily_follow_limit" value="{{ config.instagram.daily_follow_limit if config.instagram else 100 }}" min="1" max="200">
                        </div>
                        <button type="submit" class="btn">💾 Save Configuration</button>
                    </form>
                </div>
                
                <!-- Notification Settings -->
                <div class="card">
                    <h3>📧 Notification Settings</h3>
                    <form method="post" action="/update_notifications">
                        <h4>Email Notifications:</h4>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="email_enabled" {% if config.notifications and config.notifications.email.enabled %}checked{% endif %}> 
                                Enable Email Notifications
                            </label>
                        </div>
                        <div class="form-group">
                            <label>Sender Email (Gmail):</label>
                            <input type="email" name="sender_email" value="{{ config.notifications.email.sender_email if config.notifications and config.notifications.email else '' }}">
                        </div>
                        <div class="form-group">
                            <label>App Password:</label>
                            <input type="password" name="sender_password" value="{{ config.notifications.email.sender_password if config.notifications and config.notifications.email else '' }}">
                        </div>
                        <div class="form-group">
                            <label>Recipient Email:</label>
                            <input type="email" name="recipient_email" value="{{ config.notifications.email.recipient_email if config.notifications and config.notifications.email else '' }}">
                        </div>
                        
                        <h4 style="margin-top: 20px;">Discord Notifications:</h4>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="discord_enabled" {% if config.notifications and config.notifications.discord.enabled %}checked{% endif %}> 
                                Enable Discord Notifications
                            </label>
                        </div>
                        <div class="form-group">
                            <label>Discord Webhook URL:</label>
                            <input type="url" name="webhook_url" value="{{ config.notifications.discord.webhook_url if config.notifications and config.notifications.discord else '' }}">
                        </div>
                        <button type="submit" class="btn">📧 Save Notifications</button>
                    </form>
                </div>
            </div>
            
            <!-- Live Logs -->
            <div class="card full-width">
                <h3>📋 Live Logs</h3>
                <div style="margin-bottom: 15px;">
                    <button onclick="refreshLogs('instagram-bot')" class="btn btn-info">🔄 Refresh Bot Logs</button>
                    <button onclick="refreshLogs('instagram-dashboard')" class="btn btn-info">🔄 Refresh Dashboard Logs</button>
                </div>
                <div id="logs" class="logs-container">
                    Click "Refresh Bot Logs" to view live system logs...
                </div>
            </div>
        </div>
    </div>

    <script>
        function controlService(service, action) {
            fetch('/control_service', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({service: service, action: action})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Service ${action} successful!`);
                    location.reload();
                } else {
                    alert(`❌ Service ${action} failed: ${data.error}`);
                }
            });
        }
        
        function refreshLogs(service) {
            document.getElementById('logs').textContent = 'Loading logs...';
            fetch(`/logs/${service}`)
            .then(response => response.text())
            .then(data => {
                document.getElementById('logs').textContent = data;
            });
        }
        
        // Auto-refresh stats every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
    """
    
    return render_template_string(template, 
                                config=config, 
                                stats=stats, 
                                is_configured=is_configured,
                                bot_status=bot_status,
                                dashboard_status=dashboard_status)

@app.route('/update_config', methods=['POST'])
def update_config():
    config = dashboard.load_config()
    
    # Update Instagram settings
    if 'instagram' not in config:
        config['instagram'] = {}
    
    config['instagram']['username'] = request.form['username']
    config['instagram']['password'] = request.form['password']
    config['instagram']['target_accounts'] = [acc.strip() for acc in request.form['target_accounts'].split(',')]
    config['instagram']['users_per_account'] = int(request.form['users_per_account'])
    config['instagram']['daily_follow_limit'] = int(request.form['daily_follow_limit'])
    
    dashboard.save_config(config)
    flash('Configuration saved successfully!')
    return redirect(url_for('index'))

@app.route('/update_notifications', methods=['POST'])
def update_notifications():
    config = dashboard.load_config()
    
    # Initialize notifications structure
    if 'notifications' not in config:
        config['notifications'] = {'email': {}, 'discord': {}}
    
    # Update email settings
    config['notifications']['email'] = {
        'enabled': 'email_enabled' in request.form,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': request.form['sender_email'],
        'sender_password': request.form['sender_password'],
        'recipient_email': request.form['recipient_email'],
        'daily_report': True,
        'error_alerts': True
    }
    
    # Update Discord settings
    config['notifications']['discord'] = {
        'enabled': 'discord_enabled' in request.form,
        'webhook_url': request.form['webhook_url'],
        'daily_report': True,
        'error_alerts': True
    }
    
    dashboard.save_config(config)
    flash('Notification settings saved successfully!')
    return redirect(url_for('index'))

@app.route('/control_service', methods=['POST'])
def control_service():
    data = request.json
    service = data['service']
    action = data['action']
    
    success = dashboard.control_service(service, action)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': f'Failed to {action} {service}'})

@app.route('/logs/<service>')
def get_logs(service):
    logs = dashboard.get_recent_logs(service, 50)
    return logs

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 