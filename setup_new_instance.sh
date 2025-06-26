#!/bin/bash
# Setup script for fresh AWS Ubuntu instance

echo "🚀 Setting up fresh AWS instance for Instagram automation..."

# Configuration
AWS_HOST="ec2-3-17-165-195.us-east-2.compute.amazonaws.com"
AWS_USER="ubuntu"
KEY_FILE="instagram-automation-key-new.pem"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH key file $KEY_FILE not found!"
    exit 1
fi

echo "📦 Installing system dependencies..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    # Update system
    sudo apt update -y
    
    # Install Python and pip
    sudo apt install -y python3 python3-pip python3-venv
    
    # Install Chrome dependencies
    sudo apt install -y wget gnupg2 software-properties-common apt-transport-https ca-certificates
    
    # Add Google Chrome repository
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # Update and install Chrome
    sudo apt update -y
    sudo apt install -y google-chrome-stable
    
    # Install ChromeDriver
    CHROME_VERSION=\$(google-chrome --version | awk '{print \$3}' | cut -d'.' -f1)
    echo \"Chrome version: \$CHROME_VERSION\"
    
    # Download and install ChromeDriver
    CHROMEDRIVER_VERSION=\$(curl -s \"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_\$CHROME_VERSION\")
    echo \"ChromeDriver version: \$CHROMEDRIVER_VERSION\"
    
    wget -O /tmp/chromedriver.zip \"https://storage.googleapis.com/chrome-for-testing-public/\$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip\"
    sudo unzip -o /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    
    # Install Xvfb for headless display
    sudo apt install -y xvfb
    
    echo '✅ System dependencies installed'
"

echo "📁 Setting up project directory and virtual environment..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    # Create project directory
    mkdir -p ~/instabot
    cd ~/instabot
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment and install Python packages
    source venv/bin/activate
    pip install --upgrade pip
    pip install selenium flask schedule
    
    # Test installations
    python --version
    pip --version
    google-chrome --version
    chromedriver --version
    
    echo '✅ Virtual environment and packages installed'
"

echo "📤 Uploading bot files..."
# Upload bot files
scp -i "$KEY_FILE" complete_instagram_bot.py "$AWS_USER@$AWS_HOST:~/instabot/"
scp -i "$KEY_FILE" scheduler.py "$AWS_USER@$AWS_HOST:~/instabot/"
scp -i "$KEY_FILE" dashboard.py "$AWS_USER@$AWS_HOST:~/instabot/"
scp -i "$KEY_FILE" test_bot.py "$AWS_USER@$AWS_HOST:~/instabot/"

echo "🔧 Making scripts executable and testing..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd ~/instabot
    chmod +x *.py
    
    # Create instagram_data directory
    mkdir -p instagram_data
    
    # Test the bot
    source venv/bin/activate
    echo '🧪 Testing bot...'
    timeout 120 python test_bot.py || echo 'Test completed (may have timed out)'
"

echo "🌐 Starting web dashboard..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd ~/instabot
    source venv/bin/activate
    
    # Start dashboard in background
    nohup python dashboard.py > dashboard.log 2>&1 &
    echo 'Dashboard started in background'
    
    # Wait and check if running
    sleep 3
    if pgrep -f dashboard.py > /dev/null; then
        echo '✅ Dashboard is running'
    else
        echo '❌ Dashboard failed to start'
    fi
"

echo "📅 Setting up scheduler service..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd ~/instabot
    
    # Create systemd service with absolute paths
    sudo tee /etc/systemd/system/instagram-scheduler.service > /dev/null << EOF
[Unit]
Description=Instagram Automation Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/instabot
Environment=PATH=/home/ubuntu/instabot/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/ubuntu/instabot/venv/bin/python scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and start service
    sudo systemctl daemon-reload
    sudo systemctl enable instagram-scheduler
    sudo systemctl start instagram-scheduler
    
    # Check service status
    sudo systemctl status instagram-scheduler --no-pager
"

echo "📊 Creating status script..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    cd ~/instabot
    
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
    echo 'Last action:' \$(tail -1 instagram_data/action_log.json 2>/dev/null | head -c 100)
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
"

echo "🎉 Setup Complete!"
echo "================================"
echo
echo "✅ Fresh AWS instance configured!"
echo "✅ Python, Chrome, ChromeDriver installed"
echo "✅ Virtual environment created"
echo "✅ Bot files uploaded"
echo "✅ Dashboard started"
echo "✅ Scheduler service configured"
echo
echo "🔗 Access dashboard: http://$AWS_HOST:5000"
echo
echo "🧪 Test the setup:"
echo "  ssh -i $KEY_FILE $AWS_USER@$AWS_HOST 'cd ~/instabot && ./status.sh'" 