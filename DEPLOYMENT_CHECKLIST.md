# 📋 Deployment Checklist

Use this checklist to track your deployment progress.

## 🚀 Quick Start (TL;DR)

**Time Required:** ~30-45 minutes  
**Cost:** ~$6/month  
**End Result:** 24/7 Instagram bot with web dashboard

```bash
# 1. Create Hetzner server (Ubuntu 22.04, 4GB RAM)
# 2. Note server IP address
# 3. Run deployment script:
./deploy_to_hetzner.sh YOUR_SERVER_IP

# 4. SSH to server and run setup:
ssh -i ~/.ssh/hetzner_instagram_bot root@YOUR_SERVER_IP
./setup_hetzner_server.sh

# 5. Configure bot:
sudo -u bot nano /home/bot/instagram-automation/config.json

# 6. Start services:
systemctl start instagram-bot instagram-dashboard
systemctl enable instagram-bot instagram-dashboard

# 7. Access dashboard:
# http://YOUR_SERVER_IP:5000
```

---

## ✅ Phase 1: Server Setup

- [ ] **1.1** Hetzner account created
- [ ] **1.2** Server created (Ubuntu 22.04, 4GB RAM)
- [ ] **1.3** Server IP noted: `_________________`
- [ ] **1.4** SSH access confirmed
- [ ] **1.5** System updated (`apt update && apt upgrade -y`)

---

## ✅ Phase 2: Deployment Preparation

- [ ] **2.1** Navigate to project directory
- [ ] **2.2** Run deployment script: `./deploy_to_hetzner.sh YOUR_SERVER_IP`
- [ ] **2.3** Files uploaded to server
- [ ] **2.4** Upload verified

---

## ✅ Phase 3: Server Configuration

- [ ] **3.1** SSH to server
- [ ] **3.2** Setup script executable: `chmod +x setup_hetzner_server.sh`
- [ ] **3.3** Setup script completed: `./setup_hetzner_server.sh`
- [ ] **3.4** Deployment package extracted
- [ ] **3.5** Files copied to bot directory
- [ ] **3.6** Python dependencies installed

---

## ✅ Phase 4: Bot Configuration

- [ ] **4.1** Config file edited: `sudo -u bot nano /home/bot/instagram-automation/config.json`
- [ ] **4.2** Instagram credentials added
- [ ] **4.3** Target accounts configured
- [ ] **4.4** Dashboard password set
- [ ] **4.5** Configuration saved

---

## ✅ Phase 5: Service Deployment

- [ ] **5.1** Instagram bot service started: `systemctl start instagram-bot`
- [ ] **5.2** Dashboard service started: `systemctl start instagram-dashboard`
- [ ] **5.3** Services enabled for auto-start
- [ ] **5.4** Service status verified (both "active (running)")
- [ ] **5.5** Logs checked and working

---

## ✅ Phase 6: Remote Access

- [ ] **6.1** Dashboard accessible: `http://YOUR_SERVER_IP:5000`
- [ ] **6.2** Dashboard login working
- [ ] **6.3** Statistics displayed correctly
- [ ] **6.4** Password changed from default
- [ ] **6.5** Notifications configured (if desired)

---

## ✅ Phase 7: Testing

- [ ] **7.1** Manual test run completed
- [ ] **7.2** Follow/unfollow functionality confirmed
- [ ] **7.3** Dashboard updates working
- [ ] **7.4** Logs show proper activity
- [ ] **7.5** Scheduled automation verified

---

## ✅ Phase 8: Final Verification

- [ ] **8.1** Both services running: `systemctl status instagram-bot instagram-dashboard`
- [ ] **8.2** Dashboard accessible remotely
- [ ] **8.3** Bot following users successfully
- [ ] **8.4** Auto-scheduling working (check next day)
- [ ] **8.5** 48-hour unfollow working (check after 48h)

---

## 🔧 Essential Commands

### Service Management
```bash
# Check status
systemctl status instagram-bot instagram-dashboard

# Restart services
systemctl restart instagram-bot instagram-dashboard

# View logs
journalctl -u instagram-bot -f
journalctl -u instagram-dashboard -f
```

### Configuration Changes
```bash
# Edit config
sudo -u bot nano /home/bot/instagram-automation/config.json

# Restart after changes
systemctl restart instagram-bot
```

### System Monitoring
```bash
# System resources
htop
df -h
free -h

# Recent activity logs
journalctl -u instagram-bot --since "1 hour ago"
```

---

## 🚨 Troubleshooting Quick Fixes

### Bot Not Working
```bash
# Check logs
journalctl -u instagram-bot -f

# Restart service
systemctl restart instagram-bot

# Test manually
sudo -u bot bash -c "cd /home/bot/instagram-automation && source venv/bin/activate && python server_bot.py"
```

### Dashboard Not Accessible
```bash
# Check service
systemctl status instagram-dashboard

# Check firewall
ufw status

# Test locally
curl http://localhost:5000
```

### Chrome Issues
```bash
# Re-run setup (installs latest Chrome/ChromeDriver)
./setup_hetzner_server.sh
```

---

## 📊 Success Indicators

✅ **Dashboard shows:** `http://YOUR_SERVER_IP:5000`  
✅ **Services status:** Both "active (running)"  
✅ **Daily follows:** 15 new follows per day  
✅ **Auto unfollows:** Users unfollowed after 48 hours  
✅ **Statistics:** Updating in real-time  
✅ **Notifications:** Working (if enabled)  

---

## 📱 Contact & Support

If you encounter issues:

1. **Check logs first:** `journalctl -u instagram-bot -f`
2. **Verify configuration:** Config file syntax and credentials
3. **Restart services:** Often fixes temporary issues
4. **Re-run setup:** If Chrome/system issues

**Your Bot Dashboard:** `http://YOUR_SERVER_IP:5000`  
**Monthly Cost:** ~$6/month  
**Maintenance:** ~5 minutes/day  

🎉 **Congratulations on your autonomous Instagram bot deployment!** 