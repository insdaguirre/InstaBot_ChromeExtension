# 🥧 Raspberry Pi Instagram Automation Deployment Guide

**The BEST Oracle Cloud Alternative - $0/month forever with full control!**

## 🎯 Why Raspberry Pi is Perfect for Instagram Automation

### **Cost Comparison (3 Years)**
| Solution | Initial Cost | Monthly Cost | 3-Year Total |
|----------|--------------|--------------|--------------|
| **Oracle Cloud** | $0 | $0* | $0* |
| **Raspberry Pi 4** | $100 | $3 | $208 |
| **AWS** | $0 | $80 | $2,880 |
| **VPS** | $0 | $6 | $216 |

*Oracle Cloud risk: Service can be discontinued, accounts can be suspended

### **Raspberry Pi Advantages**
- ✅ **True ownership** - No account suspensions
- ✅ **100% uptime control** - No cloud provider outages
- ✅ **Zero ongoing costs** - Just electricity (~$36/year)
- ✅ **Physical access** - Debug issues directly
- ✅ **Privacy** - Your data never leaves your home
- ✅ **Learning experience** - Gain valuable skills
- ✅ **Expandable** - Add more Pis as needed

## 🛒 Shopping List

### **Essential Hardware**
```
Raspberry Pi 4B (8GB): $75
   └─ 8GB RAM handles multiple Instagram accounts easily

MicroSD Card (64GB Class 10): $15
   └─ SanDisk Extreme Pro recommended for speed

Power Supply (USB-C, 3A): $10
   └─ Official Raspberry Pi charger preferred

Ethernet Cable: $5
   └─ More reliable than WiFi for 24/7 operation

Total: $105
```

### **Optional Upgrades**
```
Case with Fan: $15
   └─ Keeps Pi cool during heavy usage

External SSD (120GB): $25
   └─ Better performance and reliability

PoE HAT: $20
   └─ Power over Ethernet for clean setup

USB Power Bank: $30
   └─ Backup power during outages

Total with upgrades: $195
```

## 🚀 Step-by-Step Setup Guide

### **Step 1: Prepare Raspberry Pi OS**

**Download and Flash Raspberry Pi OS:**
1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS Lite (64-bit)** to SD card
3. Enable SSH before first boot:
   ```bash
   # Enable SSH
   touch /Volumes/boot/ssh
   
   # Configure WiFi (optional)
   cat > /Volumes/boot/wpa_supplicant.conf << EOF
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   
   network={
       ssid="YOUR_WIFI_NAME"
       psk="YOUR_WIFI_PASSWORD"
   }
   EOF
   ```

### **Step 2: Initial Raspberry Pi Configuration**

**First Login:**
```bash
# SSH into your Pi (find IP in router admin or use nmap)
ssh pi@192.168.1.XXX
# Default password: raspberry

# Update system
sudo apt update && sudo apt upgrade -y

# Configure Pi
sudo raspi-config
```

**In raspi-config menu:**
1. **Change User Password** - Set secure password
2. **Network Options** - Configure WiFi if needed
3. **Boot Options** - Desktop/CLI: Console Autologin
4. **Advanced Options** - Memory Split: 16MB (minimal GPU memory)
5. **Advanced Options** - Expand Filesystem
6. **Finish** and reboot

### **Step 3: Install Instagram Automation**

**Download and run the portable setup script:**
```bash
# Download the setup script
wget https://raw.githubusercontent.com/YOUR_REPO/portable_automation_setup.sh

# Make executable and run
chmod +x portable_automation_setup.sh
./portable_automation_setup.sh
```

**Manual Setup (if needed):**
```bash
# Clone your automation repository
git clone https://github.com/YOUR_USERNAME/instagram-automation.git
cd instagram-automation

# Run setup
chmod +x setup.sh
./setup.sh
```

### **Step 4: Configure Instagram Automation**

**Edit configuration files:**
```bash
cd ~/instagram-automation

# Configure Instagram credentials
nano .env
```

**Update .env file:**
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
DAILY_FOLLOW_LIMIT=100
FOLLOWERS_PER_ACCOUNT=25
FOLLOW_SCHEDULE=10:00
UNFOLLOW_SCHEDULE=22:00
MIN_DELAY=15
MAX_DELAY=45
HEADLESS=true
```

**Configure target accounts:**
```bash
nano config/automation_config.json
```

### **Step 5: Start Automation Services**

```bash
# Start the automation
./scripts/control.sh start

