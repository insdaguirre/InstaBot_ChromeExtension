#!/bin/bash
# AWS Ubuntu 22.04 Instagram Automation Deployment Script
# Adapted from Oracle Cloud deployment for AWS EC2

set -e

echo "🟡 AWS Instagram Automation Deployment"
echo "====================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}[STEP]${NC} $1"
    echo "----------------------------------------"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system
print_step "1. Updating system packages"
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python and pip
print_step "2. Installing Python and dependencies"
sudo apt-get install -y python3 python3-pip python3-venv git curl wget unzip

# Install Chrome and ChromeDriver (AWS Ubuntu 22.04 specific)
print_step "3. Installing Google Chrome and ChromeDriver"

# Install Chrome (AWS Ubuntu 22.04 method)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver using new method (Chrome 115+)
CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
print_status "Chrome version: $CHROME_VERSION"

# For Chrome 115+, use the new ChromeDriver API
MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d'.' -f1)
print_status "Chrome major version: $MAJOR_VERSION"

if [ "$MAJOR_VERSION" -ge 115 ]; then
    print_status "Using new ChromeDriver API for Chrome $MAJOR_VERSION"
    
    # Get the latest ChromeDriver version for this Chrome version
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$MAJOR_VERSION")
    
    if [ -z "$CHROMEDRIVER_VERSION" ] || [ "$CHROMEDRIVER_VERSION" = "Not Found" ]; then
        print_warning "ChromeDriver not found for Chrome $MAJOR_VERSION, using stable release"
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
    fi
    
    print_status "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"
    
    # Download from new location
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64
else
    print_status "Using legacy ChromeDriver API for Chrome $MAJOR_VERSION"
    # Fallback to old method for older Chrome versions
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$MAJOR_VERSION")
    print_status "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"
    
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    sudo mv /tmp/chromedriver /usr/local/bin/
    sudo chmod +x /usr/local/bin/chromedriver
    rm /tmp/chromedriver.zip
fi

# Verify ChromeDriver installation
print_status "ChromeDriver installed at: $(which chromedriver)"
print_status "ChromeDriver version: $(chromedriver --version)"

# Install Xvfb for virtual display
print_step "4. Installing virtual display support"
sudo apt-get install -y xvfb x11vnc

# Install system monitoring tools
print_step "5. Installing system monitoring tools"
sudo apt-get install -y htop iotop nethogs

# Create application directory
print_step "6. Setting up application directory"
APP_DIR="$HOME/instagram-automation"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Create directory structure
mkdir -p {config,logs,data,backups,scripts}

# Create virtual environment
print_step "7. Creating Python virtual environment"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
print_step "8. Installing Python dependencies"
cat > requirements.txt << 'EOF'
selenium==4.15.2
schedule==1.2.0
flask==2.3.3
waitress==2.1.2
psutil==5.9.6
requests==2.31.0
python-dotenv==1.0.0
jsonschema==4.17.3
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Create AWS-optimized configuration file
print_step "9. Creating AWS configuration file"
cat > config/automation_config.json << 'EOF'
{
  "provider": "AWS",
  "target_accounts": [
    "target_account_1",
    "target_account_2",
    "target_account_3",
    "target_account_4"
  ],
  "settings": {
    "daily_follow_limit": 100,
    "followers_per_account": 25,
    "unfollow_delay_hours": 48,
    "batch_size": 4,
    "retry_attempts": 3,
    "rate_limiting": {
      "min_delay_seconds": 15,
      "max_delay_seconds": 45,
      "pause_on_error_minutes": 30
    }
  },
  "schedule": {
    "follow_time": "10:00",
    "unfollow_time": "22:00",
    "timezone": "UTC"
  },
  "browser": {
    "headless": true,
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "window_size": "1920,1080"
  },
  "aws_specific": {
    "instance_type": "t2.micro",
    "region": "us-east-1",
    "memory_limit_mb": 1024
  }
}
EOF

# Create environment file template
print_step "10. Creating environment configuration"
cat > .env << 'EOF'
# Instagram Automation Configuration for AWS
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
DAILY_FOLLOW_LIMIT=100
FOLLOWERS_PER_ACCOUNT=25
FOLLOW_SCHEDULE=10:00
UNFOLLOW_SCHEDULE=22:00
MIN_DELAY=15
MAX_DELAY=45
HEADLESS=true
CLOUD_PROVIDER=AWS
AWS_REGION=us-east-1
EOF

# Create control scripts
print_step "11. Creating management scripts"

cat > scripts/control.sh << 'EOF'
#!/bin/bash
# AWS Instagram Automation Control Script

APP_DIR="$HOME/instagram-automation"
VENV_PATH="$APP_DIR/venv"

