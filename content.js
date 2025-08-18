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
    let privateAccountsUnfollowed = 0;
    
    updateStatus(`🎯 Looking for follow buttons...`);
    
    try {
        // Wait for modal to be ready
        await waitForElement('div[role="dialog"]', 5000);
        
        let attempts = 0;
        let maxAttempts = 20;
        
        while (followed < count && attempts < maxAttempts) {
            // Only look for buttons that say "Follow" (not "Following" or "Requested")
            // Use a more robust selector that handles different button structures
            let followButtons = document.querySelectorAll('button');
            followButtons = Array.from(followButtons).filter(button => {
                const text = button.textContent.trim();
                return text.includes('Follow') && !text.includes('Following') && !text.includes('Requested');
            });
            
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
                        
                        // Store original button text and find the user row for reliable button tracking
                        const originalText = button.textContent.trim();
                        const userRow = button.closest('div[role="dialog"] div');
                        
                        if (!userRow) {
                            updateStatus(`⚠️ Could not find user row for @${username}, skipping...`);
                            continue;
                        }
                        
                        // Click follow button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500);
                        button.click();
                        
                        // Wait longer for Instagram's UI to update and stabilize
                        await sleep(2000);
                        
                        // Find the updated button by looking in the same user row
                        let updatedButton = null;
                        let attempts = 0;
                        const maxAttempts = 5;
                        
                        while (!updatedButton && attempts < maxAttempts) {
                            // Look for the button in the same user row
                            const buttons = userRow.querySelectorAll('button');
                            for (let btn of buttons) {
                                const btnText = btn.textContent.trim();
                                // Check if this button has changed from the original state
                                if (btnText !== originalText && (btnText.includes('Following') || btnText.includes('Requested'))) {
                                    updatedButton = btn;
                                    break;
                                }
                            }
                            
                            if (!updatedButton) {
                                // Wait a bit more and try again
                                await sleep(500);
                                attempts++;
                            }
                        }
                        
                        if (!updatedButton) {
                            updateStatus(`❓ Could not detect button state change for @${username}, skipping...`);
                            continue;
                        }
                        
                        const newText = updatedButton.textContent.trim();
                        
                        console.log(`Button state change for @${username}: "${originalText}" -> "${newText}"`);
                        
                        if (newText.includes("Following")) {
                            // Public account - successfully followed
                            followed++;
                            updateStatus(`✅ Followed @${username} (public account) (${followed}/${count})`);
                        } else if (newText.includes("Requested")) {
                            // Private account - unfollow it
                            updateStatus(`⚠️ @${username} is private, unfollowing...`);
                            
                            // Wait for the button to fully stabilize
                            await sleep(1500);
                            
                            // Click the button again to unfollow
                            updatedButton.click();
                            await sleep(1500);
                            
                            // Look for unfollow confirmation button with multiple methods
                            let unfollowBtn = null;
                            
                            // Method 1: Look for button with "Unfollow" text
                            unfollowBtn = document.querySelector('button:contains("Unfollow")');
                            
                            // Method 2: Look for button with specific Instagram structure
                            if (!unfollowBtn) {
                                const allButtons = document.querySelectorAll('button');
                                for (let btn of allButtons) {
                                    if (btn.textContent.trim().includes('Unfollow')) {
                                        unfollowBtn = btn;
                                        break;
                                    }
                                }
                            }
                            
                            // Method 3: Look for button in the confirmation dialog
                            if (!unfollowBtn) {
                                const dialogs = document.querySelectorAll('div[role="dialog"]');
                                for (let dialog of dialogs) {
                                    const btn = dialog.querySelector('button');
                                    if (btn && btn.textContent.trim().includes('Unfollow')) {
                                        unfollowBtn = btn;
                                        break;
                                    }
                                }
                            }
                            
                            if (unfollowBtn) {
                                unfollowBtn.click();
                                await sleep(1000);
                                privateAccountsUnfollowed++;
                                updateStatus(`🔄 Unfollowed @${username} (private account) - ${privateAccountsUnfollowed} private accounts removed`);
                            } else {
                                updateStatus(`❌ Could not find unfollow confirmation for @${username}, may need manual intervention`);
                                console.log('Unfollow button not found, available buttons:', 
                                    Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()));
                            }
                        } else {
                            // Button didn't change as expected, might be an error
                            updateStatus(`❓ Unexpected button state for @${username}: "${newText}" (expected "Following" or "Requested")`);
                            console.log(`Unexpected button state: "${newText}" for @${username}`);
                        }
                        
                        // Wait between follows
                        await sleep(1000);
                    }
                } catch (error) {
                    console.log('Error following user:', error);
                    updateStatus(`❌ Error following user: ${error.message}`);
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
            ? `🎉 Successfully followed ${followed} public users! (${privateAccountsUnfollowed} private accounts were skipped)`
            : `⚠️ Followed ${followed}/${count} public users (${privateAccountsUnfollowed} private accounts were skipped)`;
            
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

// Enhanced button state detection function
function detectButtonStateChange(originalButton, userRow, originalText) {
    return new Promise(async (resolve) => {
        let updatedButton = null;
        let attempts = 0;
        const maxAttempts = 10; // Increased attempts for better reliability
        
        while (!updatedButton && attempts < maxAttempts) {
            // Look for the button in the same user row
            const buttons = userRow.querySelectorAll('button');
            for (let btn of buttons) {
                const btnText = btn.textContent.trim();
                // Check if this button has changed from the original state
                if (btnText !== originalText && (btnText.includes('Following') || btnText.includes('Requested'))) {
                    updatedButton = btn;
                    break;
                }
            }
            
            if (!updatedButton) {
                // Wait a bit more and try again
                await sleep(300);
                attempts++;
            }
        }
        
        resolve(updatedButton);
    });
}

// Make the function available globally for testing
window.detectButtonStateChange = detectButtonStateChange; 