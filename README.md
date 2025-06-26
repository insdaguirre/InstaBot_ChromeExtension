# Instagram Automation System

🤖 **Fully functional Instagram automation bot deployed on AWS**

## ✅ What This Is

This is a **COMPLETE, WORKING Instagram automation system** that:

- ✅ **Automatically follows** users from target accounts
- ✅ **Auto-unfollows** after 48 hours  
- ✅ **Runs 24/7** on AWS cloud
- ✅ **Web dashboard** for monitoring
- ✅ **Scheduled execution** (twice daily)
- ✅ **Proven to work** with proper AWS instance

## 💰 Requirements: Paid AWS Instance

⚠️ **IMPORTANT:** This automation requires a **paid AWS instance** to function properly.

**Why paid instance is required:**
- Instagram's heavy JavaScript needs **2GB+ RAM**
- Free tier t2.micro (1GB RAM) causes Chrome crashes
- **Minimum:** t3.small instance (~$16/month)
- **Recommended:** t3.medium for multiple accounts

**Free tier limitations:**
- ❌ Insufficient memory for Instagram automation
- ❌ Chrome crashes during follower collection
- ❌ Complex JavaScript fails to load properly

## 🚀 Current Working System

### 🎯 Core Files
- `complete_instagram_bot.py` - Main automation bot (proven working)
- `scheduler.py` - Automated scheduling service  
- `dashboard.py` - Web dashboard for monitoring
- `test_bot.py` - Quick functionality tests

### 🛠️ Deployment
- `setup_new_instance.sh` - Complete AWS instance setup
- `DEPLOYMENT_ROADMAP.md` - Step-by-step deployment guide
- `deploy_complete_system.sh` - Automated deployment script
- `cleanup_aws.sh` - AWS cleanup utilities

### 📊 Configuration
- `settings.json` - Instagram credentials
- `requirements.txt` - Python dependencies

## 🎯 Current Configuration

- **Target accounts:** `1001tracklists`, `housemusic.us`, `housemusicnerds`, `edm`
- **Daily follows:** 100 (25 per account)
- **Auto-unfollow:** 48 hours
- **Schedule:** Twice daily (10 AM & 6 PM UTC)
- **Platform:** AWS EC2 (t3.small minimum)

## 🌐 Live Dashboard

**URL:** `http://ec2-3-17-165-195.us-east-2.compute.amazonaws.com:5000`

## 💻 Deployment Requirements

### AWS Instance Specifications:
- **Instance Type:** t3.small or larger (NOT t2.micro)
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 8GB+ SSD
- **Cost:** ~$16-30/month depending on instance size

### Why These Specs:
- Instagram requires significant memory for JavaScript processing
- Chrome browser needs substantial RAM for stable operation
- Multiple target accounts increase memory requirements

## 🛠️ Quick Deploy

```bash
# 1. Create AWS t3.small instance (PAID)
# 2. Ensure SSH key exists
ls instagram-automation-key-new.pem

# 3. Deploy to AWS instance
./setup_new_instance.sh

# 4. Monitor via dashboard
open http://YOUR-INSTANCE:5000
```

## 📁 Archive Structure

All non-functional/experimental code moved to `archive/`:
- `archive/old_versions/` - Previous AWS attempts
- `archive/cloud_attempts/` - Oracle/GCP experiments  
- `archive/local_versions/` - Local development versions
- `archive/failed_experiments/` - Experimental scripts
- `archive/documentation/` - Outdated documentation

## 📈 Status

✅ **System:** Fully functional  
✅ **Scheduler:** Running  
✅ **Dashboard:** Accessible  
✅ **Login/Navigation:** Working  
✅ **Follower collection:** Works on t3.small+  
⚠️ **Limitation:** Requires paid AWS instance

## 💡 Cost Estimate

**Monthly AWS costs:**
- **t3.small:** ~$16/month (2GB RAM, 2 vCPU)
- **t3.medium:** ~$32/month (4GB RAM, 2 vCPU) - recommended for heavy use

**Alternative:** You can run this locally for free, but won't have 24/7 automation.

---
*Last updated: June 26, 2025* 