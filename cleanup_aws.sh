#!/bin/bash
# AWS Cleanup Script - Removes old problematic files

echo "🧹 Cleaning up AWS instance..."

# Configuration
AWS_HOST="ec2-3-17-165-195.us-east-2.compute.amazonaws.com"
AWS_USER="ubuntu"
KEY_FILE="instagram-automation-key-new.pem"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH key file $KEY_FILE not found!"
    echo "Please download it from AWS Console first"
    exit 1
fi

echo "🔌 Connecting to AWS and cleaning up..."
ssh -i "$KEY_FILE" "$AWS_USER@$AWS_HOST" "
    echo '🛑 Stopping all processes...'
    pkill -f python 2>/dev/null || echo 'No Python processes found'
    pkill -f instagram 2>/dev/null || echo 'No Instagram processes found'
    pkill -f chrome 2>/dev/null || echo 'No Chrome processes found'
    pkill -f chromedriver 2>/dev/null || echo 'No ChromeDriver processes found'
    
    echo '🗑️ Stopping services...'
    sudo systemctl stop instagram-scheduler 2>/dev/null || echo 'No scheduler service found'
    sudo systemctl disable instagram-scheduler 2>/dev/null || echo 'Service not enabled'
    sudo rm -f /etc/systemd/system/instagram-scheduler.service
    sudo systemctl daemon-reload
    
    echo '📁 Going to bot directory...'
    cd ~/instabot
    
    echo '💾 Backing up important data...'
    mkdir -p ~/backup/\$(date +%Y%m%d_%H%M%S)
    cp -r instagram_data ~/backup/\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'No data to backup'
    cp *.log ~/backup/\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo 'No logs to backup'
    
    echo '🗂️ Removing old bot files...'
    rm -f aws_instagram_bot.py
    rm -f working_instagram_bot.py
    rm -f instagram_bot.py
    rm -f test_*.py
    rm -f *.log
    rm -f scheduler.py
    rm -f dashboard.py
    rm -f web_dashboard.py
    rm -f cloud_*.py
    
    echo '🧽 Cleaning up temporary files...'
    rm -f *.pid
    rm -f nohup.out
    rm -f dashboard.log
    rm -f scheduler.log
    
    echo '📋 Current directory contents:'
    ls -la
    
    echo '🔍 Checking virtual environment...'
    source venv/bin/activate
    echo 'Python version:' \$(python --version)
    echo 'Virtual env path:' \$(which python)
    
    echo '✅ Cleanup complete!'
    echo '📊 Ready for new deployment'
"

echo "🎉 AWS cleanup finished!"
echo "✅ Old files removed"
echo "✅ Processes stopped"
echo "✅ Services disabled"
echo "✅ Data backed up"
echo ""
echo "🚀 Now run: ./deploy_complete_system.sh" 