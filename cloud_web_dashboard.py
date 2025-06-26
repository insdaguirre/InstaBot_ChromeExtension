#!/usr/bin/env python3
"""
Cloud Web Dashboard for Instagram Automation
Lightweight monitoring interface for Oracle Cloud Free Tier
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, redirect, url_for

app = Flask(__name__)

# HTML Template for dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Instagram Automation Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .status-item:last-child { border-bottom: none; }
        .status-value {
            font-weight: 600;
            color: #333;
        }
        .status-good { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
            margin: 30px 0;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        .btn-success {
            background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            color: white;
        }
        .btn-danger {
            background: linear-gradient(45deg, #cb2d3e, #ef473a);
            color: white;
        }
        .btn-warning {
            background: linear-gradient(45deg, #f7971e, #ffd200);
            color: #333;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .log-container {
            background: #1a1a1a;
            border-radius: 15px;
            padding: 20px;
            margin-top: 30px;
            max-height: 400px;
            overflow-y: auto;
        }
        .log-header {
            color: #fff;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        .log-content {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            color: #00ff00;
            white-space: pre-wrap;
        }
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .emoji { font-size: 1.2em; }
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .status-grid { grid-template-columns: 1fr; }
            .controls { flex-direction: column; align-items: center; }
            .btn { width: 200px; text-align: center; }
        }
    </style>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
        
        function updateCountdown() {
            const now = new Date().getTime();
            const nextRefresh = now + 30000;
            
            setInterval(() => {
                const timeLeft = Math.max(0, Math.floor((nextRefresh - new Date().getTime()) / 1000));
                document.getElementById('countdown').textContent = timeLeft;
            }, 1000);
        }
        
        window.onload = updateCountdown;
    </script>
</head>
<body>
    <div class="auto-refresh">
        🔄 Auto-refresh in <span id="countdown">30</span>s
    </div>
    
    <div class="container">
        <div class="header">
            <h1><span class="emoji">☁️</span> Cloud Instagram Automation</h1>
            <p>Oracle Cloud Free Tier Dashboard</p>
        </div>
        
        <div class="status-grid">
            <div class="card">
                <h3><span class="emoji">🤖</span> Service Status</h3>
                <div class="status-item">
                    <span>Service Status:</span>
                    <span class="status-value {{ 'status-good' if status.get('status') == 'running' else 'status-error' }}">
                        {{ status.get('status', 'Unknown').title() }}
                    </span>
                </div>
                <div class="status-item">
                    <span>Started:</span>
                    <span class="status-value">{{ status.get('started_at', 'N/A')[:19] if status.get('started_at') else 'N/A' }}</span>
                </div>
                <div class="status-item">
                    <span>Last Update:</span>
                    <span class="status-value">{{ status.get('last_update', 'N/A')[:19] if status.get('last_update') else 'N/A' }}</span>
                </div>
                <div class="status-item">
                    <span>Process ID:</span>
                    <span class="status-value">{{ status.get('pid', 'N/A') }}</span>
                </div>
            </div>
            
            <div class="card">
                <h3><span class="emoji">📊</span> Daily Progress</h3>
                <div class="status-item">
                    <span>Today's Follows:</span>
                    <span class="status-value status-good">{{ status.get('daily_follows_count', 0) }}/{{ config.get('daily_follow_limit', 100) }}</span>
                </div>
                <div class="status-item">
                    <span>Last Follow Job:</span>
                    <span class="status-value">{{ status.get('last_follow_job', 'N/A')[:19] if status.get('last_follow_job') else 'N/A' }}</span>
                </div>
                <div class="status-item">
                    <span>Last Unfollow Job:</span>
                    <span class="status-value">{{ status.get('last_unfollow_job', 'N/A')[:19] if status.get('last_unfollow_job') else 'N/A' }}</span>
                </div>
                <div class="status-item">
                    <span>Follow Schedule:</span>
                    <span class="status-value">{{ config.get('follow_schedule', '10:00') }} daily</span>
                </div>
            </div>
            
            <div class="card">
                <h3><span class="emoji">💻</span> System Resources</h3>
                <div class="status-item">
                    <span>Memory Available:</span>
                    <span class="status-value {{ 'status-good' if status.get('memory_available', 0) > 300 else 'status-warning' if status.get('memory_available', 0) > 200 else 'status-error' }}">
                        {{ status.get('memory_available', 'N/A') }} MB
                    </span>
                </div>
                <div class="status-item">
                    <span>Disk Usage:</span>
                    <span class="status-value {{ 'status-good' if status.get('disk_usage', 0) < 70 else 'status-warning' if status.get('disk_usage', 0) < 85 else 'status-error' }}">
                        {{ status.get('disk_usage', 'N/A') }}%
                    </span>
                </div>
                <div class="status-item">
                    <span>Last Health Check:</span>
                    <span class="status-value">{{ status.get('health_check', 'N/A')[:19] if status.get('health_check') else 'N/A' }}</span>
                </div>
                <div class="status-item">
                    <span>Cloud Mode:</span>
                    <span class="status-value status-good">{{ 'Enabled' if config.get('cloud_mode') else 'Disabled' }}</span>
                </div>
            </div>
            
            <div class="card">
                <h3><span class="emoji">⚙️</span> Configuration</h3>
                <div class="status-item">
                    <span>Target Accounts:</span>
                    <span class="status-value">{{ config.get('target_accounts', [])|length }}</span>
                </div>
                <div class="status-item">
                    <span>Users per Account:</span>
                    <span class="status-value">{{ config.get('followers_per_account', 25) }}</span>
                </div>
                <div class="status-item">
                    <span>Unfollow Delay:</span>
                    <span class="status-value">{{ config.get('unfollow_delay_hours', 48) }} hours</span>
                </div>
                <div class="status-item">
                    <span>Automation:</span>
                    <span class="status-value {{ 'status-good' if config.get('enabled') else 'status-error' }}">
                        {{ 'Enabled' if config.get('enabled') else 'Disabled' }}
                    </span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <a href="/start" class="btn btn-success">▶️ Start Service</a>
            <a href="/stop" class="btn btn-danger">⏹️ Stop Service</a>
            <a href="/restart" class="btn btn-warning">🔄 Restart Service</a>
            <a href="/test" class="btn btn-primary">🧪 Test Run</a>
            <a href="/status" class="btn btn-primary">📋 Raw Status</a>
        </div>
        
        <div class="log-container">
            <div class="log-header">📝 Recent Logs (Last 50 lines)</div>
            <div class="log-content">{{ logs }}</div>
        </div>
    </div>
</body>
</html>
"""

