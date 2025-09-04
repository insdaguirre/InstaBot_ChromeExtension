# 📸 Instagram Bot - Chrome Extension

![Instagram Bot Extension](render.png)

A powerful Chrome extension for Instagram automation that works directly in your browser. Follow users from followers lists and unfollow them selectively using intelligent batch management and search-based detection. **Features smart private account detection and persistent batch storage!**

---

## 🚀 Key Features

- **🎯 Intelligent Following:** Automatically detects and skips private accounts
- **📦 Batch Management:** Organizes follows into timestamped batches for easy tracking
- **🔍 Search-Based Unfollowing:** Uses Instagram's search to find users quickly
- **💾 Persistent Storage:** Batches survive browser restarts, device shutdowns, and Chrome updates
- **☑️ Checkbox Selection:** Select specific batches to unfollow with easy checkbox interface
- **🛡️ Undetectable:** Uses your real browser session with natural human-like timing
- **🔄 Automatic Cleanup:** Removes private account follow requests immediately

---

## 🛠️ How It Works

### Smart Following System

1. **Navigate to any user's followers page**
2. **Click "START FOLLOWING"** with your desired count (1-50)
3. **Automatic detection:**
   - **Public accounts:** Button changes "Follow" → "Following" ✅ (Added to batch)
   - **Private accounts:** Button changes "Follow" → "Requested" → Automatically unfollowed 🔄 (Not stored)
4. **Batch creation:** New timestamped batch created with only public accounts
5. **Persistent storage:** Batch saved permanently until you choose to unfollow

### Intelligent Unfollowing System

1. **Navigate to your following page**
2. **Select batches** using checkboxes
3. **Click "UNFOLLOW SELECTED"**
4. **Search-based unfollowing:** Extension types each username into Instagram's search
5. **Automatic processing:** Finds and unfollows each user efficiently
6. **Status tracking:** Users marked as unfollowed but batch data preserved for records

---

## 📦 Batch Storage System

### What Gets Stored

Each batch contains:
```javascript
{
  id: "batch_1694123456789_abc123def",
  timestamp: "2025-09-04T18:49:00.000Z",
  source_accounts: ["boilerroomtv"],
  users: [
    {
      username: "user123",
      followed_at: "2025-09-04T18:49:15.123Z",
      unfollowed: false,
      unfollowed_at: null,
      source_account: "boilerroomtv"
    }
  ],
  completed: true
}
```

### Storage Guarantees

**✅ Data Persists Through:**
- Browser closing and reopening
- Computer shutdown and restart
- Chrome updates
- Extension reloads/updates
- Time passing (no expiration)

**❌ Data Only Deleted When:**
- Extension is manually uninstalled
- User clears all Chrome extension data
- (Currently batches are preserved even after unfollowing for record keeping)

### Storage Location
- **Chrome's `chrome.storage.local`** - Official Chrome extension storage API
- **Isolated and secure** - Only this extension can access the data
- **No cloud sync** - Data stays on your device
- **No size limits** for practical usage

---

## 🖥️ Installation & Setup

### Installation
1. **Download/Clone this repository**
2. **Open Chrome:** `chrome://extensions/`
3. **Enable "Developer mode"** (toggle top-right)
4. **Click "Load unpacked"** 
5. **Select the `chrome-extension-clean` folder**
6. **Extension icon appears** in Chrome toolbar

### First Use
1. **Login to Instagram** in Chrome normally
2. **Navigate to target page:**
   - **Following:** Any user's profile → "followers" 
   - **Unfollowing:** Your profile → "following"
3. **Click extension icon**
4. **Interface adapts** based on page type

---

## 📋 User Interface

### Following Page
```
✅ Ready to follow users from this followers list
┌─ FOLLOW USERS ─────────────────────┐
│ Number to follow: [10] ▼           │
│ [START FOLLOWING]                  │
└────────────────────────────────────┘
```

### Following Management Page  
```
✅ Ready to unfollow users from your following list
┌─ UNFOLLOW BATCHES ─────────────────┐
│ 9/4/2025 06:49 PM                 │
│ Users: 3 • Unfollowed: 0           │
│ Sources: boilerroomtv              │
│ ☑️ Select to unfollow 3 users      │
│                                    │
│ [UNFOLLOW SELECTED] [🔄 REFRESH]   │
└────────────────────────────────────┘
```

---

## ⚙️ Technical Details

### Following Logic
- **Page detection:** Automatically detects followers vs following pages
- **Button monitoring:** Watches for state changes after clicking "Follow"
- **Private account detection:** "Requested" = private → auto-unfollow
- **Public account confirmation:** "Following" = public → add to batch
- **Smart scrolling:** Loads more users when needed
- **Random delays:** 0.7-2.5 seconds between actions
- **Batch creation:** Each session creates new timestamped batch

### Unfollowing Logic
- **Search-based:** Types username into Instagram's search input
- **Multiple strategies:** Tries different input selectors for reliability
- **Checkbox selection:** Users choose which batches to process
- **Automatic cleanup:** Clears search after each user
- **Fallback scrolling:** Manual search if search input unavailable
- **Status tracking:** Marks users as unfollowed but preserves data

