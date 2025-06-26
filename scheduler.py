#!/usr/bin/env python3
"""
Instagram Automation Scheduler - Runs bot daily
"""
import schedule
import time
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Setup logging for scheduler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SCHEDULER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_bot():
    """Run the Instagram bot"""
    try:
        logger.info("🕐 Starting scheduled Instagram automation...")
        
        # Run the bot
        result = subprocess.run([
            sys.executable, 'complete_instagram_bot.py'
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            logger.info("✅ Bot completed successfully")
            logger.info(f"Output: {result.stdout}")
        else:
            logger.error("❌ Bot failed")
            logger.error(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("⏰ Bot timed out after 1 hour")
    except Exception as e:
        logger.error(f"❌ Error running bot: {str(e)}")

def main():
    """Main scheduler function"""
    logger.info("🚀 Instagram Automation Scheduler started")
    
    # Schedule the bot to run daily at 10 AM
    schedule.every().day.at("10:00").do(run_bot)
    
    # Also schedule for 6 PM for more activity
    schedule.every().day.at("18:00").do(run_bot)
    
    logger.info("📅 Scheduled bot to run daily at 10:00 AM and 6:00 PM")
    
    # Keep the scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    main() 