case "$1" in
    start)
        echo "🚀 Starting AWS Instagram Automation..."
        cd "$APP_DIR"
        source "$VENV_PATH/bin/activate"
        
        # Start virtual display
        export DISPLAY=:99
        Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
        XVFB_PID=$!
        echo $XVFB_PID > xvfb.pid
        sleep 2
        
        # Start automation in background
        nohup python aws_instagram_bot.py > logs/automation.log 2>&1 &
        echo $! > automation.pid
        
        # Start dashboard in background
        nohup python aws_web_dashboard.py > logs/dashboard.log 2>&1 &
        echo $! > dashboard.pid
        
        echo "✅ Services started on AWS"
        echo "📊 Dashboard: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
        ;;
    stop)
        echo "🛑 Stopping AWS Instagram Automation..."
        cd "$APP_DIR"
        
        # Kill processes using PID files
        [ -f automation.pid ] && kill $(cat automation.pid) 2>/dev/null && rm automation.pid
        [ -f dashboard.pid ] && kill $(cat dashboard.pid) 2>/dev/null && rm dashboard.pid
        [ -f xvfb.pid ] && kill $(cat xvfb.pid) 2>/dev/null && rm xvfb.pid
        
        echo "✅ Services stopped"
        ;;
    restart)
        $0 stop
        sleep 3
        $0 start
        ;;
    status)
        echo "📊 AWS Service Status:"
        cd "$APP_DIR"
        
        if [ -f automation.pid ] && kill -0 $(cat automation.pid) 2>/dev/null; then
            echo "✅ Automation: Running (PID: $(cat automation.pid))"
        else
            echo "❌ Automation: Stopped"
        fi
        
        if [ -f dashboard.pid ] && kill -0 $(cat dashboard.pid) 2>/dev/null; then
            echo "✅ Dashboard: Running (PID: $(cat dashboard.pid))"
        else
            echo "❌ Dashboard: Stopped"
        fi
        
        if [ -f xvfb.pid ] && kill -0 $(cat xvfb.pid) 2>/dev/null; then
            echo "✅ Virtual Display: Running (PID: $(cat xvfb.pid))"
        else
            echo "❌ Virtual Display: Stopped"
        fi
        
        echo "🌐 Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'Not available')"
        ;;
    logs)
        echo "📝 Recent AWS Logs:"
        cd "$APP_DIR"
        tail -f logs/*.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
EOF

# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# AWS Backup Script

APP_DIR="$HOME/instagram-automation"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
AWS_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//')

echo "💾 Creating AWS backup..."
mkdir -p "$BACKUP_DIR"

# Create backup archive
tar -czf "$BACKUP_DIR/aws_backup_$TIMESTAMP.tar.gz" \
    -C "$APP_DIR" \
    config/ \
    data/ \
    .env \
    requirements.txt \
    *.py 2>/dev/null

echo "✅ AWS backup created: aws_backup_$TIMESTAMP.tar.gz"
echo "📁 Location: $BACKUP_DIR/"
echo "🌐 Region: $AWS_REGION"

# Keep only last 5 backups
cd "$BACKUP_DIR"
ls -t aws_backup_*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null || true

echo "🧹 Old backups cleaned up"
EOF

# Make scripts executable
chmod +x scripts/*.sh

# Create initial log files
print_step "12. Setting up logging"
touch logs/automation.log logs/dashboard.log

print_step "13. Final setup"
deactivate

# Print completion message
echo ""
echo "🎉 AWS Instagram Automation Setup Complete!"
echo "==========================================="
echo ""
echo "📁 Installation Location: $APP_DIR"
echo "🖥️  Cloud Provider: AWS EC2"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your Instagram bot files:"
echo "   cp cloud_instagram_bot.py $APP_DIR/aws_instagram_bot.py"
echo "   cp cloud_web_dashboard.py $APP_DIR/aws_web_dashboard.py"
echo "   cp cloud_scheduler.py $APP_DIR/aws_scheduler.py"
echo ""
echo "2. Configure Instagram credentials:"
echo "   nano $APP_DIR/.env"
echo ""
echo "3. Update target accounts:"
echo "   nano $APP_DIR/config/automation_config.json"
echo ""
echo "4. Start the automation:"
echo "   cd $APP_DIR && ./scripts/control.sh start"
echo ""
echo "5. Access dashboard:"
echo "   http://\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo ""
echo "🔧 Management Commands:"
echo "   ./scripts/control.sh [start|stop|restart|status|logs]"
echo "   ./scripts/backup.sh (create backup)"
echo ""
echo "🚛 Migration Ready:"
echo "   ✅ Easy migration to GCP or Azure"
echo "   ✅ Complete in 15-20 minutes"
echo "   ✅ No vendor lock-in"
echo ""
print_status "AWS deployment script completed successfully!" 