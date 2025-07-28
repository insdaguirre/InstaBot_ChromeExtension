# 📸 Instagram Bot - Chrome Extension

A Chrome extension for Instagram automation that works directly in your browser. Follow and unfollow users with precise control while using your real Instagram session.

## 🎨 Interface Preview

The extension features a **vintage Windows-style popup interface** with:
- **Blue title bar** with "Instagram Bot" branding
- **Vintage gray background** with thick borders
- **Monospace font** for that retro computer feel
- **Real-time status updates** with timestamps
- **Smart page detection** showing current Instagram page type
- **Followed list counter** showing stored usernames count
- **Clear list button** for managing followed users

### Extension Icon
- **Instagram-themed icon** with gradient background (pink to purple)
- **Camera symbol** with "A" for automation
- **Multiple sizes:** 16px, 32px, 48px, 128px for different contexts
- **Appears in Chrome toolbar** when installed

### Popup Interface Sections:
- **Page Detection:** Shows "Followers of @username" or "Following of @username"
- **Follow Users:** Input field for number (1-50) + "START FOLLOWING" button
- **Unfollow Users:** Input field for number (1-50) + "START UNFOLLOWING" button  
- **Followed List:** Shows count of stored usernames + "CLEAR LIST" button
- **Status Log:** Real-time updates with timestamps and progress indicators

### Interface Screenshots:

#### ✅ **Follow Configuration**
![Follow Configuration](./follow-config.png)
*Chrome extension popup showing the follow interface with page detection and follow controls*

#### ✅ **Unfollow Configuration**  
![Unfollow Configuration](./unfollow-config.png)
*Chrome extension popup showing the unfollow interface with page detection and unfollow controls*

### Interface States:

*Note: See the screenshots above for actual interface appearance. The ASCII art below shows the basic layout structure.*

#### ✅ **Ready State (Followers Page)**
```
┌─────────────────────────┐
│ Instagram Bot           │
├─────────────────────────┤
│ ✅ Ready to follow users│
│                         │
│ CURRENT PAGE            │
│ Followers of @username  │
│                         │
│ FOLLOW USERS            │
│ Number to follow: [10]  │
│ [START FOLLOWING]       │
│                         │
│ FOLLOWED LIST           │
│ Followed: 15 users      │
│ [CLEAR LIST]            │
│                         │
│ STATUS                  │
│ Ready to follow users   │
└─────────────────────────┘
```

#### ✅ **Ready State (Following Page)**
```
┌─────────────────────────┐
│ Instagram Bot           │
├─────────────────────────┤
│ ✅ Ready to unfollow    │
│                         │
│ CURRENT PAGE            │
│ Following of @username  │
│                         │
│ UNFOLLOW USERS          │
│ Number to unfollow: [10]│
│ [START UNFOLLOWING]     │
│                         │
│ FOLLOWED LIST           │
│ Followed: 15 users      │
│ [CLEAR LIST]            │
│                         │
│ STATUS                  │
│ Ready to unfollow users │
└─────────────────────────┘
```

#### ⚠️ **Working State (During Automation)**
```
┌─────────────────────────┐
│ Instagram Bot           │
├─────────────────────────┤
│ ⏳ Following @user123   │
│                         │
│ CURRENT PAGE            │
│ Followers of @username  │
│                         │
│ FOLLOW USERS            │
│ Number to follow: [10]  │
│ [START FOLLOWING]       │
│                         │
│ FOLLOWED LIST           │
│ Followed: 18 users      │
│ [CLEAR LIST]            │
│                         │
│ STATUS                  │
│ [6:15:30 PM] ✅ Followed│
│ @user123 (3/10)        │
│ ⏳ Waiting 1.8s...      │
└─────────────────────────┘
```

---

## 🚀 Why Chrome Extension? (Design Choices)

