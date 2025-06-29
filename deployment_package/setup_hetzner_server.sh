#!/bin/bash
# Instagram Bot Hetzner Server Setup Script

set -e

echo "🚀 Setting up Instagram Bot on Hetzner Server"
echo "============================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git curl wget gnupg2 unzip

# Install Google Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Create bot user
echo "👤 Creating bot user..."
sudo useradd -m -s /bin/bash bot
sudo usermod -aG sudo bot

# Create project directory
echo "📁 Setting up project directory..."
sudo mkdir -p /home/bot/instagram-automation
sudo chown bot:bot /home/bot/instagram-automation

# Switch to bot user for remaining setup
echo "🔄 Switching to bot user..."
sudo -u bot bash << 'BOTUSER'
cd /home/bot/instagram-automation

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install selenium webdriver-manager schedule flask requests python-dotenv psutil

# Create required directories
mkdir -p logs bot_data

# Create default config file
cat > config.json << 'CONFIG'
{
  "instagram": {
    "username": "",
    "password": "",
    "target_accounts": ["deadmau5", "skrillex", "1001tracklists"],
    "users_per_account": 5,
    "daily_follow_limit": 15,
    "unfollow_after_hours": 48
  },
  "schedule": {
    "follow_time": "09:00",
    "unfollow_time": "15:00"
  },
  "notifications": {
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "",
      "sender_password": "",
      "recipient_email": ""
    },
    "discord": {
      "enabled": false,
      "webhook_url": ""
    }
  },
  "web_dashboard": {
    "enabled": true,
    "port": 5000,
    "password": "admin123"
  }
}
CONFIG

echo "✅ Bot user setup completed"
BOTUSER

# Install and configure services
echo "⚙️ Installing systemd services..."
sudo cp instagram-bot.service /etc/systemd/system/
sudo cp instagram-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable instagram-bot
sudo systemctl enable instagram-dashboard

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

# Set up log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/instagram-bot << LOGROTATE
/home/bot/instagram-automation/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
LOGROTATE

echo ""
echo "✅ Instagram Bot Server Setup Complete!"
echo "======================================="
echo ""
echo "📋 Next Steps:"
echo "1. Copy your bot files to /home/bot/instagram-automation/"
echo "2. Edit /home/bot/instagram-automation/config.json with your settings"
echo "3. Start the services:"
echo "   sudo systemctl start instagram-bot"
echo "   sudo systemctl start instagram-dashboard"
echo ""
echo "🌐 Web Dashboard: http://YOUR_SERVER_IP:5000"
echo "🔑 Default Password: admin123"
echo ""
echo "📊 Check Status:"
echo "   sudo systemctl status instagram-bot"
echo "   sudo systemctl status instagram-dashboard"
echo ""
echo "📋 View Logs:"
echo "   sudo journalctl -u instagram-bot -f"
echo "   sudo journalctl -u instagram-dashboard -f"
