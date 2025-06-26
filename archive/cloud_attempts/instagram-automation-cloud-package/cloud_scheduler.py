#!/usr/bin/env python3
"""
Cloud Instagram Automation Scheduler - Optimized for Oracle Cloud Free Tier
24/7 automation with minimal resource usage and robust error handling
"""
import os
import sys
import time
import json
import logging
import schedule
import signal
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from cloud_instagram_bot import CloudInstagramBot, CloudLogger

class CloudInstagramScheduler:
    def __init__(self, config_file='cloud_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.running = False
        self.setup_logging()
        self.setup_signal_handlers()
        
        # Cloud-specific optimizations
        self.max_memory_mb = 800  # Leave 200MB for system
        self.daily_follows_count = 0
        self.last_follow_date = None
        self.target_account_index = 0
        
    def setup_logging(self):
        """Setup cloud-optimized logging"""
        log_dir = Path('instagram_data/logs')
        log_dir.mkdir(exist_ok=True, parents=True)
        
        # Configure logging for cloud with log rotation
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    log_dir / 'cloud_scheduler.log',
                    maxBytes=5*1024*1024,  # 5MB max
                    backupCount=3
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def load_config(self):
        """Load cloud configuration with Oracle Cloud optimizations"""
        default_config = {
            "instagram_username": "",
            "instagram_password": "",
            "target_accounts": [
                "example_account1",
                "example_account2", 
                "example_account3",
                "example_account4"
            ],
            "daily_follow_limit": 100,
            "followers_per_account": 25,  # 4 accounts × 25 = 100 total
            "accounts_per_batch": 4,
            "unfollow_delay_hours": 48,
            "follow_schedule": "10:00",
            "unfollow_schedule": "22:00",
            "min_delay_between_follows": 15,  # Faster for cloud
            "max_delay_between_follows": 45,
            "enabled": True,
            "cloud_mode": True,
            "headless": True,
            "max_retries": 3
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                
        # Save updated config
        self.save_config(default_config)
        return default_config
        
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def check_system_resources(self):
        """Check if system has enough resources for automation"""
        try:
            # Check memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                
            for line in meminfo.split('\n'):
                if 'MemAvailable:' in line:
                    available_mb = int(line.split()[1]) // 1024
                    if available_mb < 300:  # Need at least 300MB available
                        self.logger.warning(f"Low memory: {available_mb}MB available")
                        return False
                    break
                    
            return True
        except:
            return True  # Assume OK if can't check
            
    def get_next_target_accounts(self):
        """Get the next batch of target accounts for following"""
        target_accounts = self.config['target_accounts']
        accounts_per_batch = self.config['accounts_per_batch']
        
        if len(target_accounts) < accounts_per_batch:
            self.logger.warning(f"Not enough target accounts. Need at least {accounts_per_batch}")
            return target_accounts
            
        # For 100 follows/day, use all accounts to spread the load
        return target_accounts
        
    def daily_follow_job(self):
        """Execute daily follow job with cloud optimizations"""
        if not self.config['enabled']:
            self.logger.info("Scheduler disabled, skipping follow job")
            return
            
        if not self.check_system_resources():
            self.logger.warning("Insufficient system resources, skipping follow job")
            return
            
        today = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if self.last_follow_date != today:
            self.daily_follows_count = 0
            self.last_follow_date = today
            
        # Check daily limit
        if self.daily_follows_count >= self.config['daily_follow_limit']:
            self.logger.info(f"Daily follow limit of {self.config['daily_follow_limit']} reached")
            return
            
        self.logger.info("🚀 Starting cloud follow job...")
        
        retries = 0
        max_retries = self.config.get('max_retries', 3)
        
        while retries < max_retries:
            try:
                # Get target accounts
                target_accounts = self.get_next_target_accounts()
                followers_per_account = self.config['followers_per_account']
                
                self.logger.info(f"📋 Following {followers_per_account} users from each: {target_accounts}")
                
                # Create cloud bot instance
                bot = CloudInstagramBot(
                    username=self.config['instagram_username'],
                    password=self.config['instagram_password'],
                    target_accounts=target_accounts,
                    users_per_account=followers_per_account
                )
                
                # Execute following
                cloud_logger = CloudLogger(self.logger)
                successfully_followed = bot.run_follow_job(cloud_logger)
                
                # Update daily counter
                self.daily_follows_count += len(successfully_followed)
                
                self.logger.info(f"✅ Follow job completed: {len(successfully_followed)} new follows")
                self.logger.info(f"📊 Daily progress: {self.daily_follows_count}/{self.config['daily_follow_limit']}")
                
                # Export results
                if successfully_followed:
                    bot.export_followed_users(successfully_followed, cloud_logger)
                
                # Save status
                self.save_status({
                    'last_follow_job': datetime.now().isoformat(),
                    'daily_follows_count': self.daily_follows_count,
                    'last_follow_date': today.isoformat(),
                    'successfully_followed': len(successfully_followed),
                    'target_accounts': target_accounts
                })
                
                # Success, break retry loop
                break
                
            except Exception as e:
                retries += 1
                self.logger.error(f"❌ Follow job error (attempt {retries}/{max_retries}): {e}")
                
                if retries < max_retries:
                    wait_time = 60 * retries  # Exponential backoff
                    self.logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error("❌ Follow job failed after all retries")
                    
    def daily_unfollow_job(self):
        """Execute daily unfollow job with cloud optimizations"""
        if not self.config['enabled']:
            self.logger.info("Scheduler disabled, skipping unfollow job")
            return
            
        if not self.check_system_resources():
            self.logger.warning("Insufficient system resources, skipping unfollow job")
            return
            
        self.logger.info("🔄 Starting cloud unfollow job...")
        
        try:
            # Load followed users data
            followed_users_file = Path('followed_users.json')
            if not followed_users_file.exists():
                self.logger.info("No followed users file found")
                return
                
            with open(followed_users_file, 'r') as f:
                followed_users = json.load(f)
                
            # Find users to unfollow (>48 hours old)
            cutoff_time = datetime.now() - timedelta(hours=self.config['unfollow_delay_hours'])
            users_to_unfollow = []
            
            for user in followed_users:
                if isinstance(user, dict) and 'followed_at' in user and not user.get('unfollowed', False):
                    try:
                        followed_at = datetime.fromisoformat(user['followed_at'])
                        if followed_at <= cutoff_time:
                            users_to_unfollow.append(user['username'])
                    except:
                        continue
                        
            if not users_to_unfollow:
                self.logger.info("No users ready for unfollowing")
                return
                
            # Limit unfollows to avoid rate limiting
            max_unfollows = min(len(users_to_unfollow), 100)
            users_to_unfollow = users_to_unfollow[:max_unfollows]
            
            self.logger.info(f"📋 Unfollowing {len(users_to_unfollow)} users")
            
            # Create cloud bot instance
            bot = CloudInstagramBot(
                username=self.config['instagram_username'],
                password=self.config['instagram_password'],
                target_accounts=[],  # Not used for unfollowing
                users_per_account=0
            )
            
            # Execute unfollowing
            cloud_logger = CloudLogger(self.logger)
            successfully_unfollowed = bot.run_unfollow_job(users_to_unfollow, cloud_logger)
            
            # Update followed users data
            for user in followed_users:
                if isinstance(user, dict) and user.get('username') in successfully_unfollowed:
                    user['unfollowed'] = True
                    user['unfollowed_at'] = datetime.now().isoformat()
                    
            # Save updated data
            with open(followed_users_file, 'w') as f:
                json.dump(followed_users, f, indent=2)
                
            self.logger.info(f"✅ Unfollow job completed: {len(successfully_unfollowed)} accounts")
            
            # Save status
            self.save_status({
                'last_unfollow_job': datetime.now().isoformat(),
                'successfully_unfollowed': len(successfully_unfollowed)
            })
            
        except Exception as e:
            self.logger.error(f"❌ Error in unfollow job: {e}")
            
    def save_status(self, status_update):
        """Save current status to file"""
        status_file = Path('instagram_data/cloud_status.json')
        status_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Load existing status
        current_status = {}
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    current_status = json.load(f)
            except:
                pass
                
        # Update status
        current_status.update(status_update)
        current_status['last_update'] = datetime.now().isoformat()
        current_status['pid'] = os.getpid()
        
        # Save status
        try:
            with open(status_file, 'w') as f:
                json.dump(current_status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving status: {e}")
            
    def setup_schedules(self):
        """Setup scheduled jobs optimized for cloud"""
        follow_time = self.config['follow_schedule']
        unfollow_time = self.config['unfollow_schedule']
        
        # Schedule daily jobs
        schedule.every().day.at(follow_time).do(self.daily_follow_job)
        schedule.every().day.at(unfollow_time).do(self.daily_unfollow_job)
        
        # Add health check every hour
        schedule.every().hour.do(self.health_check)
        
        self.logger.info(f"📅 Scheduled follows at {follow_time}")
        self.logger.info(f"📅 Scheduled unfollows at {unfollow_time}")
        self.logger.info(f"🏥 Health checks every hour")
        
    def health_check(self):
        """Perform system health check"""
        try:
            # Update status with health info
            self.save_status({
                'health_check': datetime.now().isoformat(),
                'memory_available': self.get_available_memory(),
                'disk_usage': self.get_disk_usage()
            })
            
            self.logger.info("🏥 Health check completed")
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            
    def get_available_memory(self):
        """Get available memory in MB"""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemAvailable:' in line:
                        return int(line.split()[1]) // 1024
        except:
            return 0
            
    def get_disk_usage(self):
        """Get disk usage percentage"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return round((used / total) * 100, 1)
        except:
            return 0
        
    def run_scheduler(self):
        """Main scheduler loop optimized for cloud"""
        self.logger.info("🤖 Cloud Instagram Scheduler starting...")
        self.logger.info(f"📊 Daily limit: {self.config['daily_follow_limit']} follows")
        self.logger.info(f"⏰ Follow time: {self.config['follow_schedule']}")
        self.logger.info(f"⏰ Unfollow time: {self.config['unfollow_schedule']}")
        self.logger.info(f"🌐 Cloud mode: {self.config.get('cloud_mode', True)}")
        
        self.setup_schedules()
        self.running = True
        
        # Save initial status
        self.save_status({
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'config': self.config,
            'cloud_optimized': True
        })
        
        # Main loop with cloud optimizations
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds (more frequent for cloud)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
        self.logger.info("🛑 Cloud Instagram Scheduler stopped")
        
        # Save final status
        self.save_status({
            'status': 'stopped',
            'stopped_at': datetime.now().isoformat()
        })

def main():
    """Main entry point for cloud scheduler"""
    # Set cloud environment variables
    os.environ['HEADLESS'] = 'true'
    os.environ['DISPLAY'] = ':99'
    
    scheduler = CloudInstagramScheduler()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'status':
            status_file = Path('instagram_data/cloud_status.json')
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    print(json.dumps(status, indent=2))
            else:
                print("No status file found")
            return
        elif sys.argv[1] == 'test':
            # Test mode - run a quick follow job
            print("🧪 Running test follow job...")
            scheduler.daily_follow_job()
            return
    
    # Run the cloud scheduler
    scheduler.run_scheduler()

if __name__ == "__main__":
    main() 