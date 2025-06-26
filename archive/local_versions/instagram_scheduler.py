#!/usr/bin/env python3
"""
Instagram Automation Scheduler - 24/7 Daemon Service
Automatically follows 100 people per day and unfollows after 48 hours
"""
import os
import sys
import time
import json
import random
import logging
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from instagram_bot import InstagramBot
import signal

class InstagramScheduler:
    def __init__(self, config_file='scheduler_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.running = False
        self.current_follow_session = None
        self.setup_logging()
        self.setup_signal_handlers()
        
        # State tracking
        self.daily_follows_count = 0
        self.last_follow_date = None
        self.target_account_index = 0
        
    def setup_logging(self):
        """Setup logging for the scheduler"""
        log_dir = Path('instagram_data/logs')
        log_dir.mkdir(exist_ok=True, parents=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'scheduler.log'),
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
        """Load scheduler configuration"""
        default_config = {
            "instagram_username": "",
            "instagram_password": "",
            "target_accounts": [
                "account1",
                "account2", 
                "account3",
                "account4"
            ],
            "daily_follow_limit": 100,
            "followers_per_account": 50,
            "accounts_per_batch": 2,
            "unfollow_delay_hours": 48,
            "follow_schedule": "10:00",  # Daily follow time
            "unfollow_schedule": "22:00",  # Daily unfollow time
            "min_delay_between_follows": 30,  # seconds
            "max_delay_between_follows": 120,  # seconds
            "enabled": True
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
            
    def get_next_target_accounts(self):
        """Get the next 2 target accounts for following"""
        target_accounts = self.config['target_accounts']
        accounts_per_batch = self.config['accounts_per_batch']
        
        if len(target_accounts) < accounts_per_batch:
            self.logger.warning(f"Not enough target accounts configured. Need at least {accounts_per_batch}")
            return target_accounts
            
        # Cycle through accounts
        selected_accounts = []
        for i in range(accounts_per_batch):
            account_index = (self.target_account_index + i) % len(target_accounts)
            selected_accounts.append(target_accounts[account_index])
            
        # Update index for next batch
        self.target_account_index = (self.target_account_index + accounts_per_batch) % len(target_accounts)
        
        return selected_accounts
        
    def daily_follow_job(self):
        """Execute daily follow job"""
        if not self.config['enabled']:
            self.logger.info("Scheduler is disabled, skipping follow job")
            return
            
        today = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if self.last_follow_date != today:
            self.daily_follows_count = 0
            self.last_follow_date = today
            
        # Check if we've already hit the daily limit
        if self.daily_follows_count >= self.config['daily_follow_limit']:
            self.logger.info(f"Daily follow limit of {self.config['daily_follow_limit']} already reached")
            return
            
        self.logger.info("🚀 Starting daily follow job...")
        
        try:
            # Get target accounts for this batch
            target_accounts = self.get_next_target_accounts()
            followers_per_account = self.config['followers_per_account']
            
            self.logger.info(f"📋 Following {followers_per_account} users from each: {target_accounts}")
            
            # Create bot instance
            bot = InstagramBot(
                username=self.config['instagram_username'],
                password=self.config['instagram_password'],
                target_accounts=target_accounts,
                users_per_account=followers_per_account
            )
            
            # Execute following with logging
            class SchedulerLogger:
                def __init__(self, logger):
                    self.logger = logger
                def emit(self, message):
                    self.logger.info(message)
                    
            logger_signal = SchedulerLogger(self.logger)
            
            successfully_followed = bot.run(logger_signal)
            
            # Update daily counter
            self.daily_follows_count += len(successfully_followed)
            
            self.logger.info(f"✅ Follow job completed: {len(successfully_followed)} new follows")
            self.logger.info(f"📊 Daily progress: {self.daily_follows_count}/{self.config['daily_follow_limit']}")
            
            # Save status
            self.save_status({
                'last_follow_job': datetime.now().isoformat(),
                'daily_follows_count': self.daily_follows_count,
                'last_follow_date': today.isoformat(),
                'target_account_index': self.target_account_index,
                'last_followed_accounts': target_accounts,
                'successfully_followed': len(successfully_followed)
            })
            
        except Exception as e:
            self.logger.error(f"❌ Error in follow job: {e}")
            
    def daily_unfollow_job(self):
        """Execute daily unfollow job (unfollow users after 48 hours)"""
        if not self.config['enabled']:
            self.logger.info("Scheduler is disabled, skipping unfollow job")
            return
            
        self.logger.info("🔄 Starting daily unfollow job...")
        
        try:
            # Load followed users data
            followed_users_file = Path('followed_users.json')
            if not followed_users_file.exists():
                self.logger.info("No followed users file found, nothing to unfollow")
                return
                
            with open(followed_users_file, 'r') as f:
                followed_users = json.load(f)
                
            # Find users to unfollow (followed more than 48 hours ago)
            cutoff_time = datetime.now() - timedelta(hours=self.config['unfollow_delay_hours'])
            users_to_unfollow = []
            
            for user in followed_users:
                if isinstance(user, dict) and 'followed_at' in user and not user.get('unfollowed', False):
                    followed_at = datetime.fromisoformat(user['followed_at'])
                    if followed_at <= cutoff_time:
                        users_to_unfollow.append(user['username'])
                        
            if not users_to_unfollow:
                self.logger.info("No users ready for unfollowing")
                return
                
            self.logger.info(f"📋 Unfollowing {len(users_to_unfollow)} users (followed >48h ago)")
            
            # Create bot instance for unfollowing
            bot = InstagramBot(
                username=self.config['instagram_username'],
                password=self.config['instagram_password'],
                target_accounts=users_to_unfollow,
                users_per_account=0
            )
            
            # Execute unfollowing
            class SchedulerLogger:
                def __init__(self, logger):
                    self.logger = logger
                def emit(self, message):
                    self.logger.info(message)
                    
            logger_signal = SchedulerLogger(self.logger)
            
            successfully_unfollowed = bot.run_unfollow(logger_signal)
            
            # Mark users as unfollowed
            for user in followed_users:
                if isinstance(user, dict) and user.get('username') in successfully_unfollowed:
                    user['unfollowed'] = True
                    user['unfollowed_at'] = datetime.now().isoformat()
                    
            # Save updated followed users
            with open(followed_users_file, 'w') as f:
                json.dump(followed_users, f, indent=2)
                
            self.logger.info(f"✅ Unfollow job completed: {len(successfully_unfollowed)} users unfollowed")
            
            # Save status
            self.save_status({
                'last_unfollow_job': datetime.now().isoformat(),
                'successfully_unfollowed': len(successfully_unfollowed)
            })
            
        except Exception as e:
            self.logger.error(f"❌ Error in unfollow job: {e}")
            
    def save_status(self, status_update):
        """Save current status to file"""
        status_file = Path('instagram_data/scheduler_status.json')
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
        
        # Save status
        try:
            with open(status_file, 'w') as f:
                json.dump(current_status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving status: {e}")
            
    def setup_schedules(self):
        """Setup scheduled jobs"""
        follow_time = self.config['follow_schedule']
        unfollow_time = self.config['unfollow_schedule']
        
        # Schedule daily jobs
        schedule.every().day.at(follow_time).do(self.daily_follow_job)
        schedule.every().day.at(unfollow_time).do(self.daily_unfollow_job)
        
        self.logger.info(f"📅 Scheduled daily follows at {follow_time}")
        self.logger.info(f"📅 Scheduled daily unfollows at {unfollow_time}")
        
    def run_scheduler(self):
        """Main scheduler loop"""
        self.logger.info("🤖 Instagram Scheduler starting...")
        self.logger.info(f"📊 Daily limit: {self.config['daily_follow_limit']} follows")
        self.logger.info(f"⏰ Follow time: {self.config['follow_schedule']}")
        self.logger.info(f"⏰ Unfollow time: {self.config['unfollow_schedule']}")
        
        self.setup_schedules()
        self.running = True
        
        # Save initial status
        self.save_status({
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'config': self.config
        })
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
        self.logger.info("🛑 Instagram Scheduler stopped")
        
        # Save final status
        self.save_status({
            'status': 'stopped',
            'stopped_at': datetime.now().isoformat()
        })

def main():
    """Main entry point"""
    scheduler = InstagramScheduler()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'setup':
            print("🔧 Setting up scheduler configuration...")
            # Interactive setup would go here
            return
        elif sys.argv[1] == 'status':
            # Show current status
            status_file = Path('instagram_data/scheduler_status.json')
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    print(json.dumps(status, indent=2))
            else:
                print("No status file found")
            return
    
    # Run the scheduler
    scheduler.run_scheduler()

if __name__ == "__main__":
    main() 