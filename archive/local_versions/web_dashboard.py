#!/usr/bin/env python3
"""
Instagram Automation Web Dashboard
Web interface for monitoring and controlling the 24/7 automation service
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import subprocess
import signal

app = Flask(__name__)

class DashboardAPI:
    def __init__(self):
        self.config_file = 'scheduler_config.json'
        self.status_file = 'instagram_data/scheduler_status.json'
        
    def get_config(self):
        """Get current configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
        
    def save_config(self, config):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
    def get_status(self):
        """Get current scheduler status"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {'status': 'unknown'}
        
    def get_stats(self):
        """Get automation statistics"""
        stats = {
            'total_followed': 0,
            'total_unfollowed': 0,
            'daily_follows': 0,
            'pending_unfollows': 0,
            'success_rate': 0
        }
        
        # Load followed users
        followed_users_file = Path('followed_users.json')
        if followed_users_file.exists():
            with open(followed_users_file, 'r') as f:
                followed_users = json.load(f)
                
            total_followed = len([u for u in followed_users if isinstance(u, dict)])
            total_unfollowed = len([u for u in followed_users if isinstance(u, dict) and u.get('unfollowed', False)])
            
            # Count today's follows
            today = datetime.now().date()
            daily_follows = len([
                u for u in followed_users 
                if isinstance(u, dict) and 'followed_at' in u
                and datetime.fromisoformat(u['followed_at']).date() == today
            ])
            
            # Count pending unfollows (followed >48h ago, not unfollowed)
            cutoff_time = datetime.now() - timedelta(hours=48)
            pending_unfollows = len([
                u for u in followed_users
                if isinstance(u, dict) and 'followed_at' in u and not u.get('unfollowed', False)
                and datetime.fromisoformat(u['followed_at']) <= cutoff_time
            ])
            
            stats.update({
                'total_followed': total_followed,
                'total_unfollowed': total_unfollowed,
                'daily_follows': daily_follows,
                'pending_unfollows': pending_unfollows,
                'success_rate': round((total_followed / max(1, total_followed + total_unfollowed)) * 100, 1)
            })
            
        return stats
        
    def get_logs(self, lines=50):
        """Get recent log entries"""
        log_file = Path('instagram_data/logs/scheduler.log')
        if not log_file.exists():
            return []
            
        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                return [line.strip() for line in log_lines[-lines:]]
        except:
            return []

dashboard_api = DashboardAPI()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get current status"""
    status = dashboard_api.get_status()
    config = dashboard_api.get_config()
    stats = dashboard_api.get_stats()
    
    return jsonify({
        'status': status,
        'config': config,
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    lines = request.args.get('lines', 50, type=int)
    logs = dashboard_api.get_logs(lines)
    return jsonify({'logs': logs})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'POST':
        new_config = request.get_json()
        dashboard_api.save_config(new_config)
        return jsonify({'success': True})
    else:
        config = dashboard_api.get_config()
        return jsonify(config)

@app.route('/api/control/<action>')
def api_control(action):
    """Control the scheduler service"""
    try:
        if action == 'start':
            # Start the scheduler in background
            subprocess.Popen(['python3', 'instagram_scheduler.py'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           preexec_fn=os.setsid)
            return jsonify({'success': True, 'message': 'Scheduler started'})
            
        elif action == 'stop':
            # Try to stop gracefully
            status = dashboard_api.get_status()
            if 'pid' in status:
                try:
                    os.kill(status['pid'], signal.SIGTERM)
                except:
                    pass
            return jsonify({'success': True, 'message': 'Stop signal sent'})
            
        elif action == 'restart':
            # Stop and start
            api_control('stop')
            import time
            time.sleep(2)
            api_control('start')
            return jsonify({'success': True, 'message': 'Scheduler restarted'})
            
        else:
            return jsonify({'success': False, 'message': 'Unknown action'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/setup')
def setup():
    """Setup page"""
    return render_template('setup.html')

if __name__ == '__main__':
    # Create templates directory and files
    os.makedirs('templates', exist_ok=True)
    
    # Create dashboard HTML template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Automation Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #333; margin-bottom: 10px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #667eea; }
        .stat-card .label { color: #666; font-size: 14px; }
        .controls { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .controls h3 { margin-bottom: 15px; color: #333; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.running { background: #d4edda; color: #155724; }
        .status.stopped { background: #f8d7da; color: #721c24; }
        .logs { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .logs h3 { margin-bottom: 15px; color: #333; }
        .log-container { background: #f8f9fa; padding: 15px; border-radius: 5px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        .config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .config-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        @media (max-width: 768px) { .config-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Instagram Automation Dashboard</h1>
            <p>24/7 Automated Following & Unfollowing Service</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 Daily Follows</h3>
                <div class="value" id="daily-follows">-</div>
                <div class="label">Today</div>
            </div>
            <div class="stat-card">
                <h3>👥 Total Followed</h3>
                <div class="value" id="total-followed">-</div>
                <div class="label">All time</div>
            </div>
            <div class="stat-card">
                <h3>🔄 Pending Unfollows</h3>
                <div class="value" id="pending-unfollows">-</div>
                <div class="label">Ready (48h+)</div>
            </div>
            <div class="stat-card">
                <h3>✅ Success Rate</h3>
                <div class="value" id="success-rate">-</div>
                <div class="label">Percentage</div>
            </div>
        </div>
        
        <div class="controls">
            <h3>🎮 Service Controls</h3>
            <div class="status" id="service-status">Checking status...</div>
            <button class="btn btn-success" onclick="controlService('start')">▶️ Start</button>
            <button class="btn btn-danger" onclick="controlService('stop')">⏹️ Stop</button>
            <button class="btn btn-primary" onclick="controlService('restart')">🔄 Restart</button>
            <button class="btn btn-primary" onclick="refreshData()">🔄 Refresh</button>
        </div>
        
        <div class="config-grid">
            <div class="config-card">
                <h3>⚙️ Configuration</h3>
                <div id="config-display">Loading...</div>
            </div>
            <div class="config-card">
                <h3>📋 Schedule</h3>
                <div id="schedule-display">Loading...</div>
            </div>
        </div>
        
        <div class="logs">
            <h3>📝 Recent Logs</h3>
            <div class="log-container" id="logs">Loading logs...</div>
        </div>
    </div>

    <script>
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update stats
                document.getElementById('daily-follows').textContent = data.stats.daily_follows;
                document.getElementById('total-followed').textContent = data.stats.total_followed;
                document.getElementById('pending-unfollows').textContent = data.stats.pending_unfollows;
                document.getElementById('success-rate').textContent = data.stats.success_rate + '%';
                
                // Update status
                const statusEl = document.getElementById('service-status');
                const status = data.status.status || 'unknown';
                statusEl.textContent = '🤖 Service Status: ' + status.toUpperCase();
                statusEl.className = 'status ' + status;
                
                // Update config
                const config = data.config;
                document.getElementById('config-display').innerHTML = `
                    <p><strong>Daily Limit:</strong> ${config.daily_follow_limit || 'Not set'}</p>
                    <p><strong>Target Accounts:</strong> ${(config.target_accounts || []).length} configured</p>
                    <p><strong>Unfollow Delay:</strong> ${config.unfollow_delay_hours || 48} hours</p>
                    <p><strong>Enabled:</strong> ${config.enabled ? '✅' : '❌'}</p>
                `;
                
                // Update schedule
                document.getElementById('schedule-display').innerHTML = `
                    <p><strong>Follow Time:</strong> ${config.follow_schedule || 'Not set'}</p>
                    <p><strong>Unfollow Time:</strong> ${config.unfollow_schedule || 'Not set'}</p>
                    <p><strong>Last Follow:</strong> ${data.status.last_follow_job ? new Date(data.status.last_follow_job).toLocaleString() : 'Never'}</p>
                    <p><strong>Last Unfollow:</strong> ${data.status.last_unfollow_job ? new Date(data.status.last_unfollow_job).toLocaleString() : 'Never'}</p>
                `;
                
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        async function refreshLogs() {
            try {
                const response = await fetch('/api/logs?lines=100');
                const data = await response.json();
                const logsEl = document.getElementById('logs');
                logsEl.innerHTML = data.logs.join('\\n');
                logsEl.scrollTop = logsEl.scrollHeight;
            } catch (error) {
                console.error('Error refreshing logs:', error);
            }
        }
        
        async function controlService(action) {
            try {
                const response = await fetch(`/api/control/${action}`);
                const data = await response.json();
                alert(data.message);
                setTimeout(refreshData, 2000);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        setInterval(refreshLogs, 60000);
        
        // Initial load
        refreshData();
        refreshLogs();
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("🌐 Starting Instagram Automation Dashboard...")
    print("📱 Open http://localhost:5000 in your browser")
    print("🎮 Use the dashboard to monitor and control your automation")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 