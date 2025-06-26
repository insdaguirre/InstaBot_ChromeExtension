#!/bin/bash
# Quick setup script for Oracle Cloud VM

echo "🚀 Quick Instagram Automation Setup"
echo "===================================="

# Make deployment script executable
chmod +x cloud_deploy.sh

# Run deployment
echo "Starting automated deployment..."
./cloud_deploy.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./configure.sh"
echo "2. Edit Instagram credentials"
echo "3. Start automation: ./service_control.sh start"
echo "4. Access dashboard: http://$(curl -s ifconfig.me):5000"