# Check status
./scripts/control.sh status

# View logs
./scripts/control.sh logs
```

**Access web dashboard:**
```
http://192.168.1.XXX:5000
```
*(Replace XXX with your Pi's IP address)*

## 🔧 Raspberry Pi Optimization

### **Performance Optimization**

**1. Enable GPU memory split:**
```bash
sudo raspi-config
# Advanced Options > Memory Split > 16
```

**2. Optimize Chrome for Pi:**
```bash
# Create Chrome launch script
cat > ~/instagram-automation/launch_chrome.sh << 'EOF'
#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
google-chrome \
  --headless \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --disable-background-timer-throttling \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --memory-pressure-off \
  --max_old_space_size=2048
EOF
chmod +x ~/instagram-automation/launch_chrome.sh
```

**3. Enable swap for extra memory:**
```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### **Reliability Improvements**

**1. Auto-start on boot:**
```bash
# Add to crontab
crontab -e

# Add this line:
@reboot cd /home/pi/instagram-automation && ./scripts/control.sh start
```

**2. Automatic restart on failure:**
```bash
# Create monitoring script
cat > ~/instagram-automation/scripts/monitor.sh << 'EOF'
#!/bin/bash
# Check if automation is running, restart if not

cd ~/instagram-automation

if ! ./scripts/control.sh status | grep -q "Running"; then
    echo "$(date): Automation stopped, restarting..." >> logs/monitor.log
    ./scripts/control.sh start
fi
EOF

chmod +x ~/instagram-automation/scripts/monitor.sh

# Add to crontab (check every 5 minutes)
crontab -e
# Add: */5 * * * * /home/pi/instagram-automation/scripts/monitor.sh
```

**3. Daily health check:**
```bash
cat > ~/instagram-automation/scripts/health_check.sh << 'EOF'
#!/bin/bash
# Daily health check and maintenance

LOG_FILE="logs/health_check.log"
echo "$(date): Daily health check started" >> $LOG_FILE

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Warning - Disk usage: ${DISK_USAGE}%" >> $LOG_FILE
    # Clean old logs
    find logs/ -name "*.log" -mtime +7 -delete
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "$(date): Memory usage: ${MEM_USAGE}%" >> $LOG_FILE

# Restart services daily to prevent memory leaks
echo "$(date): Daily restart" >> $LOG_FILE
./scripts/control.sh restart

echo "$(date): Health check completed" >> $LOG_FILE
EOF

chmod +x ~/instagram-automation/scripts/health_check.sh

# Add to crontab (daily at 3 AM)
crontab -e
# Add: 0 3 * * * /home/pi/instagram-automation/scripts/health_check.sh
```

## 🌐 Network Configuration

### **Port Forwarding for Remote Access**

**Configure router to access Pi from anywhere:**

1. **Find Pi's IP address:**
   ```bash
   hostname -I
   ```

2. **Access router admin panel** (usually 192.168.1.1 or 192.168.0.1)

3. **Set up port forwarding:**
   ```
   Service: Instagram-Automation
   External Port: 5000
   Internal IP: 192.168.1.XXX (your Pi's IP)
   Internal Port: 5000
   Protocol: TCP
   ```

4. **Find your public IP:**
   ```bash
   curl ifconfig.me
   ```

5. **Access dashboard from anywhere:**
   ```
   http://YOUR_PUBLIC_IP:5000
   ```

### **Dynamic DNS Setup (Optional)**

**For easy access with a domain name:**

1. **Sign up for free DDNS** (NoIP, DuckDNS, etc.)

2. **Install DDNS client on Pi:**
   ```bash
   # Example for DuckDNS
   mkdir ~/duckdns
   cd ~/duckdns
   echo 'echo url="https://www.duckdns.org/update?domains=YOURSUBDOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -' > duck.sh
   chmod 700 duck.sh
   
   # Add to crontab (update every 5 minutes)
   crontab -e
   # Add: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
   ```

3. **Access with domain:**
   ```
   http://yourname.duckdns.org:5000
   ```

## 🔒 Security Best Practices

### **SSH Security**

**1. Change default SSH port:**
```bash
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222
sudo systemctl restart ssh
```

**2. Disable password authentication:**
```bash
# Generate SSH key on your computer
ssh-keygen -t rsa -b 4096

# Copy public key to Pi
ssh-copy-id -p 2222 pi@YOUR_PI_IP

# Disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

### **Firewall Configuration**

```bash
# Install and configure UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (use your custom port)
sudo ufw allow 2222/tcp

