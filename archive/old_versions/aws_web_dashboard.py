#!/usr/bin/env python3
"""
AWS Instagram Automation Dashboard
Optimized for EC2 t2.micro instances
"""

from flask import Flask, render_template_string, jsonify
import psutil
import json
import os
import subprocess
import requests
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Instagram Automation Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status-running { color: #27ae60; font-weight: bold; }
        .status-stopped { color: #e74c3c; font-weight: bold; }
        .metric { font-size: 2em; font-weight: bold; color: #f39c12; }
        .aws-badge { background: #ff9900; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        button { background: #ff9900; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #e68900; }
        .log-box { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; height: 300px; overflow-y: scroll; font-family: monospace; }
        h1 { color: #2c3e50; text-align: center; }
        h2 { color: #34495e; border-bottom: 2px solid #ff9900; padding-bottom: 10px; }
        .aws-info { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🟡 AWS Instagram Automation Dashboard</h1>
        <p style="text-align: center; color: #7f8c8d;">
            <span class="aws-badge">AWS EC2</span> • Migration-Ready • Cost-Optimized
        </p>
        
        <div class="aws-info">
            <h3>🔄 Migration Strategy:</h3>
            <p><strong>Year 1:</strong> Free on AWS (12 months) → <strong>Year 2:</strong> Move to Google Cloud (12 months free) → <strong>Year 3:</strong> Move to Azure (12 months free)</p>
            <p>Total cost for 3 years: <strong>$0</strong> | Migration time: <strong>15 minutes per year</strong></p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>🤖 Service Status</h2>
                <div id="service-status">Loading...</div>
            </div>
            
            <div class="card">
                <h2>📊 AWS Resources</h2>
                <div id="system-stats">Loading...</div>
            </div>
            
            <div class="card">
                <h2>📈 Today's Progress</h2>
                <div id="progress">Loading...</div>
            </div>
            
            <div class="card">
                <h2>⚙️ Configuration</h2>
                <div id="config-info">Loading...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📝 Live Logs</h2>
            <div class="log-box" id="logs">Loading logs...</div>
        </div>
        
        <div class="card" style="text-align: center;">
            <h2>🔧 Controls</h2>
            <button onclick="controlService('start')">▶️ Start</button>
            <button onclick="controlService('stop')">⏹️ Stop</button>
            <button onclick="controlService('restart')">🔄 Restart</button>
            <button onclick="refreshData()">🔄 Refresh</button>
            <button onclick="createBackup()">💾 Backup</button>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('service-status').innerHTML = data.services;
                    document.getElementById('system-stats').innerHTML = data.system;
                    document.getElementById('progress').innerHTML = data.progress;
                    document.getElementById('config-info').innerHTML = data.config;
                });
            
            fetch('/api/logs')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('logs').innerHTML = data;
                    document.getElementById('logs').scrollTop = document.getElementById('logs').scrollHeight;
                });
        }
        
        function controlService(action) {
            fetch('/api/control/' + action, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    setTimeout(refreshData, 2000);
                });
        }
        
        function createBackup() {
            fetch('/api/backup', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Backup created: ' + data.filename);
                });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
"""

def get_aws_metadata():
    """Get AWS EC2 metadata"""
    try:
        metadata = {}
        metadata['instance_id'] = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id', timeout=2
        ).text
        metadata['instance_type'] = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-type', timeout=2
        ).text
        metadata['availability_zone'] = requests.get(
            'http://169.254.169.254/latest/meta-data/placement/availability-zone', timeout=2
        ).text
        metadata['public_ipv4'] = requests.get(
            'http://169.254.169.254/latest/meta-data/public-ipv4', timeout=2
        ).text
        return metadata
    except:
        return {'instance_id': 'unknown', 'instance_type': 'unknown', 'availability_zone': 'unknown', 'public_ipv4': 'localhost'}

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    # Check if processes are running
    automation_running = os.path.exists('automation.pid')
    dashboard_running = os.path.exists('dashboard.pid')
    
    if automation_running:
        try:
            with open('automation.pid', 'r') as f:
                pid = int(f.read().strip())
            automation_running = psutil.pid_exists(pid)
        except:
            automation_running = False
    
    # System stats
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # AWS metadata
    aws_metadata = get_aws_metadata()
    
    return jsonify({
        'services': f"""
            <p>🤖 Automation: <span class="status-{'running' if automation_running else 'stopped'}">
                {'Running' if automation_running else 'Stopped'}
            </span></p>
            <p>📊 Dashboard: <span class="status-running">Running</span></p>
            <p>🌐 Public IP: <a href="http://{aws_metadata['public_ipv4']}:5000">{aws_metadata['public_ipv4']}:5000</a></p>
        """,
        'system': f"""
            <p>💾 Memory: {memory.percent:.1f}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)</p>
            <p>💻 CPU: {cpu_percent:.1f}%</p>
            <p>💽 Disk: {disk.percent:.1f}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)</p>
            <p>🏷️ Instance: {aws_metadata['instance_type']}</p>
            <p>🌍 Zone: {aws_metadata['availability_zone']}</p>
            <p>🆔 ID: {aws_metadata['instance_id'][:8]}...</p>
        """,
        'progress': f"""
            <p class="metric">0</p>
            <p>Follows Today</p>
            <p>Next action: Check logs for schedule</p>
            <p style="color: #f39c12;">💰 Current cost: <strong>$0/month</strong> (Free tier)</p>
        """,
        'config': f"""
            <p>🎯 Target Accounts: See config/automation_config.json</p>
            <p>📅 Schedule: 10:00 AM follows, 10:00 PM unfollows</p>
            <p>🔢 Daily Limit: 100 follows</p>
            <p>☁️ Provider: AWS EC2 (Year 1 free)</p>
            <p>🚛 Status: Migration-ready</p>
        """
    })

@app.route('/api/logs')
def api_logs():
    try:
        with open('logs/aws_automation.log', 'r') as f:
            lines = f.readlines()
            # Get last 50 lines
            recent_lines = lines[-50:] if len(lines) > 50 else lines
            return '<br>'.join([line.strip() for line in recent_lines])
    except:
        return "No AWS logs available yet"

@app.route('/api/control/<action>', methods=['POST'])
def api_control(action):
    try:
        result = subprocess.run(['./scripts/control.sh', action], 
                              capture_output=True, text=True)
        return jsonify({'message': f'AWS action {action} completed', 'output': result.stdout})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'})

@app.route('/api/backup', methods=['POST'])
def api_backup():
    try:
        result = subprocess.run(['./scripts/backup.sh'], 
                              capture_output=True, text=True)
        filename = "aws_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".tar.gz"
        return jsonify({'message': 'Backup created successfully', 'filename': filename})
    except Exception as e:
        return jsonify({'message': f'Backup failed: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 