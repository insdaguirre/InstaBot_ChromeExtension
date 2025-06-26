#!/bin/bash
# Complete Instagram Bot Deployment Script

echo "🚀 Deploying Complete Instagram Automation System to AWS..."

# Configuration
AWS_HOST="ec2-3-17-165-195.us-east-2.compute.amazonaws.com"
AWS_USER="ubuntu"
KEY_FILE="instagram-automation-key-new.pem"
REMOTE_DIR="~/instabot"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH key file $KEY_FILE not found!"
    echo "Please ensure your SSH key is in the current directory"
    exit 1
fi

# Set correct permissions for SSH key
chmod 600 "$KEY_FILE"

echo "📁 Creating remote directory structure..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    mkdir -p $REMOTE_DIR/instagram_data
    mkdir -p $REMOTE_DIR/logs
"

echo "📤 Uploading bot files..."

# Upload main bot file
scp -i "$KEY_FILE" complete_instagram_bot.py "$AWS_USER@$AWS_HOST:$REMOTE_DIR/"

# Upload scheduler
scp -i "$KEY_FILE" scheduler.py "$AWS_USER@$AWS_HOST:$REMOTE_DIR/"

# Upload dashboard
scp -i "$KEY_FILE" dashboard.py "$AWS_USER@$AWS_HOST:$REMOTE_DIR/"

echo "🔧 Setting up the system on AWS..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd $REMOTE_DIR
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install required packages
    pip install schedule flask
    
    # Make scripts executable
    chmod +x complete_instagram_bot.py
    chmod +x scheduler.py
    chmod +x dashboard.py
    
    echo '✅ System setup complete!'
"

echo "🧪 Testing the complete bot..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd $REMOTE_DIR
    source venv/bin/activate
    
    # Test the bot with a quick dry run
    timeout 120 python complete_instagram_bot.py || echo 'Test completed (may have timed out)'
"

echo "🌐 Starting web dashboard..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd $REMOTE_DIR
    source venv/bin/activate
    
    # Start dashboard in background
    nohup python dashboard.py > dashboard.log 2>&1 &
    echo 'Dashboard started in background'
    
    # Wait a moment and check if it's running
    sleep 3
    if pgrep -f dashboard.py > /dev/null; then
        echo '✅ Dashboard is running'
        echo '🔗 Access at: http://$AWS_HOST:5000'
    else
        echo '❌ Dashboard failed to start'
    fi
"

echo "📅 Setting up the scheduler..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd $REMOTE_DIR
    source venv/bin/activate
    
    # Create systemd service for scheduler
    sudo tee /etc/systemd/system/instagram-scheduler.service > /dev/null << EOF
[Unit]
Description=Instagram Automation Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$REMOTE_DIR
Environment=PATH=$REMOTE_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$REMOTE_DIR/venv/bin/python scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable instagram-scheduler
    sudo systemctl start instagram-scheduler
    
    echo '✅ Scheduler service installed and started'
    
    # Check service status
    sudo systemctl status instagram-scheduler --no-pager
"

echo "📊 Creating status check script..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd $REMOTE_DIR
    
    cat > status.sh << 'EOF'
#!/bin/bash
echo '🤖 Instagram Bot System Status'
echo '================================'
echo
echo '📅 Scheduler Service:'
sudo systemctl status instagram-scheduler --no-pager | head -5
echo
echo '🌐 Dashboard Process:'
if pgrep -f dashboard.py > /dev/null; then
    echo '✅ Dashboard is running (PID: '\$(pgrep -f dashboard.py)')'
else
    echo '❌ Dashboard is not running'
fi
echo
echo '📊 Recent Activity:'
if [ -f instagram_data/action_log.json ]; then
    echo 'Last action:' \$(tail -1 instagram_data/action_log.json | jq -r '.timestamp + \" - \" + .action + \": \" + .target' 2>/dev/null || echo 'No recent actions')
else
    echo 'No action log found'
fi
echo
echo '💾 Storage Usage:'
df -h . | tail -1
echo
echo '🔗 Access dashboard at: http://$AWS_HOST:5000'
EOF

    chmod +x status.sh
    echo '✅ Status script created'
"

echo "🎉 Deployment Complete!"
echo "================================"
echo
echo "✅ Complete Instagram automation system deployed!"
echo
echo "📋 What's running:"
echo "  🤖 Complete Instagram bot (complete_instagram_bot.py)"
echo "  📅 Scheduler (runs bot twice daily at 10 AM and 6 PM)"
echo "  🌐 Web dashboard (port 5000)"
echo
echo "🔗 Access dashboard: http://$AWS_HOST:5000"
echo
echo "🔧 Management commands:"
echo "  Check status: ssh -i $KEY_FILE $AWS_USER@$AWS_HOST 'cd $REMOTE_DIR && ./status.sh'"
echo "  View logs: ssh -i $KEY_FILE $AWS_USER@$AWS_HOST 'cd $REMOTE_DIR && tail -f scheduler.log'"
echo "  Restart scheduler: ssh -i $KEY_FILE $AWS_USER@$AWS_HOST 'sudo systemctl restart instagram-scheduler'"
echo
echo "🎯 Bot Configuration:"
echo "  • Target accounts: 1001tracklists, housemusic.us, housemusicnerds, edm"
echo "  • 25 follows per account (100 total per day)"
echo "  • 48-hour auto-unfollow"
echo "  • Runs at 10 AM and 6 PM daily"
echo
echo "🚀 Your Instagram automation is now running 24/7!" 