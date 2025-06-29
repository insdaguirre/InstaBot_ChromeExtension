#!/usr/bin/env python3
"""
Instagram Automation Server Bot - Autonomous Deployment Version
Runs 24/7 on server, reads config file for settings, sends notifications
"""
import json
import time
import logging
import schedule
import smtplib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
import signal

# Import the bot logic from our GUI version
from instagram_gui import InstagramBotGUI

class ServerInstagramBot:
    def __init__(self):
        self.data_dir = Path('bot_data')
        self.data_dir.mkdir(exist_ok=True)
        
        self.config_file = Path('config.json')
        self.running = True
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.logger.info("🚀 Server Instagram Bot initialized")
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler - daily rotation
        today = datetime.now().strftime("%Y%m%d")
        file_handler = logging.FileHandler(log_dir / f'bot_{today}.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup logger
        self.logger = logging.getLogger('ServerBot')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def load_config(self):
        """Load configuration from config.json"""
        default_config = {
            "instagram": {
                "username": "",
                "password": "",
                "target_accounts": ["deadmau5", "skrillex", "1001tracklists"],
                "users_per_account": 5,
                "daily_follow_limit": 15,
                "unfollow_after_hours": 48
            },
            "schedule": {
                "follow_time": "09:00",
                "unfollow_time": "15:00",
                "timezone": "UTC"
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": "",
                    "recipient_email": "",
                    "daily_report": True,
                    "error_alerts": True
                },
                "discord": {
                    "enabled": False,
                    "webhook_url": "",
                    "daily_report": True,
                    "error_alerts": True
                }
            },
            "web_dashboard": {
                "enabled": True,
                "port": 5000,
                "password": "admin123",
                "host": "0.0.0.0"
            },
            "bot_settings": {
                "headless": True,
                "follow_delay_min": 15,
                "follow_delay_max": 30,
                "max_retries": 3
            }
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.logger.info(f"📝 Created default config file: {self.config_file}")
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            self.logger.info("✅ Configuration loaded successfully")
            return config
        except Exception as e:
            self.logger.error(f"❌ Error loading config: {e}")
            return default_config
            
    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("💾 Configuration saved")
        except Exception as e:
            self.logger.error(f"❌ Error saving config: {e}")
            
    def send_email_notification(self, subject, body, is_error=False):
        """Send email notification"""
        try:
            email_config = self.config['notifications']['email']
            if not email_config['enabled']:
                return
                
            if is_error and not email_config['error_alerts']:
                return
                
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = f"[Instagram Bot] {subject}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            text = msg.as_string()
            server.sendmail(email_config['sender_email'], email_config['recipient_email'], text)
            server.quit()
            
            self.logger.info(f"📧 Email sent: {subject}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send email: {e}")
            
    def send_discord_notification(self, message, is_error=False):
        """Send Discord webhook notification"""
        try:
            discord_config = self.config['notifications']['discord']
            if not discord_config['enabled']:
                return
                
            if is_error and not discord_config['error_alerts']:
                return
                
            color = 0xff0000 if is_error else 0x00ff00
            
            payload = {
                "embeds": [{
                    "title": "Instagram Bot Update",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            
            response = requests.post(discord_config['webhook_url'], json=payload)
            if response.status_code == 204:
                self.logger.info(f"📱 Discord notification sent")
            else:
                self.logger.error(f"❌ Discord notification failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to send Discord notification: {e}")
            
    def get_bot_stats(self):
        """Get current bot statistics"""
        try:
            follows_file = self.data_dir / 'follows.json'
            action_log_file = self.data_dir / 'action_log.json'
            
            follows_data = {}
            action_log = []
            
            if follows_file.exists():
                with open(follows_file, 'r') as f:
                    follows_data = json.load(f)
                    
            if action_log_file.exists():
                with open(action_log_file, 'r') as f:
                    action_log = json.load(f)
            
            # Calculate stats
            now = datetime.now()
            today = now.date()
            
            following = [u for u, d in follows_data.items() if d.get('status') == 'following']
            unfollowed = [u for u, d in follows_data.items() if d.get('status') == 'unfollowed']
            
            today_follows = len([
                a for a in action_log 
                if a.get('action') == 'follow' 
                and datetime.fromisoformat(a['timestamp']).date() == today
            ])
            
            today_unfollows = len([
                a for a in action_log 
                if a.get('action') == 'unfollow' 
                and datetime.fromisoformat(a['timestamp']).date() == today
            ])
            
            return {
                'total_following': len(following),
                'total_unfollowed': len(unfollowed),
                'today_follows': today_follows,
                'today_unfollows': today_unfollows,
                'last_action': action_log[-1]['timestamp'] if action_log else None,
                'status': 'running' if self.running else 'stopped'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting stats: {e}")
            return {}
            
    def send_daily_report(self):
        """Send daily activity report"""
        try:
            stats = self.get_bot_stats()
            
            report = f"""📊 Instagram Bot Daily Report - {datetime.now().strftime('%B %d, %Y')}

✅ Status: {stats.get('status', 'unknown').title()}
👥 Currently Following: {stats.get('total_following', 0)} users
🔄 Total Unfollowed: {stats.get('total_unfollowed', 0)} users

📈 Today's Activity:
• Followed: {stats.get('today_follows', 0)} new users
• Unfollowed: {stats.get('today_unfollows', 0)} users

🎯 Target Accounts: {', '.join(self.config['instagram']['target_accounts'])}
⚙️ Daily Limit: {self.config['instagram']['daily_follow_limit']} follows

{f"🕒 Last Action: {stats.get('last_action', 'None')}" if stats.get('last_action') else "📋 No actions today"}

---
Autonomous Instagram Bot Server
"""
            
            # Send email report
            self.send_email_notification("Daily Report", report)
            
            # Send Discord report
            self.send_discord_notification(report)
            
            self.logger.info("📊 Daily report sent")
            
        except Exception as e:
            self.logger.error(f"❌ Error sending daily report: {e}")
            
    def run_follow_cycle(self):
        """Run the follow cycle"""
        try:
            self.logger.info("🚀 Starting follow cycle")
            
            # Check configuration
            instagram_config = self.config.get('instagram', {})
            username = instagram_config.get('username', '')
            password = instagram_config.get('password', '')
            
            if not username or not password:
                self.logger.warning("⚠️ Instagram credentials not configured. Use web dashboard to set them.")
                return
            
            # Check daily limit
            stats = self.get_bot_stats()
            if stats.get('today_follows', 0) >= instagram_config.get('daily_follow_limit', 15):
                self.logger.info(f"📊 Daily follow limit reached ({instagram_config.get('daily_follow_limit', 15)})")
                return
                
            # Create bot instance
            bot = InstagramBotGUI(
                username,
                password,
                instagram_config.get('target_accounts', ['deadmau5', 'skrillex', '1001tracklists']),
                instagram_config.get('users_per_account', 5)
            )
            
            # Initialize driver
            if not bot.init_driver(show_browser=False):  # Always headless on server
                raise Exception("Failed to initialize Chrome driver")
                
            # Login
            if not bot.login():
                raise Exception("Failed to login to Instagram")
                
            self.logger.info("✅ Bot logged in successfully")
            
            # Follow users from target accounts
            total_follows = 0
            for account in instagram_config['target_accounts']:
                try:
                    follows = bot.follow_users_from_account(account)
                    total_follows += follows
                    self.logger.info(f"📊 Followed {follows} users from @{account}")
                    
                    # Check if we've hit daily limit
                    current_stats = self.get_bot_stats()
                    if current_stats.get('today_follows', 0) >= instagram_config['daily_follow_limit']:
                        self.logger.info("📊 Daily follow limit reached, stopping")
                        break
                        
                except Exception as e:
                    self.logger.error(f"❌ Error with account @{account}: {e}")
                    
            # Cleanup
            if bot.driver:
                bot.driver.quit()
                
            self.logger.info(f"🎉 Follow cycle completed: {total_follows} total follows")
            
            # Send notification for significant activity
            if total_follows > 0:
                message = f"✅ Follow cycle completed: {total_follows} new follows from {len(instagram_config['target_accounts'])} accounts"
                self.send_discord_notification(message)
                
        except Exception as e:
            error_msg = f"❌ Follow cycle failed: {str(e)}"
            self.logger.error(error_msg)
            self.send_email_notification("Follow Cycle Error", error_msg, is_error=True)
            self.send_discord_notification(error_msg, is_error=True)
            
    def run_unfollow_cycle(self):
        """Run the unfollow cycle"""
        try:
            self.logger.info("🔄 Starting unfollow cycle")
            
            # Check configuration
            instagram_config = self.config.get('instagram', {})
            username = instagram_config.get('username', '')
            password = instagram_config.get('password', '')
            
            if not username or not password:
                self.logger.warning("⚠️ Instagram credentials not configured. Use web dashboard to set them.")
                return
            
            # Create bot instance
            bot = InstagramBotGUI(
                username,
                password,
                [],  # No target accounts needed for unfollow
                0
            )
            
            # Initialize driver
            if not bot.init_driver(show_browser=False):
                raise Exception("Failed to initialize Chrome driver")
                
            # Login
            if not bot.login():
                raise Exception("Failed to login to Instagram")
                
            self.logger.info("✅ Bot logged in for unfollow cycle")
            
            # Unfollow old users
            unfollowed_count = bot.unfollow_old_users(
                hours_threshold=instagram_config['unfollow_after_hours']
            )
            
            # Cleanup
            if bot.driver:
                bot.driver.quit()
                
            self.logger.info(f"🔄 Unfollow cycle completed: {unfollowed_count} users unfollowed")
            
            # Send notification if users were unfollowed
            if unfollowed_count > 0:
                message = f"🔄 Unfollow cycle completed: {unfollowed_count} users unfollowed (48+ hours old)"
                self.send_discord_notification(message)
                
        except Exception as e:
            error_msg = f"❌ Unfollow cycle failed: {str(e)}"
            self.logger.error(error_msg)
            self.send_email_notification("Unfollow Cycle Error", error_msg, is_error=True)
            self.send_discord_notification(error_msg, is_error=True)
            
    def setup_schedule(self):
        """Setup the automation schedule"""
        schedule_config = self.config['schedule']
        
        # Daily follow schedule
        schedule.every().day.at(schedule_config['follow_time']).do(self.run_follow_cycle)
        self.logger.info(f"📅 Follow cycle scheduled for {schedule_config['follow_time']} daily")
        
        # Daily unfollow schedule  
        schedule.every().day.at(schedule_config['unfollow_time']).do(self.run_unfollow_cycle)
        self.logger.info(f"📅 Unfollow cycle scheduled for {schedule_config['unfollow_time']} daily")
        
        # Daily report schedule
        schedule.every().day.at("20:00").do(self.send_daily_report)
        self.logger.info("📅 Daily report scheduled for 20:00")
        
        # Config reload schedule (every hour)
        schedule.every().hour.do(self.reload_config)
        
    def reload_config(self):
        """Reload configuration from file"""
        try:
            old_config = self.config.copy()
            self.config = self.load_config()
            
            # Check if schedule changed
            if old_config.get('schedule') != self.config.get('schedule'):
                schedule.clear()
                self.setup_schedule()
                self.logger.info("🔄 Schedule updated due to config change")
                
        except Exception as e:
            self.logger.error(f"❌ Error reloading config: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def run(self):
        """Main run loop"""
        try:
            self.logger.info("🚀 Starting Instagram Bot Server")
            
            # Send startup notification
            startup_msg = f"🚀 Instagram Bot Server started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_email_notification("Bot Started", startup_msg)
            self.send_discord_notification(startup_msg)
            
            # Setup schedule
            self.setup_schedule()
            
            # Main loop
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            self.logger.info("🛑 Bot server stopped")
            
        except Exception as e:
            error_msg = f"💥 Critical error in main loop: {str(e)}"
            self.logger.error(error_msg)
            self.send_email_notification("Critical Error", error_msg, is_error=True)
            self.send_discord_notification(error_msg, is_error=True)
            
        finally:
            # Send shutdown notification
            shutdown_msg = f"🛑 Instagram Bot Server stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_email_notification("Bot Stopped", shutdown_msg)
            self.send_discord_notification(shutdown_msg)

if __name__ == "__main__":
    bot = ServerInstagramBot()
    bot.run() 