- **Natural Integration:** Works with your existing Instagram session - no separate login needed
- **Real Browser Session:** Uses your actual Chrome browser, making actions appear completely natural
- **Manual Control:** You navigate to the pages you want to automate, giving you full control
- **No Detection:** Since it uses your real browser session and you manually navigate, it's virtually undetectable
- **Simple Setup:** Just install the extension and you're ready to go
- **Privacy First:** No data ever leaves your browser, everything runs locally
- **Username Storage:** Remembers who you followed for targeted unfollowing

---

## 🛠️ How It Works

### Chrome Extension Workflow

1. **Install the Extension:** Load the extension into Chrome
2. **Navigate to Instagram:** Log into Instagram normally in your browser
3. **Go to Target Page:**
   - **For Following:** Navigate to any user's followers page (`instagram.com/USERNAME/followers/`)
   - **For Unfollowing:** Navigate to your own following page (`instagram.com/YOUR_USERNAME/following/`)
4. **Open Extension:** Click the extension icon in Chrome
5. **Set Count & Start:** Enter the number of users and click start
6. **Automated Actions:** The extension follows/unfollows the exact number you specified
7. **Username Storage:** Followed usernames are stored for targeted unfollowing

### Enhanced Page Detection System

The extension uses a **multi-layered detection approach** to reliably identify Instagram pages:

#### **1. URL-Based Detection (Primary)**
- **Followers:** Checks for `/followers/` in URL pattern
- **Following:** Checks for `/following/` in URL pattern
- **Username Extraction:** Extracts account name from URL
- **Works for Any Account:** `instagram.com/ANY_USERNAME/followers/` pattern

#### **2. Modal Dialog Detection (Fallback)**
- **Modal Content:** Checks Instagram's modal dialog for "followers" or "following" text
- **Dynamic Content:** Handles Instagram's dynamic modal loading
- **Text Analysis:** Searches modal text content for page type indicators

#### **3. Button Detection (Fallback)**
- **Follow Buttons:** Searches for buttons with "Follow" text (not "Following")
- **Following Buttons:** Searches for buttons with "Following" text
- **Multiple Methods:** Direct text matching + nested div structure scanning
- **Comprehensive Logging:** Shows exactly what buttons are found

#### **4. Page Title Detection (Final Fallback)**
- **Title Analysis:** Checks document.title for "followers" or "following"
- **Case Insensitive:** Handles any capitalization
- **Last Resort:** Used when other methods fail

#### **5. Ultimate Fallback**
- **All Buttons Scan:** Checks every button on page for "Follow" text
- **Detailed Logging:** Shows button text for debugging
- **Robust Detection:** Ensures detection even with Instagram changes

### Advanced Button Detection

The extension uses **intelligent button detection** that adapts to Instagram's changing HTML:

#### **Text-Based Detection**
```javascript
// Looks for exact "Follow" text (not "Following")
buttonText === 'follow'
```

#### **Nested Structure Detection**
```javascript
// Searches div elements within buttons
div.textContent.toLowerCase().trim() === 'follow'
```

#### **Multiple Fallback Methods**
- **Method 1:** Direct button text matching
- **Method 2:** Div structure scanning
- **Method 3:** All buttons on page scan
- **Method 4:** Comprehensive logging for debugging

### Username Storage & Targeted Unfollowing

#### **Follow Process:**
1. **Extract Username:** Gets username from button or page elements
2. **Store in Memory:** Adds to `followedUsernames` array
3. **Save to Storage:** Persists to Chrome's local storage
4. **Update UI:** Shows count in "FOLLOWED LIST" section

#### **Unfollow Process:**
1. **Load Stored List:** Retrieves usernames from storage
2. **Targeted Unfollowing:** Only unfollows users from stored list
3. **Remove from List:** Deletes username after successful unfollow
4. **Update Count:** Shows updated count in UI

---

## 🗂️ File & Component Overview

- `manifest.json` — Chrome extension configuration with icon references and storage permissions
- `popup.html` — Extension popup interface (vintage Windows style)
- `popup.js` — Popup logic, UI handling, and Chrome storage management
- `content.js` — Content script with enhanced page detection and button finding
- `icon16.png`, `icon32.png`, `icon48.png`, `icon128.png` — Extension icons

---

## 🔄 Information Flow