### Safety Features
- **Real session:** Uses your actual Instagram login
- **Manual navigation:** You control which pages to automate
- **Human-like timing:** Multiple random delays
- **Error handling:** Graceful failure if elements change
- **Rate limit aware:** Respects Instagram's limits
- **Manual override:** Close popup to stop at any time

---

## 🔄 Workflow Examples

### Following Workflow
```
1. Navigate to @boilerroomtv → followers
2. Open extension → Enter "5" → START FOLLOWING
3. Extension processes users:
   - user1: Follow → Following ✅ (Added to batch)
   - user2: Follow → Requested → Unfollow 🔄 (Skipped)
   - user3: Follow → Following ✅ (Added to batch)
   - user4: Follow → Following ✅ (Added to batch)
   - user5: Follow → Following ✅ (Added to batch)
   - user6: Follow → Following ✅ (Added to batch)
4. Batch created with 5 public accounts
5. Status: "Successfully followed 5 public users!"
```

### Unfollowing Workflow
```
1. Navigate to your following page
2. Open extension → See batch list
3. Check box next to desired batch
4. Click UNFOLLOW SELECTED
5. Extension searches for each user:
   - Types "user1" → Find → Unfollow ✅
   - Types "user3" → Find → Unfollow ✅
   - Types "user5" → Find → Unfollow ✅
6. Users marked as unfollowed, batch preserved
```

---

## 📁 Project Structure

```
chrome-extension-clean/
├── manifest.json          # Extension configuration
├── popup.html            # UI interface (Windows 95 style)
├── popup.js              # UI logic and messaging
├── content.js            # Instagram automation logic
├── batches.json          # Sample batch data (not used actively)
└── icons/                # Extension icons
```

### Key Components

**`manifest.json`**
- Extension permissions ("activeTab", "storage")
- Content script injection for Instagram
- Popup configuration

**`popup.html`**
- Vintage Windows 95 styled interface
- Adaptive UI based on page type
- Real-time status updates

**`popup.js`**
- Page detection and UI updates
- Chrome messaging to content script
- Batch loading and display
- Checkbox selection handling

**`content.js`**
- Instagram page automation
- Button state monitoring
- Search-based user finding
- Batch creation and storage
- Chrome storage API integration

---

## 🔍 Advanced Features

### Private Account Detection
```javascript
// Monitors button text changes
"Follow" → "Following" = Public account ✅
"Follow" → "Requested" = Private account → Auto-unfollow 🔄
```

### Search-Based Unfollowing
```javascript
// Uses Instagram's search input
searchInput.value = username;
searchInput.dispatchEvent(new Event('input'));
// Finds user in results and clicks unfollow
```

### Persistent Storage
```javascript
// Saves to Chrome's secure storage
await chrome.storage.local.set({ followBatches: batches });
// Data survives browser restarts, shutdowns, etc.
```

### Checkbox Selection
```javascript
// Multiple batch selection
const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
// Process each selected batch
```

---

## ⚠️ Important Notes

### Usage Guidelines
- **Manual navigation required:** You choose which pages to automate
- **Respect rate limits:** Instagram may limit actions if done too frequently
- **Use responsibly:** Follow Instagram's terms of service
- **Monitor your account:** Check for any Instagram warnings or restrictions

### Data Privacy
- **Local storage only:** All data stays on your device
- **No external servers:** Nothing sent outside your browser
- **Secure storage:** Uses Chrome's encrypted storage API
- **User controlled:** Only you can access or delete the data

### Browser Requirements
- **Chrome browser required:** Extension built for Chrome
- **Developer mode:** Needed for unpacked extension installation
- **Instagram login:** Must be logged into Instagram in Chrome

---

## 🛡️ Safety & Detection Avoidance

### Undetectable Design
- **Real browser session:** Uses your actual Chrome browser
- **Manual navigation:** You control page selection
- **Human-like timing:** Random delays between actions
- **Native Instagram features:** Uses Instagram's own search functionality
- **No external requests:** All actions happen within Instagram

### Natural Behavior Simulation
- **Variable delays:** 0.7-2.5 second random intervals
- **Smart scrolling:** Mimics natural user scrolling
- **Button state monitoring:** Waits for natural page updates
- **Search usage:** Uses Instagram's built-in search like a real user
- **Session respect:** Works within your existing login session

---

## 🔧 Troubleshooting

### Common Issues

**Extension not detecting page:**
- Make sure you're on Instagram.com
- Navigate to followers or following page
- Refresh page and try again

**Following not working:**
- Ensure you're on a user's followers page (not following)
- Check if Instagram has temporary restrictions
- Try with smaller numbers (5-10 users)

**Unfollowing stuck:**
- Make sure you're on your own following page  
- Check if users still exist (accounts may be deleted)
- Try refreshing and reloading extension

**Batches not loading:**
- Reload extension in chrome://extensions/
- Check Chrome storage permissions
- Try refreshing batches button

### Support
- Check browser console for error messages
- Ensure Chrome developer mode is enabled
- Verify extension has proper permissions
- Test with small numbers first

---

## 🚨 Disclaimer

This tool is for educational and personal use only. Use responsibly and in accordance with Instagram's terms of service. The extension works with your real Instagram account, so exercise caution with the number of actions performed. The developers are not responsible for any account restrictions or violations that may result from misuse of this tool.

**Always respect others' privacy and Instagram's community guidelines.**