# Allow dashboard
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable
```

### **Automatic Security Updates**

```bash
# Install unattended upgrades
sudo apt install unattended-upgrades

# Configure automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📊 Monitoring and Maintenance

### **System Monitoring Dashboard**

Your Pi includes a comprehensive web dashboard at `http://PI_IP:5000` with:

- 🤖 **Service Status** - Automation running/stopped
- 📊 **System Resources** - CPU, RAM, disk usage
- 📈 **Daily Progress** - Follows completed today
- ⚙️ **Configuration** - Current settings
- 📝 **Live Logs** - Real-time automation logs
- 🔧 **Remote Controls** - Start/stop/restart services

### **Mobile Access**

**Access your Pi from your phone:**
1. Connect to same WiFi network
2. Open browser to `http://PI_IP:5000`
3. Bookmark for quick access
4. Monitor automation on-the-go

### **Email Notifications (Optional)**

**Get notified of issues:**
```bash
# Install mail utilities
sudo apt install ssmtp mailutils

# Configure email
sudo nano /etc/ssmtp/ssmtp.conf
# Add your email settings

# Test email
echo "Pi automation started" | mail -s "Instagram Automation Alert" your@email.com
```

## 🚛 Migration and Backup

### **Complete Backup Strategy**

**1. Automatic daily backups:**
```bash
# Already configured in setup script
./scripts/backup.sh
```

**2. Full SD card image backup:**
```bash
# On your computer (Mac/Linux)
sudo dd if=/dev/disk2 of=pi-backup-$(date +%Y%m%d).img bs=1m

# On Windows, use Win32DiskImager
```

**3. Cloud backup (optional):**
```bash
# Sync to Google Drive, Dropbox, etc.
rclone sync ~/instagram-automation/backups/ gdrive:/pi-backups/
```

### **Migration to New Pi**

**Super easy migration process:**

1. **Create backup on old Pi:**
   ```bash
   ./scripts/backup.sh
   ```

2. **Set up new Pi** (follow setup guide)

3. **Transfer backup:**
   ```bash
   scp backup_20240101_120000.tar.gz pi@NEW_PI_IP:~/
   ```

4. **Restore on new Pi:**
   ```bash
   cd ~/instagram-automation
   ./scripts/restore.sh ~/backup_20240101_120000.tar.gz
   ./scripts/control.sh start
   ```

**Migration time: 10 minutes!**

## 💡 Pro Tips

### **Multiple Account Management**

**Run multiple Instagram accounts:**
```bash
# Create separate directories
mkdir ~/instagram-automation-account2
cd ~/instagram-automation-account2

# Copy and configure
cp -r ~/instagram-automation/* .
nano .env  # Configure for account 2
nano config/automation_config.json

# Start on different port
sed -i 's/5000/5001/g' web_dashboard.py
./scripts/control.sh start
```

### **Performance Monitoring**

**Monitor Pi performance:**
```bash
# CPU temperature
vcgencmd measure_temp

# CPU speed
vcgencmd measure_clock arm

# Memory usage
free -h

# Disk usage
df -h
```

### **Troubleshooting Common Issues**

**Pi running slow:**
```bash
# Check for throttling
vcgencmd get_throttled
# 0x0 = no throttling
# Any other value indicates thermal/voltage issues

# Solutions:
# 1. Add heatsink/fan
# 2. Check power supply (use official 3A charger)
# 3. Reduce Chrome memory usage
```

**Automation not starting:**
```bash
# Check logs
./scripts/control.sh logs

# Check Chrome installation
google-chrome --version

# Test virtual display
DISPLAY=:99 google-chrome --headless --dump-dom https://google.com
```

## 🎉 Success! You now have:

- ✅ **$0/month Instagram automation** (just electricity costs)
- ✅ **100% control** - No account suspensions or service changes
- ✅ **True ownership** - Your hardware, your rules
- ✅ **Professional monitoring** - Web dashboard and logging
- ✅ **Easy migration** - Move to new Pi in 10 minutes
- ✅ **No vendor lock-in** - Works on any Pi or Ubuntu server
- ✅ **Expandable** - Add more Pis as you grow
- ✅ **Privacy-focused** - Your data never leaves your home

**Your Instagram automation is now running 24/7 on your own hardware!**

---

*This setup is infinitely better than Oracle Cloud because YOU control everything. No one can suspend your "account" or discontinue the "service" - it's YOUR Raspberry Pi!* 