```mermaid
graph TD;
    User["User<br/>navigates to Instagram"] --> Page["Instagram<br/>Followers/Following Page"];
    User -->|"Click extension"| Popup["popup.html<br/>(Extension GUI)"];
    Popup -->|"Send message"| Content["content.js<br/>(Content Script)"];
    Content -->|"Multi-layer Detection"| Page;
    Content -->|"Find & click buttons"| Page;
    Content -->|"Store usernames"| Storage["Chrome Storage"];
    Content -->|"Update status"| Popup;
    Storage -->|"Load usernames"| Content;
```

---

## 🧩 Component Relationships

```mermaid
graph LR;
    Popup["popup.html + popup.js"] --messages--> Content["content.js"];
    Content --runs on--> Instagram["Instagram Pages"];
    Content --stores--> Storage["Chrome Storage"];
    Storage --loads--> Content;
    Manifest["manifest.json"] --configures--> Popup;
    Manifest --configures--> Content;
    Icons["icon*.png"] --displayed by--> Chrome["Chrome Browser"];
```

---

## 🖥️ How to Use

### Installation

1. **Download/Clone this repository**
2. **Open Chrome and go to:** `chrome://extensions/`
3. **Enable "Developer mode"** (toggle in top right)
4. **Click "Load unpacked"** and select the `chrome-extension` folder
5. **The extension icon will appear** in your Chrome toolbar

### Usage

1. **Login to Instagram** in Chrome normally
2. **Navigate to the target page:**
   - **To Follow:** Go to any user's profile → Click "followers" (URL should be `instagram.com/USERNAME/followers/`)
   - **To Unfollow:** Go to your own profile → Click "following" (URL should be `instagram.com/YOUR_USERNAME/following/`)
3. **Click the extension icon** in Chrome toolbar
4. **The popup will detect the page type** and show appropriate options
5. **Enter the number** of users to follow/unfollow (1-50)
6. **Click START** and watch the automation work
7. **Monitor progress** in the status area
8. **Check "FOLLOWED LIST"** to see stored usernames count

---

## ⚙️ Technical Details

### Enhanced Page Detection System
- **Multi-Layer Detection:** URL → Modal → Buttons → Title → Ultimate Fallback
- **URL-Based Detection:** Primary method checks URL for `/followers/` or `/following/`
- **Modal Dialog Analysis:** Checks Instagram's modal content for page type
- **Button Detection:** Multiple methods to find follow/following buttons
- **Comprehensive Logging:** Detailed console output for debugging
- **Real-time Feedback:** Shows detection process in console

### Advanced Button Detection
- **Text-Based Detection:** Looks for exact "Follow" vs "Following" text
- **Nested Structure Scanning:** Searches div elements within buttons
- **Multiple Fallback Methods:** Several approaches to find buttons
- **Detailed Logging:** Shows button text and detection process
- **Robust Against Changes:** Adapts to Instagram's dynamic HTML

### Follow/Unfollow Logic
- **Exact Count:** Follows/unfollows exactly the number you specify
- **Random Delays:** 0.7-2.5 second random delays between actions (human-like behavior)
- **Username Storage:** Stores followed usernames in Chrome's local storage
- **Targeted Unfollowing:** Only unfollows users from stored list
- **Smart Scrolling:** Automatically scrolls to find more users if needed
- **Progress Tracking:** Real-time status updates with timestamps

### Username Storage System
- **Chrome Storage:** Uses `chrome.storage.local` for persistence
- **Memory Array:** Maintains `followedUsernames` array in content script
- **Automatic Saving:** Saves after each successful follow
- **Targeted Unfollowing:** Only attempts to unfollow stored usernames
- **UI Integration:** Shows count and provides clear list button

### Safety Features
- **Session Management:** Uses your real browser session (no separate login)
- **Manual Navigation:** You control which pages to automate
- **Random Delays:** 0.7-2.5 second random intervals prevent detection
- **Status Updates:** Real-time feedback on progress with timestamps
- **Error Handling:** Graceful handling of missing elements or Instagram changes
- **Rate Limit Awareness:** Stops if Instagram blocks actions

