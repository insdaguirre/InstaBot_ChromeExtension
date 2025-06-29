#!/bin/bash
# Deploy Instagram Bot to Hetzner Server

echo "🚀 Instagram Bot Hetzner Deployment"
echo "===================================="

# Check if we have server IP
if [ -z "$1" ]; then
    echo "❌ Usage: $0 <server-ip>"
    echo "Example: $0 123.456.789.0"
    exit 1
fi

SERVER_IP=$1
echo "🎯 Target Server: $SERVER_IP"

# Create deployment package
echo "📦 Creating deployment package..."
mkdir -p deployment_package
cp server_bot.py deployment_package/
cp instagram_gui.py deployment_package/
cp web_dashboard.py deployment_package/
cp requirements_server.txt deployment_package/
cp instagram-bot.service deployment_package/
cp instagram-dashboard.service deployment_package/
cp setup_hetzner_server.sh deployment_package/

# Create deployment archive
tar -czf instagram-bot-deployment.tar.gz deployment_package/

echo "📋 Deployment package created: instagram-bot-deployment.tar.gz"
echo ""
echo "🚀 Next Steps:"
echo "1. Copy files to server:"
echo "   scp -i ~/.ssh/hetzner_instagram_bot instagram-bot-deployment.tar.gz root@$SERVER_IP:~/"
echo "   scp -i ~/.ssh/hetzner_instagram_bot setup_hetzner_server.sh root@$SERVER_IP:~/"
echo ""
echo "2. SSH to server and run setup:"
echo "   ssh -i ~/.ssh/hetzner_instagram_bot root@$SERVER_IP"
echo "   chmod +x setup_hetzner_server.sh"
echo "   ./setup_hetzner_server.sh"
echo ""
echo "3. Extract and deploy bot:"
echo "   tar -xzf instagram-bot-deployment.tar.gz"
echo "   cd deployment_package"
echo "   cp * /home/bot/instagram-automation/"
echo ""
echo "4. Configure and start:"
echo "   sudo -u bot nano /home/bot/instagram-automation/config.json"
echo "   sudo systemctl start instagram-bot"
echo "   sudo systemctl start instagram-dashboard"
echo ""
echo "5. Access dashboard:"
echo "   http://$SERVER_IP:5000"
