# Instagram Automation Tool

A GUI-based tool for automating Instagram following/unfollowing with customizable delays and targets.

## Features

- User-friendly GUI interface
- Multiple target account support
- Customizable follow/unfollow delays
- Automatic unfollowing after specified delay
- Progress logging
- Settings persistence
- Rate limit avoidance

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository
3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python gui.py
```

2. Enter your Instagram credentials
3. Add target accounts (one per line)
4. Configure settings:
   - Number of users to follow per account
   - Follow delay range (in seconds)
   - Unfollow delay (in hours)
5. Click Start to begin automation

## Important Notes

- Use this tool responsibly and in accordance with Instagram's terms of service
- Recommended delays: 30-60 seconds between follows
- Keep daily follow counts reasonable to avoid restrictions
- The tool saves followed users and their timestamps for proper unfollow scheduling
- You can stop the automation at any time by clicking the Stop button

## Files

- `gui.py`: Main GUI application
- `instagram_bot.py`: Instagram automation logic
- `followed_users.json`: Tracks followed users (created automatically)
- `settings.json`: Saves your settings (created automatically)

## Requirements

- Python 3.8+
- Chrome browser
- Stable internet connection

## Disclaimer

This tool is for educational purposes only. Use at your own risk. The authors are not responsible for any account restrictions or bans that may result from using this tool. 