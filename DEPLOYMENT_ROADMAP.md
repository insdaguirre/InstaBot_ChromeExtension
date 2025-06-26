# 🚀 Complete Instagram Bot Deployment Roadmap

## Phase 1: Prepare Your Local Environment

### Step 1: Get Your SSH Key (DETAILED)

**Option A: If You Still Have the Original Key**
1. **Check if you already have it:**
   ```bash
   # In Terminal, navigate to your project folder
   cd "/Users/diegoaguirre/instagram automation"
   ls -la *.pem
   ```
   - If you see `instagram-automation-key.pem`, skip to Step 1D
   - If not, continue to Option B

**Option B: Download from AWS Console (Most Likely)**
1. **Open browser** → Go to: https://console.aws.amazon.com/ec2/
2. **Sign in** to your AWS account
3. **In the left sidebar**, click **"Key Pairs"** (under Network & Security)
4. **Find** `instagram-automation-key` in the list
5. **IMPORTANT:** You CANNOT download the `.pem` file again if you created it before!

**Option C: Create New Key Pair (If Original Lost)**
1. **In Key Pairs page**, click **"Create key pair"** (orange button, top right)
2. **Name:** `instagram-automation-key-new`
3. **Key pair type:** RSA
4. **Private key file format:** .pem
5. **Click "Create key pair"** - The `.pem` file will download automatically
6. **Move the downloaded file:**
   ```bash
   # In Terminal (replace Downloads with where your file downloaded)
   mv ~/Downloads/instagram-automation-key-new.pem "/Users/diegoaguirre/instagram automation/"
   ```

**Option D: Update AWS Security Group for New Key (If Created New)**
If you created a new key, you need to update your EC2 instance:
1. **In AWS Console** → **EC2** → **Instances**
2. **Select your instance** `i-0b20ed9f8671df28b`
3. **Actions** → **Security** → **Change key pair**
4. **Select your new key pair**
5. **Click "Associate key pair"**

**Step 1D: Set Permissions (REQUIRED - Run in Terminal)**
```bash
# Navigate to your project directory first
cd "/Users/diegoaguirre/instagram automation"

# Set correct permissions (replace with your actual key name)
chmod 600 instagram-automation-key.pem

# Verify it worked
ls -la *.pem
# Should show: -rw------- 1 diegoaguirre staff ... instagram-automation-key.pem
```

**Step 1E: Test SSH Connection**
```bash
# Test if the key works (replace with your actual key name)
ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com "echo 'Connection successful!'"
```
**Expected:** Should print "Connection successful!"
**If fails:** Your key is wrong or security group blocks your IP

### Step 2: Verify Local Files (DETAILED)
**Run these exact commands in Terminal:**
```bash
# Make sure you're in the right directory
cd "/Users/diegoaguirre/instagram automation"
pwd
# Should print: /Users/diegoaguirre/instagram automation

# Check for all required files
ls -la *.py *.sh *.md
```

**You MUST see ALL of these files:**
- ✅ `complete_instagram_bot.py` (424 lines, new working bot)
- ✅ `scheduler.py` (new scheduler with timing)
- ✅ `dashboard.py` (web interface for monitoring)
- ✅ `deploy_complete_system.sh` (automated deployment)
- ✅ `test_bot.py` (verification script)
- ✅ `cleanup_aws.sh` (cleanup script)
- ✅ `DEPLOYMENT_ROADMAP.md` (this file)

**If ANY are missing:**
```bash
# Check what files exist
ls -la
# Look for the missing files and make sure they were created properly
```

**Verify scripts are executable:**
```bash
# These should be executable (green in ls output)
ls -la *.sh
# If not executable, run:
chmod +x *.sh
```

---

## Phase 2: Clean Up AWS Instance (AUTOMATED)

### Step 3: Use Automated Cleanup Script
**Instead of manual cleanup, use the automated script:**

```bash
# Make sure you're in the project directory
cd "/Users/diegoaguirre/instagram automation"

# Run the automated cleanup script
./cleanup_aws.sh
```

**What this script does step-by-step:**
1. ✅ Connects to your AWS instance
2. ✅ Stops all running Python/Instagram/Chrome processes
3. ✅ Stops and removes old scheduler services
4. ✅ Backs up any existing data to `~/backup/TIMESTAMP/`
5. ✅ Removes all old problematic bot files
6. ✅ Cleans up temporary files and logs
7. ✅ Verifies virtual environment still works
8. ✅ Shows you what's left in the directory

**Expected Output:**
```
🧹 Cleaning up AWS instance...
🔌 Connecting to AWS and cleaning up...
🛑 Stopping all processes...
🗑️ Stopping services...
📁 Going to bot directory...
💾 Backing up important data...
🗂️ Removing old bot files...
🧽 Cleaning up temporary files...
📋 Current directory contents:
total 16
drwxrwxr-x 4 ubuntu ubuntu 4096 Dec XX XX:XX .
drwxr-xr-x 6 ubuntu ubuntu 4096 Dec XX XX:XX ..
drwxr-xr-x 2 ubuntu ubuntu 4096 Dec XX XX:XX instagram_data
-rw-rw-r-- 1 ubuntu ubuntu  167 Dec XX XX:XX requirements.txt
drwxrwxr-x 5 ubuntu ubuntu 4096 Dec XX XX:XX venv
🔍 Checking virtual environment...
Python version: Python 3.10.12
Virtual env path: /home/ubuntu/instabot/venv/bin/python
✅ Cleanup complete!
📊 Ready for new deployment
🎉 AWS cleanup finished!
```

