#!/bin/bash

# Instagram Automation Service Control Script
# Easy management of the 24/7 automation service

SERVICE_NAME="com.instagram.automation"
PLIST_PATH="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"

case "$1" in
    start)
        echo "🚀 Starting Instagram Automation Service..."
        launchctl load "$PLIST_PATH"
        echo "✅ Service started!"
        echo "🌐 Start dashboard with: python3 web_dashboard.py"
        ;;
    stop)
        echo "🛑 Stopping Instagram Automation Service..."
        launchctl unload "$PLIST_PATH"
        echo "✅ Service stopped!"
        ;;
    restart)
        echo "🔄 Restarting Instagram Automation Service..."
        launchctl unload "$PLIST_PATH"
        sleep 2
        launchctl load "$PLIST_PATH"
        echo "✅ Service restarted!"
        ;;
    status)
        echo "📊 Instagram Automation Service Status:"
        if launchctl list | grep -q "$SERVICE_NAME"; then
            echo "✅ Service is RUNNING"
            launchctl list | grep "$SERVICE_NAME"
        else
            echo "❌ Service is STOPPED"
        fi
        
        # Show scheduler status if available
        if [ -f "instagram_data/scheduler_status.json" ]; then
            echo ""
            echo "📋 Scheduler Status:"
            python3 -c "
import json
with open('instagram_data/scheduler_status.json', 'r') as f:
    status = json.load(f)
    print(f\"Status: {status.get('status', 'unknown')}\")
    print(f\"Daily Follows: {status.get('daily_follows_count', 0)}\")
    print(f\"Last Follow Job: {status.get('last_follow_job', 'Never')}\")
    print(f\"Last Unfollow Job: {status.get('last_unfollow_job', 'Never')}\")
"
        fi
        ;;
    dashboard)
        echo "🌐 Starting Web Dashboard..."
        echo "📱 Open http://localhost:5000 in your browser"
        echo "🛑 Press Ctrl+C to stop"
        python3 web_dashboard.py
        ;;
    logs)
        echo "📜 Recent Logs:"
        if [ -f "instagram_data/logs/scheduler.log" ]; then
            tail -20 "instagram_data/logs/scheduler.log"
        else
            echo "No logs found"
        fi
        ;;
    config)
        echo "⚙️ Opening configuration file..."
        if command -v code &> /dev/null; then
            code scheduler_config.json
        elif command -v nano &> /dev/null; then
            nano scheduler_config.json
        else
            echo "📝 Edit scheduler_config.json with your preferred editor"
        fi
        ;;
    *)
        echo "🤖 Instagram Automation Service Control"
        echo "Usage: $0 {start|stop|restart|status|dashboard|logs|config}"
        echo ""
        echo "Commands:"
        echo "  start      - Start the automation service"
        echo "  stop       - Stop the automation service"
        echo "  restart    - Restart the automation service"
        echo "  status     - Show service status"
        echo "  dashboard  - Start web dashboard"
        echo "  logs       - Show recent logs"
        echo "  config     - Edit configuration"
        echo ""
        echo "Examples:"
        echo "  ./service_control.sh start"
        echo "  ./service_control.sh dashboard"
        echo "  ./service_control.sh status"
        ;;
esac 