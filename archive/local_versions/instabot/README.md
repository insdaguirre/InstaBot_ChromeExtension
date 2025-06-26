# Instagram Automation Tool

A Python-based Instagram automation tool with a GUI interface for managing follow/unfollow operations.

## Features

- Follow users from target accounts
- Unfollow users using CSV import
- Customizable delay between actions
- Action logging and history
- User-friendly GUI interface
- CSV export of followed users

## Requirements

- Python 3.x
- Google Chrome browser
- macOS (tested on darwin 24.5.0)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd instagram-automation
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip3 install PyQt5 selenium webdriver-manager requests
```

## Usage

1. Run the GUI:
```bash
python3 gui.py
```

2. Enter your Instagram credentials
3. Add target accounts for following or import CSV for unfollowing
4. Configure delay settings
5. Start the automation process

## Safety Features

- Customizable delays between actions
- Built-in rate limiting
- Action logging for tracking
- Error handling and retry mechanisms

## Note

This tool is for educational purposes only. Please use responsibly and in accordance with Instagram's terms of service. 