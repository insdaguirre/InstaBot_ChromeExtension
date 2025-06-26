# Instagram Automation System

🤖 **Automated Instagram follower management for music niche accounts**

## 🚀 Current Working System

This is the **CLEAN, FUNCTIONAL VERSION** after extensive development and testing.

### ✅ What's Working (AWS Deployed)

**🎯 Core Files:**
- `complete_instagram_bot.py` - Main automation bot (proven working)
- `scheduler.py` - Automated scheduling service  
- `dashboard.py` - Web dashboard for monitoring
- `test_bot.py` - Quick functionality tests

**🛠️ Deployment:**
- `setup_new_instance.sh` - Complete AWS instance setup
- `DEPLOYMENT_ROADMAP.md` - Step-by-step deployment guide
- `deploy_complete_system.sh` - Automated deployment script
- `cleanup_aws.sh` - AWS cleanup utilities

**📊 Configuration:**
- `settings.json` - Instagram credentials
- `requirements.txt` - Python dependencies

## 🎯 Current Configuration

- **Target accounts:** `1001tracklists`, `housemusic.us`, `housemusicnerds`, `edm`
- **Daily follows:** 100 (25 per account)
- **Auto-unfollow:** 48 hours
- **Schedule:** Twice daily (10 AM & 6 PM UTC)
- **Platform:** AWS EC2 (needs t3.small+ for memory)

## 🌐 Live Dashboard

**URL:** `http://ec2-3-17-165-195.us-east-2.compute.amazonaws.com:5000`

## 📁 Archive Structure

All non-functional/experimental code moved to `archive/`:
- `archive/old_versions/` - Previous AWS attempts
- `archive/cloud_attempts/` - Oracle/GCP experiments  
- `archive/local_versions/` - Local development versions
- `archive/failed_experiments/` - Experimental scripts
- `archive/documentation/` - Outdated documentation

## 🚨 Known Issues

- **Memory limitation:** Current t2.micro (957MB RAM) insufficient for Instagram's memory requirements
- **Solution:** Deploy to t3.small (2GB RAM) for stable operation

## 🛠️ Quick Deploy

```bash
# 1. Ensure SSH key exists
ls instagram-automation-key-new.pem

# 2. Deploy to fresh AWS instance
./setup_new_instance.sh

# 3. Monitor via dashboard
open http://YOUR-INSTANCE:5000
```

## 📈 Status

✅ **Scheduler:** Running  
✅ **Dashboard:** Accessible  
✅ **Login/Navigation:** Working  
⚠️ **Follower collection:** Needs more RAM

---
*Last updated: June 26, 2025* 