---

## 📦 Extension Structure

### Files
- `manifest.json` - Extension permissions and configuration with storage access
- `popup.html` - User interface with vintage Windows styling and followed list
- `popup.js` - Interface logic, Chrome messaging, and storage management
- `content.js` - Instagram page automation with enhanced detection and username storage
- `icon16.png`, `icon32.png`, `icon48.png`, `icon128.png` - Extension icons

### Permissions
- `activeTab` - Access to current Instagram tab
- `storage` - Save and load followed usernames across sessions

---

## 🚨 Usage Instructions

### To Follow Users:
1. Go to any Instagram user's profile (e.g., `instagram.com/1001tracklists/`)
2. Click "followers" to open the followers list (URL becomes `instagram.com/1001tracklists/followers/`)
3. Click the extension icon
4. Enter number to follow and click "START FOLLOWING"
5. Watch the "FOLLOWED LIST" count increase

### To Unfollow Users:
1. Go to your own Instagram profile  
2. Click "following" to open your following list (URL becomes `instagram.com/YOUR_USERNAME/following/`)
3. Click the extension icon
4. Enter number to unfollow and click "START UNFOLLOWING"
5. Only users from your stored list will be unfollowed

---

## 🛡️ Safety & Detection

- **Undetectable:** Uses your real browser session and manual navigation
- **Random Delays:** 0.7-2.5 second random delays mimic human behavior
- **No Automation Detection:** Since you manually navigate and use real session
- **Rate Limit Aware:** Stops if Instagram blocks actions
- **Manual Override:** You can stop automation at any time by closing the popup
- **Username Storage:** Targeted unfollowing reduces unnecessary actions

---

## 🔧 Debugging

### Console Debugging
- **Open Developer Tools:** Press F12 on Instagram page
- **Check Console:** Look for debug messages with 🔍, ✅, ❌ emojis
- **Test Functions:** Type `testPageDetection()` or `testUrlDetection()` in console
- **Monitor Status:** Watch real-time status updates in extension popup

### Enhanced Debugging Functions
- **`testPageDetection()`:** Comprehensive page detection test with detailed logging
- **`testUrlDetection()`:** URL pattern matching test
- **`debugPageDetection()`:** Basic page detection debugging
- **Button Detection Logs:** Shows button text and detection methods used

### Common Issues & Solutions
- **"Could not detect page type":** 
  - Reload the extension
  - Refresh the Instagram page
  - Wait for modal to fully load
  - Run `testPageDetection()` in console
- **"No follow buttons found":** 
  - Instagram may have changed button structure
  - Check console for button detection logs
  - Try the ultimate fallback method
- **Extension not loading:** 
  - Check that you loaded the `chrome-extension` folder
  - Enable developer mode in Chrome
  - Reload the extension

### Debugging Sequence
1. **Reload extension** → `chrome://extensions/` → refresh icon
2. **Refresh Instagram page** → wait for modal to load
3. **Open console** → run `testPageDetection()`
4. **Check button logs** → look for "🔍 Button text:" messages
5. **Monitor detection** → watch for "✅ DETECTED:" messages

---

## ⚠️ Important Notes

- **Manual Navigation Required:** You must manually navigate to the Instagram page you want to automate
- **Real Session:** Uses your actual Instagram login session
- **Rate Limits:** Instagram may still apply rate limits for excessive actions
- **Page Refresh:** If Instagram refreshes the page, just reopen the extension
- **Browser Required:** Must use Chrome browser with extension installed
- **URL Pattern:** Must be on page with URL pattern `instagram.com/USERNAME/followers/` or `instagram.com/USERNAME/following/`
- **Username Storage:** Followed usernames are stored locally in your browser
- **Clear List:** Use "CLEAR LIST" button to reset stored usernames

---

## ⚠️ Disclaimer

This tool is for educational and personal use only. Use responsibly and in accordance with Instagram's terms of service. The extension works with your real Instagram account, so exercise caution with the number of actions performed. Username storage is local to your browser and not shared with any external services. 