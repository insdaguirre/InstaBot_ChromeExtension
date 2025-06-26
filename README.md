# Instagram Automation System

🤖 **Professional Instagram automation bot with AWS cloud deployment**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)](https://aws.amazon.com)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

## 🎯 Overview

A complete Instagram automation system designed for professional social media management. Built with security, scalability, and reliability in mind.

**🔥 Key Features:**
- ✅ **Automated Following/Unfollowing** with smart targeting
- ✅ **24/7 Cloud Operation** on AWS infrastructure  
- ✅ **Web Dashboard** for monitoring and analytics
- ✅ **Secure Configuration** with environment variables
- ✅ **Rate Limiting** to avoid Instagram restrictions
- ✅ **Comprehensive Logging** and error handling
- ✅ **Modular Architecture** for easy customization

## 🚀 Quick Start

### 1. Setup
```bash
# Clone the repository
git clone https://github.com/your-username/instagram-automation.git
cd instagram-automation

# Install dependencies
pip install -r requirements.txt

# Configure credentials securely
python setup.py
```

### 2. Local Testing
```bash
# Test the configuration
python test_bot.py

# Run single automation cycle
python complete_instagram_bot.py

# Start web dashboard
python dashboard.py
```

### 3. AWS Deployment
```bash
# Deploy to AWS (requires t3.small+ instance)
./setup_new_instance.sh

# Monitor via web interface
open http://your-instance:5000
```

## 🔧 Configuration

The system supports multiple secure configuration methods:

### Option 1: Interactive Setup (Recommended)
```bash
python setup.py
# Follow the interactive prompts
```

### Option 2: Environment Variables
```bash
cp .env.template .env
# Edit .env with your credentials
export INSTAGRAM_USERNAME="your_username"
export INSTAGRAM_PASSWORD="your_password"
```

### Option 3: Configuration File
```bash
cp config.template.json config.json
# Edit config.json with your settings
```

## 🏗️ Architecture

### Core Components
- **`complete_instagram_bot.py`** - Main automation engine
- **`scheduler.py`** - Automated scheduling service  
- **`dashboard.py`** - Web monitoring interface
- **`config.py`** - Secure configuration management

### AWS Deployment
- **`setup_new_instance.sh`** - Complete AWS instance setup
- **`DEPLOYMENT_ROADMAP.md`** - Step-by-step deployment guide
- **Instance Requirements:** t3.small minimum (2GB RAM)

### Security Features
- 🔐 No hardcoded credentials
- 🔒 Environment variable support
- 🚫 Sensitive files excluded from git
- ✅ Secure configuration templates

## 📊 Automation Features

### Smart Targeting
- **Multiple target accounts** for diverse audience
- **Configurable follow limits** per account
- **Intelligent user selection** from followers
- **Duplicate prevention** and tracking

### Timing & Safety
- **Random delays** between actions (20-40 seconds)
- **Daily follow limits** to avoid restrictions
- **Auto-unfollow** after configurable delay (default: 48 hours)
- **Scheduled execution** (2x daily by default)

### Monitoring
- **Real-time web dashboard** with statistics
- **Comprehensive logging** of all actions
- **Error tracking** and recovery
- **Performance analytics**

## 💻 Technical Requirements

### Local Development
- Python 3.8+
- Chrome browser
- ChromeDriver (auto-installed)
- 4GB+ RAM recommended

### AWS Production
- **Instance Type:** t3.small minimum (t3.medium recommended)
- **RAM:** 2GB minimum (4GB for heavy usage)
- **Storage:** 8GB+ SSD
- **Monthly Cost:** ~$16-32 depending on instance size

## 🛡️ Security & Best Practices

### Configuration Security
- ✅ All credentials stored in environment variables or secure config files
- ✅ Sensitive files excluded from version control
- ✅ Template-based setup for easy deployment
- ✅ No hardcoded passwords or API keys

### Instagram Compliance
- ⏱️ **Rate limiting** to respect Instagram's terms
- 🎯 **Realistic delays** between actions
- 📊 **Conservative daily limits** (100 follows/day default)
- 🔄 **Proper unfollow scheduling** to maintain ratios

## 📈 Performance

### Optimized Operation
- **Memory efficient** Chrome configuration
- **Headless operation** for server deployment
- **Error recovery** and automatic retries
- **Resource monitoring** and cleanup

### Scalability
- **Multiple target accounts** support
- **Configurable automation limits**
- **Cloud-ready architecture**
- **Easy horizontal scaling**

## 🗂️ Project Structure

```
├── complete_instagram_bot.py    # Main automation engine
├── scheduler.py                 # Scheduling service
├── dashboard.py                 # Web monitoring interface
├── config.py                    # Secure configuration management
├── setup.py                     # Interactive setup wizard
├── test_bot.py                  # Testing utilities
├── setup_new_instance.sh        # AWS deployment script
├── DEPLOYMENT_ROADMAP.md        # Deployment documentation
├── config.template.json         # Configuration template
├── .env.template               # Environment variables template
├── requirements.txt            # Python dependencies
└── archive/                    # Previous versions and experiments
```

## 🚀 Deployment Options

### 1. AWS EC2 (Recommended)
- **Pros:** 24/7 operation, scalable, professional
- **Cons:** Monthly cost (~$16-32)
- **Best for:** Production use, multiple accounts

### 2. Local Machine
- **Pros:** Free, full control, easy development
- **Cons:** Not 24/7, requires manual management
- **Best for:** Testing, personal use

### 3. Other Cloud Providers
- **VPS providers:** DigitalOcean, Linode, Vultr
- **Cloud platforms:** Google Cloud, Azure
- **Requirements:** 2GB+ RAM, Ubuntu 22.04+

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_ROADMAP.md)** - Complete AWS setup
- **[Configuration Reference](config.template.json)** - All available options
- **[Archive](archive/)** - Previous versions and development history

## ⚠️ Disclaimer

This tool is for educational and professional social media management purposes. Users are responsible for complying with Instagram's Terms of Service and applicable laws. The authors are not responsible for any account restrictions or violations that may result from misuse.

## 🤝 Contributing

Contributions welcome! Please read the contribution guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for professional social media automation** 