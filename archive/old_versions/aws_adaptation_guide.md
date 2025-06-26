# 🟡 AWS Free Tier Adaptation Guide

**Adaptation Effort: 5-10 minutes**  
**Changes Required: Minimal - just Chrome/Selenium tweaks**

## 🎯 What Works Out-of-the-Box

Your current repo is **95% compatible** with AWS! These work perfectly:
- ✅ `cloud_instagram_bot.py` - No changes needed
- ✅ `cloud_scheduler.py` - No changes needed  
- ✅ `cloud_requirements.txt` - No changes needed
- ✅ Virtual display setup (Xvfb) - No changes needed
- ✅ Flask dashboard - No changes needed

## 🔧 Required Changes (5 minutes)

### **1. Chrome Installation Script**
Update `cloud_deploy.sh` for AWS Ubuntu:

```bash
# Current Oracle Cloud setup:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# AWS Ubuntu 20.04 needs this instead:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
```

### **2. ChromeDriver Path**  
Add AWS-specific path to `cloud_instagram_bot.py`:

```python
# In init_driver() method, update driver_paths:
driver_paths = [
    '/usr/bin/chromedriver',           # Default
    '/usr/local/bin/chromedriver',     # Manual install
    '/snap/bin/chromium.chromedriver', # AWS Ubuntu snap
    'chromedriver'                     # Fallback
]
```

### **3. AWS-Specific Firewall**
Replace Oracle Cloud firewall with AWS Security Groups:

```bash
# No iptables commands needed - AWS uses Security Groups
# Just ensure port 5000 is open in AWS console
```

## 📋 AWS Deployment Steps

### **Step 1: Launch EC2 Instance**
```
Instance Type: t2.micro (1GB RAM, 1 vCPU)
AMI: Ubuntu 20.04 LTS  
Storage: 8GB (Free tier includes 30GB)
Security Group: 
  - SSH (port 22) from your IP
  - HTTP (port 5000) from anywhere
```

### **Step 2: Deploy Your Code**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Clone your repo
git clone https://github.com/YOUR_USERNAME/instagram-automation.git
cd instagram-automation

# Run modified deployment script
chmod +x aws_deploy.sh
./aws_deploy.sh
```

### **Step 3: Configure and Start**
```bash
# Configure Instagram credentials
nano .env

# Start automation
./scripts/control.sh start

# Access dashboard
http://your-aws-instance-ip:5000
```

## 💰 AWS Free Tier Cost Analysis

### **Free Tier Limits (12 months)**
```
✅ 750 hours/month t2.micro (enough for 24/7)
✅ 30GB EBS storage
✅ 15GB data transfer out
✅ 1 Elastic IP (if you keep it assigned)
```

### **Usage for Instagram Automation**
```
CPU: ~10-20% (well within limits)
RAM: ~400-600MB (fits in 1GB)  
Storage: ~2GB (well within 30GB)
Bandwidth: ~100MB/day (well within 15GB/month)
```

### **Costs After Free Tier (Year 2+)**
```
t2.micro: $8.76/month
30GB Storage: $3.00/month  
Data Transfer: $1.35/month (15GB)
Total: $13.11/month ($157/year)
```

## 🔄 Migration Strategy (Year 2)

**When AWS free tier expires:**

```bash
# Backup data (1 minute)
./scripts/backup.sh

# Download backup to your computer
scp ubuntu@aws-ip:~/instagram-automation/backups/backup.tar.gz .

# Destroy AWS instance (avoid charges)
# Launch new instance on Google Cloud
# Upload and restore backup
```

**Migration time: 15-20 minutes**

## ⚡ AWS Adaptation Script

Create `aws_deploy.sh`:

```bash
#!/bin/bash
# AWS Ubuntu 20.04 Deployment Script

set -e

echo "🟡 AWS Instagram Automation Deployment"
echo "====================================="

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python
sudo apt-get install -y python3 python3-pip python3-venv git curl wget unzip

# Install Chrome (AWS Ubuntu specific)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install virtual display
sudo apt-get install -y xvfb x11vnc

# Setup application
mkdir -p ~/instagram-automation
cd ~/instagram-automation

# Copy your existing files here...
# (git clone, copy files, etc.)

# Create virtual environment and install packages
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ AWS deployment complete!"
echo "Configure credentials in .env file"
echo "Start with: ./scripts/control.sh start"
```

## 🎯 Summary

**AWS Adaptation:**
- ✅ **Time required**: 5-10 minutes
- ✅ **Changes needed**: Minimal (Chrome install script)
- ✅ **Free period**: 12 months  
- ✅ **Migration difficulty**: Very easy
- ✅ **Post-free cost**: $157/year 