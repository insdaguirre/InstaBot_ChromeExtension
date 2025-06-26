#!/bin/bash
# Cloud Instagram Automation Deployment Script
# Optimized for Oracle Cloud Free Tier Ubuntu VM

set -e  # Exit on any error

echo "🚀 Starting Oracle Cloud Instagram Automation Deployment"
echo "=================================================="

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
sudo apt-get install -y python3 python3-pip python3-venv git curl wget

# Install Chrome and ChromeDriver
print_step "3. Installing Google Chrome and ChromeDriver"

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
print_status "Chrome version: $CHROME_VERSION"

# Download ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

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
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Download cloud-optimized automation files
print_step "9. Setting up automation files"

# Check if we're copying from local directory or need to download
if [ -f "../cloud_instagram_bot.py" ]; then
    print_status "Copying files from local directory"
    cp ../cloud_instagram_bot.py ./
    cp ../cloud_scheduler.py ./
    cp ../cloud_web_dashboard.py ./
    cp ../cloud_requirements.txt ./requirements.txt
else
    print_status "Files will need to be uploaded manually after deployment"
fi

# Create configuration file
print_step "10. Creating configuration file"
cat > cloud_config.json << 'EOF'
{
  "instagram_username": "YOUR_INSTAGRAM_USERNAME",
  "instagram_password": "YOUR_INSTAGRAM_PASSWORD",
  "target_accounts": [
    "example_account1",
    "example_account2",
    "example_account3",
    "example_account4"
  ],
  "daily_follow_limit": 100,
  "followers_per_account": 25,
  "accounts_per_batch": 4,
  "unfollow_delay_hours": 48,
  "follow_schedule": "10:00",
  "unfollow_schedule": "22:00",
  "min_delay_between_follows": 15,
  "max_delay_between_follows": 45,
  "enabled": true,
  "cloud_mode": true,
  "headless": true,
  "max_retries": 3
}
EOF

# Create systemd service files
print_step "11. Creating systemd services"

# Create scheduler service
sudo tee /etc/systemd/system/instagram-scheduler.service > /dev/null << EOF
[Unit]
Description=Instagram Automation Cloud Scheduler
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=DISPLAY=:99
Environment=HEADLESS=true
ExecStartPre=/bin/bash -c 'Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &'
ExecStart=$APP_DIR/venv/bin/python cloud_scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=instagram-scheduler

[Install]
WantedBy=multi-user.target
EOF

# Create dashboard service
sudo tee /etc/systemd/system/instagram-dashboard.service > /dev/null << EOF
[Unit]
Description=Instagram Automation Web Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python cloud_web_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=instagram-dashboard

[Install]
WantedBy=multi-user.target
EOF

# Create management scripts
print_step "12. Creating management scripts"

# Service control script
cat > service_control.sh << 'EOF'
#!/bin/bash
# Instagram Automation Service Control Script

case "$1" in
    start)
        echo "Starting Instagram Automation services..."
        sudo systemctl start instagram-scheduler
        sudo systemctl start instagram-dashboard
        echo "Services started!"
        ;;
    stop)
        echo "Stopping Instagram Automation services..."
        sudo systemctl stop instagram-scheduler
        sudo systemctl stop instagram-dashboard
        echo "Services stopped!"
        ;;
    restart)
        echo "Restarting Instagram Automation services..."
        sudo systemctl restart instagram-scheduler
        sudo systemctl restart instagram-dashboard
        echo "Services restarted!"
        ;;
    status)
        echo "Instagram Scheduler Status:"
        sudo systemctl status instagram-scheduler --no-pager
        echo ""
        echo "Dashboard Status:"
        sudo systemctl status instagram-dashboard --no-pager
        ;;
    logs)
        echo "Recent logs (press Ctrl+C to exit):"
        sudo journalctl -f -u instagram-scheduler -u instagram-dashboard
        ;;
    enable)
        echo "Enabling services to start on boot..."
        sudo systemctl enable instagram-scheduler
        sudo systemctl enable instagram-dashboard
        echo "Services enabled!"
        ;;
    disable)
        echo "Disabling services from starting on boot..."
        sudo systemctl disable instagram-scheduler
        sudo systemctl disable instagram-dashboard
        echo "Services disabled!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOF

chmod +x service_control.sh

# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
# Update script for Instagram Automation

echo "🔄 Updating Instagram Automation..."

# Stop services
./service_control.sh stop

# Activate virtual environment
source venv/bin/activate

# Update packages
pip install --upgrade pip
pip install -r requirements.txt

# Restart services
./service_control.sh start

echo "✅ Update completed!"
EOF

chmod +x update.sh

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# System monitoring script

echo "📊 Instagram Automation System Monitor"
echo "======================================"

echo "🖥️  System Resources:"
echo "Memory Usage: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk Usage: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"

echo ""
echo "🤖 Service Status:"
sudo systemctl is-active instagram-scheduler && echo "Scheduler: Active" || echo "Scheduler: Inactive"
sudo systemctl is-active instagram-dashboard && echo "Dashboard: Active" || echo "Dashboard: Inactive"

echo ""
echo "📈 Process Information:"
ps aux | grep -E "(cloud_scheduler|cloud_web_dashboard)" | grep -v grep | head -5

echo ""
echo "🌐 Network Connections:"
ss -tuln | grep -E ":(5000|80|443)" | head -5

echo ""
echo "📝 Recent Log Entries:"
sudo journalctl -u instagram-scheduler --no-pager -n 5 --since "1 hour ago"
EOF

chmod +x monitor.sh

# Setup firewall (UFW)
print_step "13. Configuring firewall"
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 5000/tcp  # Dashboard port
sudo ufw status

# Reload systemd and enable services
print_step "14. Configuring systemd services"
sudo systemctl daemon-reload

# Create data directories
print_step "15. Creating data directories"
mkdir -p instagram_data/logs
mkdir -p instagram_data/csv_exports

# Setup log rotation
print_step "16. Setting up log rotation"
sudo tee /etc/logrotate.d/instagram-automation > /dev/null << EOF
$APP_DIR/instagram_data/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Create startup script for easy configuration
cat > configure.sh << 'EOF'
#!/bin/bash
# Configuration script for Instagram Automation

echo "🔧 Instagram Automation Configuration"
echo "====================================="

# Check if config exists
if [ ! -f "cloud_config.json" ]; then
    echo "❌ Configuration file not found!"
    exit 1
fi

echo "Current configuration:"
cat cloud_config.json | python3 -m json.tool

echo ""
read -p "Do you want to edit the configuration? (y/n): " edit_config

if [ "$edit_config" = "y" ]; then
    nano cloud_config.json
    echo "✅ Configuration updated!"
fi

echo ""
read -p "Do you want to enable auto-start on boot? (y/n): " enable_boot

if [ "$enable_boot" = "y" ]; then
    ./service_control.sh enable
fi

echo ""
read -p "Do you want to start the services now? (y/n): " start_now

if [ "$start_now" = "y" ]; then
    ./service_control.sh start
    echo ""
    echo "🌐 Dashboard will be available at: http://$(curl -s ifconfig.me):5000"
    echo "📊 Monitor with: ./monitor.sh"
    echo "🔧 Control with: ./service_control.sh [start|stop|restart|status]"
fi
EOF

chmod +x configure.sh

# Deactivate virtual environment
deactivate

# Final setup instructions
print_step "17. Deployment Complete!"
print_status "✅ Instagram Automation deployed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit configuration: ./configure.sh"
echo "2. Upload your automation files if not already present"
echo "3. Configure Instagram credentials in cloud_config.json"
echo "4. Start services: ./service_control.sh start"
echo "5. Access dashboard: http://YOUR_VM_IP:5000"
echo ""
echo "🔧 Management Commands:"
echo "  ./service_control.sh [start|stop|restart|status|logs]"
echo "  ./monitor.sh - System monitoring"
echo "  ./update.sh - Update the application"
echo ""
echo "📁 Application Directory: $APP_DIR"
echo "📝 Logs Location: $APP_DIR/instagram_data/logs/"
echo "📊 Dashboard URL: http://$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VM_IP"):5000"
echo ""
print_warning "Remember to:"
print_warning "- Configure your Instagram credentials"
print_warning "- Set up target accounts list"
print_warning "- Open port 5000 in Oracle Cloud security rules"
print_warning "- Consider setting up SSL/TLS for production use"

echo ""
echo "🎉 Ready for 24/7 cloud automation!" 