class CloudDashboard:
    def __init__(self):
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        
    def get_status(self):
        """Get current service status"""
        status_file = self.data_dir / 'cloud_status.json'
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def get_config(self):
        """Get current configuration"""
        config_file = Path('cloud_config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def get_logs(self, lines=50):
        """Get recent log entries"""
        log_file = self.data_dir / 'logs' / 'cloud_scheduler.log'
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    return ''.join(recent_lines)
            except:
                pass
        return "No logs available"
        
    def is_service_running(self):
        """Check if the scheduler service is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'cloud_scheduler.py'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
            
    def start_service(self):
        """Start the cloud scheduler service"""
        try:
            if not self.is_service_running():
                subprocess.Popen([
                    'python3', 'cloud_scheduler.py'
                ], cwd=os.getcwd())
                return True, "Service started successfully"
            else:
                return False, "Service is already running"
        except Exception as e:
            return False, f"Error starting service: {e}"
            
    def stop_service(self):
        """Stop the cloud scheduler service"""
        try:
            result = subprocess.run(['pkill', '-f', 'cloud_scheduler.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Service stopped successfully"
            else:
                return False, "Service was not running"
        except Exception as e:
            return False, f"Error stopping service: {e}"
            
    def restart_service(self):
        """Restart the cloud scheduler service"""
        stop_success, stop_msg = self.stop_service()
        import time
        time.sleep(2)  # Wait for graceful shutdown
        start_success, start_msg = self.start_service()
        
        if start_success:
            return True, "Service restarted successfully"
        else:
            return False, f"Restart failed: {start_msg}"

# Initialize dashboard
dashboard = CloudDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    status = dashboard.get_status()
    config = dashboard.get_config()
    logs = dashboard.get_logs()
    
    return render_template_string(DASHBOARD_HTML, 
                                status=status, 
                                config=config, 
                                logs=logs)

@app.route('/status')
def status():
    """Return raw status as JSON"""
    return jsonify({
        'status': dashboard.get_status(),
        'config': dashboard.get_config(),
        'service_running': dashboard.is_service_running(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/start')
def start():
    """Start the service"""
    success, message = dashboard.start_service()
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    """Stop the service"""
    success, message = dashboard.stop_service()
    return redirect(url_for('index'))

@app.route('/restart')
def restart():
    """Restart the service"""
    success, message = dashboard.restart_service()
    return redirect(url_for('index'))

@app.route('/test')
def test():
    """Run a test follow job"""
    try:
        subprocess.Popen(['python3', 'cloud_scheduler.py', 'test'])
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error running test: {e}"

@app.route('/api/logs')
def api_logs():
    """API endpoint for logs"""
    lines = request.args.get('lines', 50, type=int)
    return jsonify({
        'logs': dashboard.get_logs(lines),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Run with Waitress for production
    try:
        from waitress import serve
        print("🌐 Starting Cloud Dashboard on http://localhost:5000")
        print("📊 Dashboard ready for Oracle Cloud monitoring")
        serve(app, host='0.0.0.0', port=5000, threads=2)
    except ImportError:
        # Fallback to Flask dev server
        print("⚠️ Waitress not available, using Flask dev server")
        app.run(host='0.0.0.0', port=5000, debug=False) 