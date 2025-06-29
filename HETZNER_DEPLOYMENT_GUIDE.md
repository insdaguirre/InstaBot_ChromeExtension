# 🚀 Instagram Bot Hetzner Deployment Guide

Complete step-by-step guide to deploy your Instagram automation bot on Hetzner Cloud.

## 📋 Prerequisites

- [ ] Hetzner Cloud account
- [ ] Instagram account credentials
- [ ] Local terminal/command line access
- [ ] Basic SSH knowledge

## 💰 Cost Estimate
- **Hetzner Cloud Server (4GB):** €5.83/month (~$6/month)
- **Total Monthly Cost:** ~$6/month

---

## 🏗️ Phase 1: Server Setup

### Step 1: Create Hetzner Cloud Server

1. **Login to Hetzner Cloud Console**
   - Go to [https://console.hetzner.cloud/](https://console.hetzner.cloud/)
   - Login to your account

2. **Create New Server**
   - Click "Add Server"
   - **Location:** Choose closest to you (e.g., Nuremberg, Germany)
   - **Image:** Ubuntu 22.04
   - **Type:** Standard - CPX21 (4GB RAM, 2 vCPUs, 80GB SSD)
   - **SSH Key:** Add your SSH key or create password
   - **Name:** `instagram-bot-server`

3. **Configure Firewall (Optional but Recommended)**
   - Create firewall rule
   - **Inbound Rules:**
     - SSH (Port 22) - Your IP only
     - HTTP (Port 5000) - Your IP only (for dashboard)
   - Apply to server

4. **Wait for Server Creation**
   - Server will be ready in ~2 minutes
   - **Note down the server IP address** (you'll need this)

### Step 2: Initial Server Access

1. **SSH to Server**
   ```bash
   ssh -i ~/.ssh/hetzner_instagram_bot root@YOUR_SERVER_IP
   ```
   
2. **Update System**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Verify Server Info**
   ```bash
   # Check system info
   uname -a
   free -h
   df -h
   ```

---

## 📦 Phase 2: Prepare Deployment

### Step 3: Prepare Deployment Package (Local Machine)

1. **Navigate to Project Directory**
   ```bash
   cd "instagram automation"
   ```

2. **Run Deployment Script**
   ```bash
   ./deploy_to_hetzner.sh YOUR_SERVER_IP
   ```
   
   This creates:
   - `instagram-bot-deployment.tar.gz` - Bot files
   - Deployment instructions

3. **Verify Files Created**
   ```bash
   ls -la *.tar.gz
   # Should see: instagram-bot-deployment.tar.gz
   ```

### Step 4: Upload Files to Server

1. **Copy Deployment Package**
   ```bash
   scp -i ~/.ssh/hetzner_instagram_bot instagram-bot-deployment.tar.gz root@YOUR_SERVER_IP:~/
   scp -i ~/.ssh/hetzner_instagram_bot setup_hetzner_server.sh root@YOUR_SERVER_IP:~/
   ```

2. **Verify Upload**
   ```bash
   ssh -i ~/.ssh/hetzner_instagram_bot root@YOUR_SERVER_IP "ls -la ~/"
   # Should see both files
   ```

---

## ⚙️ Phase 3: Server Configuration

### Step 5: Run Server Setup Script

1. **SSH to Server**
   ```bash
   ssh -i ~/.ssh/hetzner_instagram_bot root@YOUR_SERVER_IP
   ```

2. **Make Setup Script Executable**
   ```bash
   chmod +x setup_hetzner_server.sh
   ```

3. **Run Setup Script**
   ```bash
   ./setup_hetzner_server.sh
   ```
   
   This will:
   - ✅ Install Python 3, pip, venv
   - ✅ Install Google Chrome & ChromeDriver
   - ✅ Create `bot` user account
   - ✅ Setup project directory
   - ✅ Install systemd services
   - ✅ Configure firewall
   - ✅ Setup log rotation

4. **Wait for Completion**
   - Script takes ~5-10 minutes
   - Should end with "✅ Instagram Bot Server Setup Complete!"

### Step 6: Deploy Bot Files

1. **Extract Deployment Package**
   ```bash
   tar -xzf instagram-bot-deployment.tar.gz
   cd deployment_package
   ```

2. **Copy Files to Bot Directory**
   ```bash
   cp * /home/bot/instagram-automation/
   chown -R bot:bot /home/bot/instagram-automation/
   ```

3. **Install Python Dependencies**
   ```bash
   sudo -u bot bash -c "cd /home/bot/instagram-automation && source venv/bin/activate && pip install -r requirements_server.txt"
   ```

---

## 🔧 Phase 4: Configuration

### Step 7: Configure Bot Settings

1. **Edit Configuration File**
   ```bash
   sudo -u bot nano /home/bot/instagram-automation/config.json
   ```

2. **Update Configuration**
   ```json
   {
     "instagram": {
       "username": "YOUR_INSTAGRAM_USERNAME",
       "password": "YOUR_INSTAGRAM_PASSWORD",
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
         "sender_email": "your-email@gmail.com",
         "sender_password": "your-app-password",
         "recipient_email": "your-email@gmail.com"
       },
       "discord": {
         "enabled": false,
         "webhook_url": ""
       }
     },
     "web_dashboard": {
       "enabled": true,
       "port": 5000,
       "password": "your-secure-password"
     }
   }
   ```

3. **Save and Exit**
   - Press `Ctrl + X`
   - Press `Y` to save
   - Press `Enter` to confirm

### Step 8: Test Bot Configuration

1. **Test Bot Manually (Optional)**
   ```bash
   sudo -u bot bash -c "cd /home/bot/instagram-automation && source venv/bin/activate && python instagram_gui.py"
   ```
   
   **Note:** This will run in headless mode on server (no GUI)

---

## 🚀 Phase 5: Service Deployment

### Step 9: Start Services

1. **Start Instagram Bot Service**
   ```bash
   systemctl start instagram-bot
   systemctl enable instagram-bot
   ```

2. **Start Web Dashboard Service**
   ```bash
   systemctl start instagram-dashboard
   systemctl enable instagram-dashboard
   ```

3. **Check Service Status**
   ```bash
   systemctl status instagram-bot
   systemctl status instagram-dashboard
   ```
   
   Both should show "active (running)" in green

### Step 10: Verify Services

1. **Check Bot Logs**
   ```bash
   journalctl -u instagram-bot -f
   ```
   
   Should show:
   ```
   🚀 Server Instagram Bot initialized
   📝 Created default config file
   ✅ Configuration loaded successfully
   ```

2. **Check Dashboard Logs**
   ```bash
   journalctl -u instagram-dashboard -f
   ```
   
   Should show:
   ```
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:5000
   ```

3. **Test Network Connectivity**
   ```bash
   curl http://localhost:5000
   # Should return HTML content
   ```

---

## 🌐 Phase 6: Remote Access Setup

### Step 11: Configure Remote Access

1. **Test Dashboard Access**
   - Open browser on your local machine
   - Go to: `http://YOUR_SERVER_IP:5000`
   - Should see Instagram Bot Dashboard

2. **Login to Dashboard**
   - Enter password from config.json
   - Should see dashboard with statistics

3. **Update Dashboard Password (Recommended)**
   ```bash
   sudo -u bot nano /home/bot/instagram-automation/config.json
   # Change "password": "your-secure-password"
   systemctl restart instagram-dashboard
   ```

### Step 12: Configure Notifications (Optional)

#### Email Notifications:
1. **Setup Gmail App Password** (if using Gmail)
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate app password for "Mail"

2. **Update Config**
   ```bash
   sudo -u bot nano /home/bot/instagram-automation/config.json
   ```
   
   Update email section:
   ```json
   "email": {
     "enabled": true,
     "sender_email": "your-email@gmail.com",
     "sender_password": "your-app-password",
     "recipient_email": "your-email@gmail.com"
   }
   ```

#### Discord Notifications:
1. **Create Discord Webhook**
   - Go to Discord server settings
   - Webhooks → Create Webhook
   - Copy webhook URL

2. **Update Config**
   ```json
   "discord": {
     "enabled": true,
     "webhook_url": "https://discord.com/api/webhooks/..."
   }
   ```

3. **Restart Services**
   ```bash
   systemctl restart instagram-bot
   ```

---

## ✅ Phase 7: Testing & Monitoring

### Step 13: Test Full Functionality

1. **Manual Test Run**
   ```bash
   # Trigger manual follow cycle
   sudo -u bot bash -c "cd /home/bot/instagram-automation && source venv/bin/activate && python -c \"
   from server_bot import ServerInstagramBot
   bot = ServerInstagramBot()
   bot.run_follow_cycle()
   \""
   ```

2. **Check Results**
   ```bash
   # Check if users were followed
   cat /home/bot/instagram-automation/bot_data/follows.json
   cat /home/bot/instagram-automation/bot_data/action_log.json
   ```

3. **Dashboard Testing**
   - Refresh dashboard in browser
   - Should see updated statistics
   - Test configuration changes

### Step 14: Monitor Services

1. **View Live Logs**
   ```bash
   # Bot logs
   journalctl -u instagram-bot -f
   
   # Dashboard logs
   journalctl -u instagram-dashboard -f
   ```

2. **Check System Resources**
   ```bash
   htop  # or top
   df -h
   free -h
   ```

3. **Verify Schedule**
   - Bot should automatically run at configured times
   - Check logs around scheduled times
   - Verify follows/unfollows happen as expected

---

## 🔧 Phase 8: Ongoing Management

### Daily Operations

1. **Check Bot Status**
   ```bash
   systemctl status instagram-bot instagram-dashboard
   ```

2. **View Recent Activity**
   - Dashboard: `http://YOUR_SERVER_IP:5000`
   - Logs: `journalctl -u instagram-bot --since "1 hour ago"`

3. **Update Target Accounts**
   - Use web dashboard OR
   - Edit config.json and restart services

### Maintenance Commands

```bash
# Restart services
systemctl restart instagram-bot instagram-dashboard

# View logs
journalctl -u instagram-bot -n 100
journalctl -u instagram-dashboard -n 100

# Check disk space
df -h

# Update bot files (if needed)
systemctl stop instagram-bot instagram-dashboard
# Upload new files
systemctl start instagram-bot instagram-dashboard
```

### Troubleshooting

1. **Bot Not Following**
   - Check logs: `journalctl -u instagram-bot -f`
   - Verify Instagram credentials
   - Check target account accessibility

2. **Dashboard Not Accessible**
   - Check service: `systemctl status instagram-dashboard`
   - Verify firewall: `ufw status`
   - Test locally: `curl http://localhost:5000`

3. **Chrome/WebDriver Issues**
   - Update ChromeDriver: Re-run setup script
   - Check headless mode: Logs should show "headless mode"

---

## 📊 Success Metrics

Your deployment is successful when:

- ✅ **Services Running:** Both services show "active (running)"
- ✅ **Dashboard Accessible:** Can access dashboard remotely
- ✅ **Bot Following:** Logs show successful follows
- ✅ **Scheduling Working:** Automatic follows at configured times
- ✅ **48h Unfollows:** Users unfollowed after 48 hours
- ✅ **Statistics Updating:** Dashboard shows current stats

## 🚨 Security Notes

- ✅ Change default dashboard password
- ✅ Restrict firewall to your IP only
- ✅ Keep Instagram credentials secure
- ✅ Monitor logs regularly
- ✅ Don't exceed Instagram rate limits

---

## 🎉 Congratulations!

You now have a fully autonomous Instagram bot running 24/7 with remote control capabilities!

**Total Setup Time:** ~30-45 minutes
**Monthly Cost:** ~$6/month
**Maintenance:** ~5 minutes/day

Your bot will:
- Follow users from target accounts daily
- Unfollow users after 48 hours
- Send you notifications
- Provide real-time dashboard access
- Run completely autonomously

**Dashboard:** `http://YOUR_SERVER_IP:5000` 