#!/bin/bash
# Create Oracle Cloud Deployment Package
# This script packages all necessary files for cloud deployment

echo "📦 Creating Oracle Cloud Deployment Package"
echo "==========================================="

# Create package directory
PACKAGE_DIR="instagram-automation-cloud-package"
mkdir -p "$PACKAGE_DIR"

echo "📁 Copying cloud-optimized files..."

# Copy cloud-specific files
cp cloud_instagram_bot.py "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ cloud_instagram_bot.py not found - will need to be created"
cp cloud_scheduler.py "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ cloud_scheduler.py not found - will need to be created"
cp cloud_web_dashboard.py "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ cloud_web_dashboard.py not found - will need to be created"
cp cloud_requirements.txt "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ cloud_requirements.txt not found - will need to be created"
cp cloud_deploy.sh "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ cloud_deploy.sh not found - will need to be created"
cp ORACLE_CLOUD_DEPLOYMENT_GUIDE.md "$PACKAGE_DIR/" 2>/dev/null || echo "⚠️ Deployment guide not found - will need to be created"

# Create README for the package
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# Instagram Automation - Oracle Cloud Package

This package contains everything needed to deploy Instagram automation on Oracle Cloud Free Tier.

## 📦 Package Contents

- `cloud_instagram_bot.py` - Cloud-optimized Instagram bot
- `cloud_scheduler.py` - 24/7 automation scheduler  
- `cloud_web_dashboard.py` - Web monitoring dashboard
- `cloud_requirements.txt` - Python dependencies
- `cloud_deploy.sh` - Automated deployment script
- `ORACLE_CLOUD_DEPLOYMENT_GUIDE.md` - Complete deployment guide

## 🚀 Quick Start

1. Follow the Oracle Cloud setup in `ORACLE_CLOUD_DEPLOYMENT_GUIDE.md`
2. Upload all files to your Oracle Cloud VM
3. Run: `chmod +x cloud_deploy.sh && ./cloud_deploy.sh`
4. Configure: `./configure.sh`
5. Access dashboard: `http://YOUR_VM_IP:5000`

## 💰 Cost

- **$0/month forever** with Oracle Cloud Always Free Tier
- 2 CPU cores, 12GB RAM, 50GB storage
- Perfect for 100 follows/day automation

## 🔗 Links

- Oracle Cloud: https://cloud.oracle.com
- Always Free: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

Ready for 24/7 Instagram growth automation!
EOF

# Create quick setup script
cat > "$PACKAGE_DIR/quick_setup.sh" << 'EOF'
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
EOF

chmod +x "$PACKAGE_DIR/quick_setup.sh"

# Create configuration template
cat > "$PACKAGE_DIR/cloud_config_template.json" << 'EOF'
{
  "instagram_username": "YOUR_INSTAGRAM_USERNAME",
  "instagram_password": "YOUR_INSTAGRAM_PASSWORD",
  "target_accounts": [
    "target_account_1",
    "target_account_2", 
    "target_account_3",
    "target_account_4"
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

# Create transfer instructions
cat > "$PACKAGE_DIR/TRANSFER_INSTRUCTIONS.md" << 'EOF'
# 📤 File Transfer Instructions

## Method 1: SCP (Mac/Linux)

```bash
# Upload entire package
scp -i ~/.ssh/oracle_cloud_key -r instagram-automation-cloud-package ubuntu@YOUR_VM_IP:~/

# SSH into VM
ssh -i ~/.ssh/oracle_cloud_key ubuntu@YOUR_VM_IP

# Navigate and setup
cd instagram-automation-cloud-package
./quick_setup.sh
```

## Method 2: WinSCP (Windows)

1. Download and install WinSCP
2. Connect using your Oracle Cloud SSH key
3. Upload the entire `instagram-automation-cloud-package` folder
4. Use PuTTY to SSH into your VM
5. Run: `cd instagram-automation-cloud-package && ./quick_setup.sh`

## Method 3: Git Repository (Recommended)

1. Upload package to GitHub/GitLab
2. SSH into Oracle Cloud VM
3. Run: `git clone YOUR_REPOSITORY_URL`
4. Navigate and setup: `cd YOUR_REPO && ./quick_setup.sh`

## Verification

After upload, verify all files are present:
```bash
ls -la instagram-automation-cloud-package/
```

Should show:
- cloud_instagram_bot.py
- cloud_scheduler.py  
- cloud_web_dashboard.py
- cloud_deploy.sh
- quick_setup.sh
- README.md
- And more...
EOF

# Create archive
echo "📦 Creating deployment archive..."
tar -czf instagram-automation-cloud.tar.gz "$PACKAGE_DIR"

echo ""
echo "✅ Package created successfully!"
echo ""
echo "📦 Package contents:"
ls -la "$PACKAGE_DIR/"
echo ""
echo "📁 Package directory: $PACKAGE_DIR/"
echo "📦 Archive file: instagram-automation-cloud.tar.gz"
echo ""
echo "🚀 Next steps:"
echo "1. Upload package to your Oracle Cloud VM"
echo "2. Extract: tar -xzf instagram-automation-cloud.tar.gz"
echo "3. Run: cd $PACKAGE_DIR && ./quick_setup.sh"
echo ""
echo "📋 Transfer options:"
echo "- SCP: scp -r $PACKAGE_DIR ubuntu@YOUR_VM_IP:~/"
echo "- Archive: Upload instagram-automation-cloud.tar.gz"
echo "- Git: Push to repository and clone on VM"
echo ""
echo "🎉 Ready for Oracle Cloud deployment!"
EOF 