**If cleanup script fails:**
```bash
# Manual connection and cleanup
ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com

# Once connected, run these commands:
pkill -f python
pkill -f instagram  
pkill -f chrome
sudo systemctl stop instagram-scheduler 2>/dev/null
cd ~/instabot
rm -f aws_instagram_bot.py working_instagram_bot.py instagram_bot.py test_*.py *.log
ls -la
source venv/bin/activate && python --version
exit
```

---

## Phase 3: Deploy New System (AUTOMATED)

### Step 4: Run Automated Deployment
**Make sure you're back in your local Terminal:**
```bash
# Navigate to project directory (if not already there)
cd "/Users/diegoaguirre/instagram automation"

# Verify you're in the right place
pwd
ls -la deploy_complete_system.sh

# Run the deployment script
./deploy_complete_system.sh
```

**Expected Step-by-Step Output:**
```
🚀 Deploying Complete Instagram Automation System to AWS...
📁 Creating remote directory structure...
📤 Uploading bot files...
complete_instagram_bot.py                    100%   15KB  15.2KB/s   00:01
scheduler.py                                 100%    2KB   2.1KB/s   00:01  
dashboard.py                                 100%    8KB   8.3KB/s   00:01
🔧 Setting up the system on AWS...
✅ System setup complete!
🧪 Testing the complete bot...
🧪 Testing Instagram Bot...
✅ Chrome started
✅ Login completed
✅ Successfully navigated to target account
✅ All tests passed! Bot is ready for deployment.
🌐 Starting web dashboard...
Dashboard started in background
✅ Dashboard is running
🔗 Access at: http://ec2-3-17-165-195.us-east-2.compute.amazonaws.com:5000
📅 Setting up the scheduler...
Created symlink /etc/systemd/system/multi-user.target.wants/instagram-scheduler.service → /etc/systemd/system/instagram-scheduler.service.
● instagram-scheduler.service - Instagram Automation Scheduler
     Loaded: loaded (/etc/systemd/system/instagram-scheduler.service; enabled; vendor preset: enabled)
     Active: active (running) since [DATE TIME]
   Main PID: [PID] (python)
      Tasks: 1 (limit: 1131)
✅ Scheduler service installed and started
```

**If deployment fails at any step:**
1. **Check error message** - script will tell you what failed
2. **Verify SSH key** is correct and accessible
3. **Check AWS instance** is running
4. **Verify security group** allows your IP on port 22

**Common Issues & Fixes:**
- **"SSH key file not found"** → Download/create key as described in Step 1
- **"Permission denied"** → Run `chmod 600 instagram-automation-key.pem`
- **"Connection refused"** → Check AWS instance is running and security group
- **"Upload failed"** → Check internet connection and try again

---

## Phase 4: Verify Everything Works

### Step 9: Check System Status
```bash
# Connect to AWS
ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com

# Go to bot directory
cd ~/instabot

# Check status
./status.sh
```

**Should see:**
- ✅ Scheduler service: "active (running)"
- ✅ Dashboard process: "Dashboard is running"
- ✅ No errors in output

### Step 6: Test Web Dashboard (DETAILED)
1. **Open your web browser** (Chrome, Safari, Firefox)
2. **Copy and paste this EXACT URL:**
   ```
   http://ec2-3-17-165-195.us-east-2.compute.amazonaws.com:5000
   ```
3. **Press Enter and wait 10-15 seconds** for the page to load

**What you SHOULD see:**
- ✅ **Title:** "🤖 Instagram Bot Dashboard"
- ✅ **4 stat cards** showing:
  - Currently Following: 0 (initially)
  - Total Unfollowed: 0 (initially)  
  - Follows (24h): 0 (initially)
  - Unfollows (24h): 0 (initially)
- ✅ **"📋 Recent Activity"** section (may be empty initially)
- ✅ **"👥 Current Follows"** section (may be empty initially)
- ✅ **Blue refresh button** that works
- ✅ **Last Updated timestamp**

**If you see ERROR MESSAGES:**
- **"This site can't be reached"** → Dashboard isn't running, check Step 5
- **"Connection refused"** → Port 5000 blocked in security group
- **"Server Error"** → Dashboard crashed, check logs

**To fix dashboard issues:**
```bash
# Connect to AWS and restart dashboard
ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com
cd ~/instabot
source venv/bin/activate
pkill -f dashboard.py
nohup python dashboard.py > dashboard.log 2>&1 &
exit
```

