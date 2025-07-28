# 📸 Instagram Bot - Chrome Extension

![Instagram Bot Extension](render.png)

A Chrome extension for Instagram automation that works directly in your browser. Follow and unfollow users with precise control while using your real Instagram session.

---

## 🚀 Why Chrome Extension? (Design Choices)

- **Natural Integration:** Works with your existing Instagram session - no separate login needed
- **Real Browser Session:** Uses your actual Chrome browser, making actions appear completely natural
- **Manual Control:** You navigate to the pages you want to automate, giving you full control
- **No Detection:** Since it uses your real browser session and you manually navigate, it's virtually undetectable
- **Simple Setup:** Just install the extension and you're ready to go
- **Privacy First:** No data ever leaves your browser, everything runs locally

---

## 🛠️ How It Works

### Chrome Extension Workflow

1. **Install the Extension:** Load the extension into Chrome
2. **Navigate to Instagram:** Log into Instagram normally in your browser
3. **Go to Target Page:**
   - **For Following:** Navigate to any user's followers page
   - **For Unfollowing:** Navigate to your own following page
4. **Open Extension:** Click the extension icon in Chrome
5. **Set Count & Start:** Enter the number of users and click start
6. **Automated Actions:** The extension follows/unfollows the exact number you specified

---

## 🗂️ File & Component Overview

- `manifest.json` — Chrome extension configuration
- `popup.html` — Extension popup interface (vintage Windows style)
- `popup.js` — Popup logic and user interface handling
- `content.js` — Content script that runs on Instagram pages and performs automation

---

## 🔄 Information Flow

```mermaid
graph TD;
    User["User<br/>navigates to Instagram"] --> Page["Instagram<br/>Followers/Following Page"];
    User -->|"Click extension"| Popup["popup.html<br/>(Extension GUI)"];
    Popup -->|"Send message"| Content["content.js<br/>(Content Script)"];
    Content -->|"Find & click buttons"| Page;
    Content -->|"Update status"| Popup;
```

---

## 🧩 Component Relationships

```mermaid
graph LR;
    Popup["popup.html + popup.js"] --messages--> Content["content.js"];
    Content --runs on--> Instagram["Instagram Pages"];
    Manifest["manifest.json"] --configures--> Popup;
    Manifest --configures--> Content;
```

---

## 🖥️ How to Use

### Installation

1. **Download/Clone this repository**
2. **Open Chrome and go to:** `chrome://extensions/`
3. **Enable "Developer mode"** (toggle in top right)
4. **Click "Load unpacked"** and select this project folder
5. **The extension icon will appear** in your Chrome toolbar

### Usage

1. **Login to Instagram** in Chrome normally
2. **Navigate to the target page:**
   - **To Follow:** Go to any user's profile → Click "followers"
   - **To Unfollow:** Go to your own profile → Click "following"
3. **Click the extension icon** in Chrome toolbar
4. **The popup will detect the page type** and show appropriate options
5. **Enter the number** of users to follow/unfollow (1-50)
6. **Click START** and watch the automation work
7. **Monitor progress** in the status area

---

## ⚙️ Technical Details

### Follow Logic
- **Context Aware:** Automatically detects if you're on followers (follow) or following (unfollow) page
- **Exact Count:** Follows/unfollows exactly the number you specify
- **Smart Scrolling:** Automatically scrolls to find more users if needed
- **1-Second Delays:** Waits 1 second between each action
- **Username Extraction:** Logs usernames for each action taken

### Page Detection
- **Followers Page:** Shows "Follow Users" option
- **Following Page:** Shows "Unfollow Users" option  
- **Other Pages:** Shows navigation instructions

### Safety Features
- **Session Management:** Uses your real browser session (no separate login)
- **Manual Navigation:** You control which pages to automate
- **Rate Limiting:** Built-in delays to prevent Instagram rate limits
- **Status Updates:** Real-time feedback on progress
- **Error Handling:** Graceful handling of missing elements or Instagram changes

---

## 📦 Extension Structure

### Files
- `manifest.json` - Extension permissions and configuration
- `popup.html` - User interface with vintage Windows styling
- `popup.js` - Interface logic and Chrome extension messaging
- `content.js` - Instagram page automation logic

### Permissions
- `activeTab` - Access to current Instagram tab
- `storage` - Save extension settings (if needed)

---

## ⚠️ Important Notes

- **Manual Navigation Required:** You must manually navigate to the Instagram page you want to automate
- **Real Session:** Uses your actual Instagram login session
- **Rate Limits:** Instagram may still apply rate limits for excessive actions
- **Page Refresh:** If Instagram refreshes the page, just reopen the extension
- **Browser Required:** Must use Chrome browser with extension installed

---

## 🚨 Usage Instructions

### To Follow Users:
1. Go to any Instagram user's profile
2. Click "followers" to open the followers list
3. Click the extension icon
4. Enter number to follow and click "START FOLLOWING"

### To Unfollow Users:
1. Go to your own Instagram profile  
2. Click "following" to open your following list
3. Click the extension icon
4. Enter number to unfollow and click "START UNFOLLOWING"

---

## 🛡️ Safety & Detection

- **Undetectable:** Uses your real browser session and manual navigation
- **Natural Timing:** 1-second delays between actions mimic human behavior
- **No Automation Detection:** Since you manually navigate and use real session
- **Rate Limit Aware:** Stops if Instagram blocks actions
- **Manual Override:** You can stop automation at any time by closing the popup

---

## ⚠️ Disclaimer

This tool is for educational and personal use only. Use responsibly and in accordance with Instagram's terms of service. The extension works with your real Instagram account, so exercise caution with the number of actions performed. 