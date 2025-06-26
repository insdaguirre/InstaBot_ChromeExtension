# 🔵 Google Cloud Platform Adaptation Guide

**Adaptation Effort: 10-15 minutes**  
**Changes Required: Medium - Debian package management tweaks**

## 🎯 What Works Out-of-the-Box

Your current repo is **90% compatible** with GCP! These work perfectly:
- ✅ `cloud_instagram_bot.py` - No changes needed
- ✅ `cloud_scheduler.py` - No changes needed  
- ✅ `cloud_requirements.txt` - No changes needed
- ✅ Virtual display setup (Xvfb) - No changes needed
- ✅ Flask dashboard - No changes needed

## 🔧 Required Changes (10-15 minutes)

### **1. Chrome Installation for Debian**
Update `cloud_deploy.sh` for GCP Debian:

```bash
# Current Oracle Cloud (Ubuntu) setup:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# GCP Debian 11 needs this instead:
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
```

### **2. GCP Metadata Detection**
Add GCP detection to `cloud_instagram_bot.py`:

```python
def detect_cloud_provider():
    """Detect if running on GCP"""
    try:
        import requests
        response = requests.get(
            'http://metadata.google.internal/computeMetadata/v1/instance/zone',
            headers={'Metadata-Flavor': 'Google'},
            timeout=2
        )
        if response.status_code == 200:
            return 'GCP'
    except:
        pass
    return 'Unknown'
```

### **3. GCP-Specific Memory Limits**
Update Chrome options for GCP's e2-micro (1GB RAM):

```python
# In init_driver() method, add GCP optimizations:
if self.detect_cloud_provider() == 'GCP':
    # More aggressive memory limits for GCP
    options.add_argument('--memory-pressure-off')
    options.add_argument('--max_old_space_size=256')  # Stricter than Oracle
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
```

### **4. GCP Firewall Rules**
Replace manual iptables with gcloud commands:

```bash
# Allow dashboard access (run from Cloud Shell or local machine with gcloud)
gcloud compute firewall-rules create allow-instagram-dashboard \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow access to Instagram automation dashboard"
```

## 📋 GCP Deployment Steps

### **Step 1: Create Compute Engine Instance**
```bash
# Using gcloud CLI (recommended)
gcloud compute instances create instagram-automation \
    --machine-type=e2-micro \
    --boot-disk-size=10GB \
    --boot-disk-type=pd-standard \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --tags=instagram-bot \
    --zone=us-central1-a

# Or use Console:
# Machine type: e2-micro (1GB RAM, 2 shared vCPUs)  
# Boot disk: Debian 11, 10GB
# Firewall: Allow HTTP traffic
```

### **Step 2: Deploy Your Code**
```bash
# SSH into instance
gcloud compute ssh instagram-automation --zone=us-central1-a

# Or use browser SSH from console

# Clone your repo
git clone https://github.com/YOUR_USERNAME/instagram-automation.git
cd instagram-automation

# Run GCP deployment script
chmod +x gcp_deploy.sh
./gcp_deploy.sh
```

### **Step 3: Configure Firewall**
```bash
# Create firewall rule for dashboard
gcloud compute firewall-rules create allow-instagram-dashboard \
    --allow tcp:5000 \
    --target-tags instagram-bot \
    --source-ranges 0.0.0.0/0
```

### **Step 4: Start Services**
```bash
# Configure Instagram credentials
nano .env

# Start automation
./scripts/control.sh start

# Get external IP
gcloud compute instances describe instagram-automation \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Access dashboard
http://EXTERNAL_IP:5000
```

## 💰 GCP Free Tier Cost Analysis

### **Free Tier Limits (12 months + Always Free)**
```
✅ 1 e2-micro instance/month (US regions only)
✅ 30GB standard persistent disk  
✅ 1GB egress/month (North America)
✅ Static IP (while instance is running)
```

### **Usage for Instagram Automation**
```
CPU: ~15-25% (2 shared vCPUs, burst capable)
RAM: ~400-700MB (fits in 1GB)  
Storage: ~3GB (well within 30GB)
Bandwidth: ~50MB/day (fits in 1GB/month)
```

### **Always Free Resources (Forever)**
```
✅ 1 e2-micro instance (f1-micro deprecated)
✅ 30GB standard disk storage
✅ 5GB snapshot storage
✅ 1GB egress/month
```

### **Costs After Free Tier (Year 2+)**
```
Nothing! GCP Always Free continues forever
⚠️ BUT: Subject to policy changes
⚠️ Limited to US regions only
⚠️ Account must remain in good standing
```

## 🔄 Migration Strategy (If Needed)

**If GCP changes policies or you need more resources:**

```bash
# Backup data (1 minute)
./scripts/backup.sh

# Download backup to your computer
gcloud compute scp instagram-automation:~/instagram-automation/backups/backup.tar.gz . \
    --zone=us-central1-a

# Delete GCP instance (if moving)
gcloud compute instances delete instagram-automation --zone=us-central1-a

# Deploy to Azure or back to AWS
```

**Migration time: 10-15 minutes**

## ⚡ GCP Adaptation Script

Create `gcp_deploy.sh`:

```bash
#!/bin/bash
# Google Cloud Platform Debian 11 Deployment Script

set -e

echo "🔵 GCP Instagram Automation Deployment"
echo "======================================"

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python and essential tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Chrome (GCP Debian specific)
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update -y
sudo apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
echo "Detected Chrome version: $CHROME_VERSION"

# Get compatible ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm /tmp/chromedriver.zip

# Install virtual display
sudo apt-get install -y xvfb x11vnc

# Install system monitoring
sudo apt-get install -y htop

# Setup application directory
mkdir -p ~/instagram-automation
cd ~/instagram-automation

# Copy your existing files here or clone from git
echo "✅ Ready for your Instagram automation files"

echo "🔧 Next steps:"
echo "1. Copy your automation files to ~/instagram-automation/"
echo "2. Create virtual environment: python3 -m venv venv"
echo "3. Install packages: source venv/bin/activate && pip install -r requirements.txt"
echo "4. Configure .env file with Instagram credentials"
echo "5. Setup firewall: gcloud compute firewall-rules create allow-instagram-dashboard --allow tcp:5000 --source-ranges 0.0.0.0/0"
echo "6. Start services: ./scripts/control.sh start"
```

## 🚨 GCP-Specific Considerations

### **Region Restrictions**
```
✅ Always Free only in US regions:
   - us-central1 (Iowa)
   - us-east1 (South Carolina)  
   - us-west1 (Oregon)

❌ Not available in:
   - Europe, Asia, other regions
   - Premium/expensive regions
```

### **Account Requirements**
```
✅ Valid credit card required (but not charged)
✅ Account must remain in good standing
✅ No abuse or policy violations
⚠️ Google can change Always Free terms
```

### **Performance Notes**
```
e2-micro specs:
✅ 2 shared vCPUs (burstable)
✅ 1GB RAM
✅ Better CPU performance than AWS t2.micro
⚠️ Shared CPU can be throttled under load
```

## 🎯 Summary

**GCP Adaptation:**
- ✅ **Time required**: 10-15 minutes
- ✅ **Changes needed**: Medium (Debian packages, metadata detection)
- ✅ **Free period**: 12 months + Always Free (forever*)
- ✅ **Migration difficulty**: Easy
- ✅ **Post-free cost**: $0/month (Always Free)
- ⚠️ **Risk**: Policy changes, US regions only 