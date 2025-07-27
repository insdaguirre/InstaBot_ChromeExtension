// content.js - Runs on Instagram pages and performs automation

let isRunning = false;

// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'checkPage') {
        const pageInfo = checkCurrentPage();
        sendResponse(pageInfo);
    } else if (request.action === 'startFollowing') {
        if (!isRunning) {
            startFollowing(request.count).then(result => {
                sendResponse(result);
            });
        } else {
            sendResponse({message: "❌ Already running, please wait..."});
        }
        return true; // Indicates we will respond asynchronously
    } else if (request.action === 'startUnfollowing') {
        if (!isRunning) {
            startUnfollowing(request.count).then(result => {
                sendResponse(result);
            });
        } else {
            sendResponse({message: "❌ Already running, please wait..."});
        }
        return true; // Indicates we will respond asynchronously
    }
});

// Check what page we're currently on
function checkCurrentPage() {
    const url = window.location.href;
    
    if (url.includes('/followers/')) {
        const username = extractUsernameFromUrl(url);
        return {
            pageType: 'followers',
            pageInfo: `Followers of @${username}`
        };
    } else if (url.includes('/following/')) {
        const username = extractUsernameFromUrl(url);
        return {
            pageType: 'following',
            pageInfo: `Following of @${username}`
        };
    } else {
        return {
            pageType: 'other',
            pageInfo: 'Not on followers/following page'
        };
    }
}

// Extract username from Instagram URL
function extractUsernameFromUrl(url) {
    const match = url.match(/instagram\.com\/([^\/]+)\/(followers|following)/);
    return match ? match[1] : 'unknown';
}

// Start following users
async function startFollowing(count) {
    isRunning = true;
    let followed = 0;
    
    updateStatus(`🎯 Looking for follow buttons...`);
    
    try {
        // Wait for modal to be ready
        await waitForElement('div[role="dialog"]', 5000);
        
        let attempts = 0;
        let maxAttempts = 20;
        
        while (followed < count && attempts < maxAttempts) {
            const followButtons = document.querySelectorAll('button:has(div:contains("Follow")):not(:has(div:contains("Following")))');
            
            if (followButtons.length === 0) {
                updateStatus(`📜 Scrolling to find more users...`);
                scrollModal();
                await sleep(2000);
                attempts++;
                continue;
            }
            
            // Process visible follow buttons
            for (let button of followButtons) {
                if (followed >= count) break;
                
                try {
                    // Get username
                    const username = getUsernameFromButton(button);
                    
                    if (username) {
                        updateStatus(`⏳ Following @${username} (${followed + 1}/${count})`);
                        
                        // Click follow button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500);
                        button.click();
                        followed++;
                        
                        updateStatus(`✅ Followed @${username} (${followed}/${count})`);
                        
                        // Wait between follows
                        await sleep(1000);
                    }
                } catch (error) {
                    console.log('Error following user:', error);
                }
            }
            
            // Scroll to load more users if needed
            if (followed < count) {
                scrollModal();
                await sleep(2000);
            }
            
            attempts++;
        }
        
        const message = followed === count 
            ? `🎉 Successfully followed ${followed} users!`
            : `⚠️ Followed ${followed}/${count} users (no more available)`;
            
        updateStatus(message);
        return {message};
        
    } catch (error) {
        const errorMsg = `❌ Error: ${error.message}`;
        updateStatus(errorMsg);
        return {message: errorMsg};
    } finally {
        isRunning = false;
    }
}

// Start unfollowing users
async function startUnfollowing(count) {
    isRunning = true;
    let unfollowed = 0;
    
    updateStatus(`🎯 Looking for following buttons...`);
    
    try {
        // Wait for modal to be ready
        await waitForElement('div[role="dialog"]', 5000);
        
        let attempts = 0;
        let maxAttempts = 20;
        
        while (unfollowed < count && attempts < maxAttempts) {
            const followingButtons = document.querySelectorAll('button:has(div:contains("Following"))');
            
            if (followingButtons.length === 0) {
                updateStatus(`📜 Scrolling to find more users...`);
                scrollModal();
                await sleep(2000);
                attempts++;
                continue;
            }
            
            // Process visible following buttons
            for (let button of followingButtons) {
                if (unfollowed >= count) break;
                
                try {
                    // Get username
                    const username = getUsernameFromButton(button);
                    
                    if (username) {
                        updateStatus(`⏳ Unfollowing @${username} (${unfollowed + 1}/${count})`);
                        
                        // Click following button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500);
                        button.click();
                        
                        // Wait for and click unfollow confirmation
                        await sleep(1000);
                        const unfollowBtn = document.querySelector('button:contains("Unfollow")');
                        if (unfollowBtn) {
                            unfollowBtn.click();
                        }
                        
                        unfollowed++;
                        updateStatus(`✅ Unfollowed @${username} (${unfollowed}/${count})`);
                        
                        // Wait between unfollows
                        await sleep(1000);
                    }
                } catch (error) {
                    console.log('Error unfollowing user:', error);
                }
            }
            
            // Scroll to load more users if needed
            if (unfollowed < count) {
                scrollModal();
                await sleep(2000);
            }
            
            attempts++;
        }
        
        const message = unfollowed === count 
            ? `🎉 Successfully unfollowed ${unfollowed} users!`
            : `⚠️ Unfollowed ${unfollowed}/${count} users (no more available)`;
            
        updateStatus(message);
        return {message};
        
    } catch (error) {
        const errorMsg = `❌ Error: ${error.message}`;
        updateStatus(errorMsg);
        return {message: errorMsg};
    } finally {
        isRunning = false;
    }
}

// Get username from a follow/following button
function getUsernameFromButton(button) {
    try {
        const userContainer = button.closest('div[role="dialog"] div').querySelector('a[href*="/"]');
        if (userContainer) {
            const href = userContainer.href;
            const match = href.match(/instagram\.com\/([^\/\?]+)/);
            return match ? match[1] : null;
        }
    } catch (error) {
        console.log('Error extracting username:', error);
    }
    return null;
}

// Scroll the modal to load more users
function scrollModal() {
    const modal = document.querySelector('div[role="dialog"]');
    if (modal) {
        const scrollableElement = modal.querySelector('div[style*="overflow"]') || modal;
        scrollableElement.scrollTop = scrollableElement.scrollHeight;
    }
}

// Wait for element to appear
function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }
        
        const observer = new MutationObserver((mutations) => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
        }, timeout);
    });
}

// Sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Send status update to popup
function updateStatus(message) {
    chrome.runtime.sendMessage({
        action: 'updateStatus',
        message: message
    });
}

// Enhanced selector for buttons containing text
Element.prototype.contains = function(text) {
    return this.textContent.includes(text);
};

// CSS selector enhancement for :contains
document.querySelectorAll = (function(original) {
    return function(selector) {
        if (selector.includes(':contains(')) {
            const match = selector.match(/(.*):contains\("([^"]+)"\)(.*)/);
            if (match) {
                const [, prefix, text, suffix] = match;
                const elements = original.call(this, prefix + suffix);
                return Array.from(elements).filter(el => el.textContent.includes(text));
            }
        }
        return original.call(this, selector);
    };
})(document.querySelectorAll); 