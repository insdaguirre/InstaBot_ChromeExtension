#!/bin/bash

# Instagram Automation Service Setup Script
# Sets up 24/7 automation with web dashboard

echo "🤖 Instagram Automation Service Setup"
echo "====================================="

# Get current directory
CURRENT_DIR="$(pwd)"
USER_HOME="$HOME"
SERVICE_NAME="com.instagram.automation"
PLIST_FILE="$SERVICE_NAME.plist"
LAUNCH_AGENTS_DIR="$USER_HOME/Library/LaunchAgents"

echo "📁 Working directory: $CURRENT_DIR"

# 1. Install required Python packages
echo ""
echo "📦 Installing required packages..."
pip3 install schedule flask

# 2. Create directories
echo ""
echo "📁 Creating directories..."
mkdir -p instagram_data/logs
mkdir -p templates

# 3. Set up configuration
echo ""
echo "⚙️ Setting up configuration..."

# Create default scheduler config if it doesn't exist
if [ ! -f "scheduler_config.json" ]; then
    cat > scheduler_config.json << EOF
{
  "instagram_username": "",
  "instagram_password": "",
  "target_accounts": [
    "example_account1",
    "example_account2",
    "example_account3",
    "example_account4"
  ],
  "daily_follow_limit": 100,
  "followers_per_account": 50,
  "accounts_per_batch": 2,
  "unfollow_delay_hours": 48,
  "follow_schedule": "10:00",
  "unfollow_schedule": "22:00",
  "min_delay_between_follows": 30,
  "max_delay_between_follows": 120,
  "enabled": false
}
EOF
    echo "✅ Created default scheduler_config.json"
    echo "❗ IMPORTANT: Edit scheduler_config.json with your settings!"
else
    echo "✅ scheduler_config.json already exists"
fi

# 4. Update plist file with correct paths
echo ""
echo "🔧 Updating service configuration..."
sed "s|/Users/diegoaguirre/instagram automation|$CURRENT_DIR|g" "$PLIST_FILE" > "${PLIST_FILE}.tmp"
mv "${PLIST_FILE}.tmp" "$PLIST_FILE"
echo "✅ Updated paths in $PLIST_FILE"

# 5. Install the service
echo ""
echo "🚀 Installing service..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist file
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"
echo "✅ Copied service file to $LAUNCH_AGENTS_DIR"

# Make scripts executable
chmod +x instagram_scheduler.py
chmod +x web_dashboard.py
chmod +x cleanup_old_csvs.py

echo ""
echo "🎉 INSTALLATION COMPLETE!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣ CONFIGURE YOUR SETTINGS:"
echo "   📝 Edit scheduler_config.json with your Instagram credentials and target accounts"
echo "   🎯 Example: \"target_accounts\": [\"account1\", \"account2\", \"account3\", \"account4\"]"
echo ""
echo "2️⃣ START THE SERVICES:"
echo "   🤖 Scheduler: launchctl load ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "   🌐 Dashboard: python3 web_dashboard.py"
echo ""
echo "3️⃣ ACCESS THE DASHBOARD:"
echo "   🌐 Open http://localhost:5000 in your browser"
echo "   🎮 Use the web interface to monitor and control automation"
echo ""
echo "📊 SERVICE MANAGEMENT COMMANDS:"
echo "   ▶️  Start:   launchctl load ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "   ⏹️  Stop:    launchctl unload ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "   🔄 Restart: launchctl unload ~/Library/LaunchAgents/$SERVICE_NAME.plist && launchctl load ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "   📊 Status:  launchctl list | grep $SERVICE_NAME"
echo ""
echo "🗂️ IMPORTANT FILES:"
echo "   📝 Config:     scheduler_config.json"
echo "   📊 Status:     instagram_data/scheduler_status.json"
echo "   📜 Logs:       instagram_data/logs/"
echo "   💾 Data:       followed_users.json"
echo ""
echo "⚠️ AUTOMATION FEATURES:"
echo "   📈 Follows 100 people per day (configurable)"
echo "   🔄 Unfollows people after 48 hours (configurable)"
echo "   🎯 Cycles through target accounts automatically"
echo "   🌐 Web dashboard for monitoring and control"
echo "   🤖 Runs 24/7 as a background service"
echo ""

# Ask if user wants to start the dashboard now
read -p "🚀 Do you want to start the web dashboard now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Starting web dashboard..."
    echo "📱 Open http://localhost:5000 in your browser"
    echo "🛑 Press Ctrl+C to stop the dashboard"
    python3 web_dashboard.py
else
    echo "✅ Setup complete!"
    echo "🌐 Run 'python3 web_dashboard.py' to start the dashboard when ready"
    echo "🤖 Don't forget to configure scheduler_config.json and start the service!"
fi 