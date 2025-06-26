# 🚀 AWS Instagram Automation - Complete Deployment Walkthrough

**Follow this step-by-step guide to deploy your Instagram automation on AWS EC2.**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- ✅ AWS account created and verified
- ✅ Credit card added (won't be charged during free tier)
- ✅ Your Instagram username and password ready
- ✅ Your target Instagram accounts list ready
- ✅ This GitHub repository cloned or files ready to upload

---

## 🔐 Step 1: Create EC2 Key Pair (5 minutes)

### 1.1 Navigate to EC2 Key Pairs
1. **Login** to [AWS Console](https://console.aws.amazon.com/)
2. **Search** for "EC2" in the top search bar
3. **Click** on "EC2" service
4. In the left sidebar, **click** "Key Pairs" (under Network & Security)

### 1.2 Create New Key Pair
1. **Click** the orange "Create key pair" button
2. **Enter** key pair name: `instagram-automation-key`
3. **Select** key pair type: `RSA`
4. **Select** private key file format:
   - **macOS/Linux**: `.pem`
   - **Windows**: `.ppk` (if using PuTTY) or `.pem` (if using WSL)
5. **Click** "Create key pair"
6. **File downloads automatically** - save it securely!

### 1.3 Set Permissions (macOS/Linux only)
```bash
# Navigate to where the key was downloaded (usually Downloads)
cd ~/Downloads

# Set correct permissions
chmod 400 instagram-automation-key.pem

# Move to a safe location
mkdir -p ~/.ssh
mv instagram-automation-key.pem ~/.ssh/
```

---

## 🌐 Step 2: Create Security Group (3 minutes)

### 2.1 Navigate to Security Groups
1. In EC2 console, **click** "Security Groups" (left sidebar under Network & Security)
2. **Click** the orange "Create security group" button

### 2.2 Configure Security Group
1. **Security group name**: `instagram-automation-sg`
2. **Description**: `Security group for Instagram automation`
3. **VPC**: Leave default (should show `vpc-xxxxx (default)`)

### 2.3 Add Inbound Rules
**Click** "Add rule" for each of these:

**Rule 1 - SSH Access:**
- **Type**: `SSH`
- **Protocol**: `TCP` (auto-filled)
- **Port range**: `22` (auto-filled)
- **Source**: `My IP` (recommended) or `0.0.0.0/0` (less secure but easier)
- **Description**: `SSH access`

**Rule 2 - Dashboard Access:**
- **Click** "Add rule"
- **Type**: `Custom TCP`
- **Protocol**: `TCP` (auto-filled)
- **Port range**: `5000`
- **Source**: `0.0.0.0/0` (to access dashboard from anywhere)
- **Description**: `Instagram automation dashboard`

### 2.4 Outbound Rules
- **Leave default** (should allow all outbound traffic)

### 2.5 Create Security Group
- **Click** orange "Create security group" button

---

## 💻 Step 3: Launch EC2 Instance (10 minutes)

### 3.1 Start Instance Creation
1. **Click** "Instances" in left sidebar
2. **Click** orange "Launch instances" button

### 3.2 Configure Instance Details

**Name and tags:**
- **Name**: `instagram-automation`

**Application and OS Images:**
- **Quick Start tab** should be selected
- **Click** "Ubuntu"
- **Select** "Ubuntu Server 22.04 LTS (HVM), SSD Volume Type"
- **Architecture**: `64-bit (x86)`

**Instance type:**
- **Click** "t2.micro" (should show "Free tier eligible")
- ⚠️ **Important**: Make sure it says "Free tier eligible"

**Key pair:**
- **Select** "Choose an existing key pair"
- **Key pair name**: Select `instagram-automation-key`
- **Check** the acknowledgment box

**Network settings:**
- **Click** "Edit" button
- **VPC**: Leave default
- **Subnet**: Leave default (or select any available)
- **Auto-assign public IP**: `Enable`
- **Firewall (security groups)**: `Select existing security group`
- **Security groups**: Select `instagram-automation-sg`

**Configure storage:**
- **Size**: `8` GiB (default is fine, up to 30 GiB is free)
- **Volume type**: `gp3` (recommended for better performance)
- **Delete on termination**: `Yes` (checked)

### 3.3 Launch Instance
1. **Review** all settings in the Summary panel on the right
2. **Click** orange "Launch instance" button
3. **Click** "View all instances"

### 3.4 Wait for Instance to Start
- **Status**: Wait until "Instance state" shows `Running`
- **Status checks**: Wait until "Status check" shows `2/2 checks passed`
- This takes about 2-3 minutes

---

## 🔗 Step 4: Connect to Your Instance (5 minutes)

### 4.1 Get Connection Information
1. **Click** on your instance (checkbox)
2. **Click** "Connect" button at the top
3. **Click** "SSH client" tab

### 4.2 Connect via Terminal (macOS/Linux)
**Copy the connection command shown**, it looks like:
```bash
ssh -i "~/.ssh/instagram-automation-key.pem" ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com
```

**In your terminal:**
```bash
# Use the exact command from AWS console
ssh -i "~/.ssh/instagram-automation-key.pem" ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com

# Type "yes" when prompted about authenticity
```

### 4.3 Connect via PuTTY (Windows)
If using PuTTY:
1. **Open** PuTTY
2. **Host Name**: `ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com`
3. **Port**: `22`
4. **Connection type**: `SSH`
5. **Expand** SSH in left panel → **Click** Auth
6. **Browse** for your `.ppk` file
7. **Click** Open

---

## 📦 Step 5: Deploy Instagram Automation (15 minutes)

### 5.1 Update System
```bash
# Update package lists
sudo apt update -y

# Upgrade existing packages (this might take a few minutes)
sudo apt upgrade -y
```

### 5.2 Clone Your Repository
```bash
# Clone your Instagram automation repository
git clone https://github.com/YOUR_USERNAME/instagram-automation.git

# Navigate to the directory
cd instagram-automation

# Make deployment script executable
chmod +x aws_deploy.sh
```

### 5.3 Run AWS Deployment Script
```bash
# Run the deployment script (this takes 10-15 minutes)
./aws_deploy.sh
```

**What this script does:**
- Installs Python, pip, and dependencies
- Installs Google Chrome and ChromeDriver
- Sets up virtual display (Xvfb)
- Creates directory structure
- Installs Python packages
- Creates configuration files
- Sets up management scripts

### 5.4 Copy Automation Files
```bash
# Copy cloud files to AWS versions
cp cloud_instagram_bot.py aws_instagram_bot.py
cp cloud_web_dashboard.py aws_web_dashboard.py
cp cloud_scheduler.py aws_scheduler.py
```

---

## ⚙️ Step 6: Configure Instagram Automation (5 minutes)

### 6.1 Set Instagram Credentials
```bash
# Edit environment file
nano .env
```

**Update the file with your Instagram credentials:**
```env
INSTAGRAM_USERNAME=your_actual_instagram_username
INSTAGRAM_PASSWORD=your_actual_instagram_password
DAILY_FOLLOW_LIMIT=100
FOLLOWERS_PER_ACCOUNT=25
FOLLOW_SCHEDULE=10:00
UNFOLLOW_SCHEDULE=22:00
MIN_DELAY=15
MAX_DELAY=45
HEADLESS=true
CLOUD_PROVIDER=AWS
AWS_REGION=us-east-1
```

**Save and exit:**
- **Press** `Ctrl+X`
- **Press** `Y` to confirm
- **Press** `Enter` to save

### 6.2 Configure Target Accounts
```bash
# Edit target accounts
nano config/automation_config.json
```

**Update the target_accounts section:**
```json
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
  }
}
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

## 🚀 Step 7: Start Your Automation (2 minutes)

### 7.1 Start Services
```bash
# Start the Instagram automation
./scripts/control.sh start

# Check status
./scripts/control.sh status
```

**Expected output:**
```
🚀 Starting AWS Instagram Automation...
✅ Services started on AWS
📊 Dashboard: http://XX.XX.XX.XX:5000
📊 AWS Service Status:
✅ Automation: Running (PID: XXXX)
✅ Dashboard: Running (PID: XXXX)
✅ Virtual Display: Running (PID: XXXX)
🌐 Public IP: XX.XX.XX.XX
```

### 7.2 View Logs (Optional)
```bash
# View real-time logs
./scripts/control.sh logs

# Press Ctrl+C to exit log view
```

---

## 🌐 Step 8: Access Your Dashboard (2 minutes)

### 8.1 Get Your Public IP
**Your public IP is shown in several places:**
- In the `./scripts/control.sh status` output
- In AWS console: Select your instance and look for "Public IPv4 address"
- Command: `curl http://169.254.169.254/latest/meta-data/public-ipv4`

### 8.2 Open Dashboard
1. **Open** your web browser
2. **Go to**: `http://YOUR_PUBLIC_IP:5000`
   - Example: `http://54.123.45.67:5000`

### 8.3 Dashboard Features
You should see:
- 🤖 **Service Status** - Running/stopped status
- 📊 **AWS Resources** - Instance info, CPU, memory usage
- 📈 **Today's Progress** - Follows completed
- ⚙️ **Configuration** - Current settings
- 📝 **Live Logs** - Real-time automation logs
- 🔧 **Controls** - Start/stop/restart buttons

---

## ✅ Step 9: Test Your Setup (5 minutes)

### 9.1 Manual Test Run
```bash
# Stop current automation
./scripts/control.sh stop

# Run a quick test
cd ~/instagram-automation
source venv/bin/activate
python aws_instagram_bot.py
```

### 9.2 Check Logs
```bash
# View automation logs
tail -f logs/aws_automation.log

# Press Ctrl+C to exit
```

### 9.3 Restart Full Automation
```bash
# Start full automation with scheduler
./scripts/control.sh start
```

---

## 🔧 Step 10: Management and Monitoring

### 10.1 Essential Commands
```bash
# Service management
./scripts/control.sh start     # Start automation
./scripts/control.sh stop      # Stop automation
./scripts/control.sh restart   # Restart automation
./scripts/control.sh status    # Check status
./scripts/control.sh logs      # View logs

# Backup (for migration)
./scripts/backup.sh            # Create backup
```

### 10.2 Monitor AWS Costs
1. **Go to** [AWS Billing Dashboard](https://console.aws.amazon.com/billing/)
2. **Click** "Bills" in left sidebar
3. **Monitor** your free tier usage
4. **Set up** billing alerts (recommended):
   - Click "Billing preferences"
   - Check "Receive Billing Alerts"
   - Go to CloudWatch → Alarms → Create Alarm

### 10.3 SSH Back In (Future Access)
```bash
# Always use this command to reconnect
ssh -i "~/.ssh/instagram-automation-key.pem" ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com

# Navigate to your automation
cd instagram-automation
```

---

## 🚛 Step 11: Prepare for Migration (Year 2)

### 11.1 Set Calendar Reminder
**Set a reminder for 11 months from now** to migrate to Google Cloud before AWS charges start.

### 11.2 Migration Process (Future)
When your free tier expires:

```bash
# 1. Create backup
./scripts/backup.sh

# 2. Download backup to your computer
scp -i ~/.ssh/instagram-automation-key.pem ubuntu@your-aws-ip:~/instagram-automation/backups/aws_backup_*.tar.gz ~/Downloads/

# 3. Set up Google Cloud (see GCP guide)
# 4. Upload backup and restore
# 5. Terminate AWS instance
```

---

## 🎉 Success! Your Instagram Automation is Live

You now have:
- ✅ **24/7 Instagram automation** running on AWS
- ✅ **Web dashboard** for monitoring at `http://YOUR_IP:5000`
- ✅ **$0/month hosting** for 12 months
- ✅ **Migration-ready** setup for year 2
- ✅ **Professional logging** and monitoring
- ✅ **Easy management** via command line

### 🔮 What Happens Next

**Your automation will:**
1. **Follow 100 people daily** from your target accounts
2. **Unfollow people** after 48 hours automatically  
3. **Run 24/7** without your intervention
4. **Log everything** for monitoring
5. **Cost $0** for the next 12 months

**In 11 months:**
1. **Create backup** (1 minute)
2. **Migrate to Google Cloud** (15 minutes)
3. **Continue free** for another 12 months
4. **Total saved**: $157/year

---

## 🆘 Troubleshooting

### Common Issues and Solutions

**🔴 Can't connect via SSH:**
```bash
# Check security group allows SSH from your IP
# Verify you're using the correct key file and instance IP
# Try: ssh -v -i "key.pem" ubuntu@your-ip (verbose mode)
```

**🔴 Dashboard not accessible:**
- Check security group allows port 5000 from 0.0.0.0/0
- Verify services are running: `./scripts/control.sh status`
- Check AWS instance public IP hasn't changed

**🔴 Automation not working:**
```bash
# Check logs
./scripts/control.sh logs

# Restart services
./scripts/control.sh restart

# Test Chrome installation
google-chrome --version
which chromedriver
```

**🔴 High memory usage:**
```bash
# Monitor resources
htop

# Check for multiple Chrome processes
ps aux | grep chrome

# Restart if needed
./scripts/control.sh restart
```

**🔴 Instagram login issues:**
- Double-check credentials in `.env` file
- Try logging in manually on Instagram web
- Check for 2FA (not currently supported)

### Getting Help

**Support Resources:**
- AWS EC2 documentation
- Check logs: `./scripts/control.sh logs`
- Monitor dashboard: `http://YOUR_IP:5000`
- AWS Free Tier usage: [AWS Billing Console](https://console.aws.amazon.com/billing/)

---

**🎊 Congratulations! Your Instagram automation is now running 24/7 on AWS for free!** 