### Step 7: Manual Bot Test (DETAILED)
**Connect to AWS and run test:**
```bash
# Connect to AWS (replace with your actual key name)
ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com

# Navigate to bot directory
cd ~/instabot

# Activate virtual environment
source venv/bin/activate

# Run the test
python test_bot.py
```

**EXACT Expected Output:**
```
🧪 Testing Instagram Bot...
✅ Chrome started
✅ Login completed
✅ Successfully navigated to target account
✅ All tests passed! Bot is ready for deployment.
🔒 Browser closed
```

**If test FAILS, you'll see:**
- **❌ Error initializing driver** → ChromeDriver issue
- **❌ Login failed** → Instagram blocked or wrong credentials
- **❌ Test failed: [error]** → Various issues

**To fix test failures:**
```bash
# Check Chrome and ChromeDriver versions
google-chrome --version
chromedriver --version

# Check if Instagram login works manually
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('https://www.instagram.com')
print('Instagram loaded:', driver.title)
driver.quit()
"

# Exit AWS after testing
exit
```

### Step 12: Check Scheduler Logs
```bash
# View scheduler logs
tail -f scheduler.log

# View system service logs
sudo journalctl -u instagram-scheduler -f

# Should see scheduled times and no errors
```

---

## Phase 5: Monitor First Automation Run

### Step 13: Trigger Manual Run (Optional)
```bash
# Force run the bot once to test full cycle
python complete_instagram_bot.py
```

**Watch for:**
- ✅ Chrome started
- ✅ Login completed
- ✅ Navigated to target accounts
- ✅ Collected followers
- ✅ Followed users
- ✅ Automation cycle completed

### Step 14: Verify Data Storage
```bash
# Check data files were created
ls -la instagram_data/
cat instagram_data/action_log.json | tail -5
```

### Step 15: Monitor Dashboard
1. **Refresh dashboard** in browser
2. **Should now see:**
   - Updated follow counts
   - Recent activity log
   - Timestamp updates

---

## Phase 6: Final Verification

### Step 16: Check All Services Running
```bash
# Check scheduler service
sudo systemctl status instagram-scheduler

# Check dashboard process
pgrep -f dashboard.py

# Check no zombie processes
ps aux | grep instagram
```

### Step 17: Test Scheduler Timing
```bash
# Check when next run is scheduled
sudo journalctl -u instagram-scheduler | tail -10

# Should show next scheduled times (10:00 AM and 6:00 PM)
```

### Step 18: Setup Monitoring Commands
```bash
# Create quick check alias
echo 'alias botcheck="cd ~/instabot && ./status.sh"' >> ~/.bashrc
source ~/.bashrc

# Test it
botcheck
```

---

## 🎯 Success Checklist

**✅ Before You're Done, Verify:**

- [ ] SSH connection works without errors
- [ ] `./status.sh` shows all services running
- [ ] Web dashboard loads at `http://ec2-3-128-30-19.us-east-2.compute.amazonaws.com:5000`
- [ ] `python test_bot.py` passes all tests
- [ ] Scheduler service is "active (running)"
- [ ] Dashboard shows in browser with no errors
- [ ] Can see bot activity in logs
- [ ] Data files are being created in `instagram_data/`

---

## 🚨 Troubleshooting Quick Fixes

**If scheduler not running:**
```bash
sudo systemctl restart instagram-scheduler
sudo systemctl status instagram-scheduler
```

**If dashboard not accessible:**
```bash
pkill -f dashboard.py
cd ~/instabot && source venv/bin/activate
nohup python dashboard.py > dashboard.log 2>&1 &
```

**If bot fails test:**
```bash
# Check Chrome/ChromeDriver
google-chrome --version
chromedriver --version
```

**Check AWS Security Group (DETAILED STEPS):**
1. **Go to AWS Console** → **EC2** → **Security Groups**
2. **Find your security group** (likely named `launch-wizard-X`)
3. **Click on the security group**
4. **Click "Inbound rules" tab**
5. **Verify you have these rules:**
   - **Type:** SSH, **Port:** 22, **Source:** Your IP (or 0.0.0.0/0)
   - **Type:** Custom TCP, **Port:** 5000, **Source:** Your IP (or 0.0.0.0/0)
6. **If missing, click "Edit inbound rules"**
7. **Click "Add rule"** and add the missing ports
8. **Click "Save rules"**

**To find your current IP:**
```bash
curl ifconfig.me
# Use this IP in the security group rules
```

---

## 🎉 You're Done!

**Your Instagram automation is now:**
- ✅ Running 24/7 on AWS
- ✅ Following 100 users/day from music accounts
- ✅ Auto-unfollowing after 48 hours  
- ✅ Monitored via web dashboard
- ✅ Scheduled to run at 10 AM and 6 PM daily
- ✅ Logging all activity
- ✅ Automatically restarting if it crashes

**Monitor at:** `http://ec2-3-128-30-19.us-east-2.compute.amazonaws.com:5000`

**Check status anytime:** `ssh -i instagram-automation-key.pem ubuntu@ec2-3-128-30-19.us-east-2.compute.amazonaws.com 'cd ~/instabot && ./status.sh'`

# Run the git history cleaning script
./clean_git_history.sh 