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
    console.log('🔍 Checking page with URL:', url);
    
    // Check if we're on Instagram at all
    if (!url.includes('instagram.com')) {
        console.log('❌ Not on Instagram');
        return {
            pageType: 'other',
            pageInfo: 'Not on Instagram'
        };
    }
    
    // SIMPLE URL-BASED DETECTION (most reliable)
    if (url.includes('/followers/')) {
        const username = extractUsernameFromUrl(url);
        console.log('✅ DETECTED: Followers page for @', username);
        return {
            pageType: 'followers',
            pageInfo: `Followers of @${username}`
        };
    }
    
    if (url.includes('/following/')) {
        const username = extractUsernameFromUrl(url);
        console.log('✅ DETECTED: Following page for @', username);
        return {
            pageType: 'following',
            pageInfo: `Following of @${username}`
        };
    }
    
    // FALLBACK: Check for follow buttons (if URL doesn't work)
    const followButtons = findFollowButtons();
    const followingButtons = findFollowingButtons();
    
    console.log('🔍 Found follow buttons:', followButtons.length);
    console.log('🔍 Found following buttons:', followingButtons.length);
    
    if (followButtons.length > 0) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Followers page via buttons for @', username);
        return {
            pageType: 'followers',
            pageInfo: `Followers of @${username}`
        };
    }
    
    if (followingButtons.length > 0) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Following page via buttons for @', username);
        return {
            pageType: 'following',
            pageInfo: `Following of @${username}`
        };
    }
    
    console.log('❌ Could not detect page type');
    console.log('URL was:', url);
    return {
        pageType: 'other',
        pageInfo: 'Not on followers/following page'
    };
}

// Debug function - can be called from console
function debugPageDetection() {
    console.log('🔍 === DEBUG PAGE DETECTION ===');
    console.log('URL:', window.location.href);
    console.log('Page title:', document.title);
    
    // Check for followers text
    const followersElements = Array.from(document.querySelectorAll('*')).filter(el => 
        el.textContent && el.textContent.toLowerCase().includes('followers')
    );
    console.log('Elements with "followers":', followersElements.length);
    
    // Check for follow buttons
    const followButtons = findFollowButtons();
    console.log('Follow buttons found:', followButtons.length);
    if (followButtons.length > 0) {
        console.log('First follow button:', followButtons[0]);
        console.log('First button text:', followButtons[0].textContent);
    }
    
    // Check for modal
    const modal = document.querySelector('div[role="dialog"]');
    console.log('Modal found:', !!modal);
    if (modal) {
        console.log('Modal text:', modal.textContent.substring(0, 200));
    }
    
    // Test page detection
    const result = checkCurrentPage();
    console.log('Page detection result:', result);
    
    console.log('🔍 === END DEBUG ===');
    return result;
}

// Make debug function available globally
window.debugPageDetection = debugPageDetection;

// Extract username from Instagram URL
function extractUsernameFromUrl(url) {
    console.log('🔍 Extracting username from URL:', url);
    
    // Method 1: Direct pattern matching for followers/following
    const followersMatch = url.match(/instagram\.com\/([^\/]+)\/followers/);
    if (followersMatch) {
        console.log('✅ Found username from followers URL:', followersMatch[1]);
        return followersMatch[1];
    }
    
    const followingMatch = url.match(/instagram\.com\/([^\/]+)\/following/);
    if (followingMatch) {
        console.log('✅ Found username from following URL:', followingMatch[1]);
        return followingMatch[1];
    }
    
    // Method 2: General Instagram username pattern
    const generalMatch = url.match(/instagram\.com\/([^\/\?]+)/);
    if (generalMatch && generalMatch[1] && !generalMatch[1].includes('/')) {
        console.log('✅ Found username from general URL:', generalMatch[1]);
        return generalMatch[1];
    }
    
    console.log('❌ Could not extract username from URL');
    return 'unknown';
}

// Extract username from the current page (not just URL)
function extractUsernameFromPage() {
    // Method 1: Try to get from URL first
    const url = window.location.href;
    const urlMatch = url.match(/instagram\.com\/([^\/]+)/);
    if (urlMatch && urlMatch[1] && !urlMatch[1].includes('/')) {
        return urlMatch[1];
    }
    
    // Method 2: Look for username in page elements
    const usernameElements = document.querySelectorAll('a[href*="/"]');
    for (let element of usernameElements) {
        const href = element.href;
        const match = href.match(/instagram\.com\/([^\/\?]+)/);
        if (match && match[1] && match[1] !== 'p' && match[1] !== 'explore' && match[1] !== 'accounts') {
            return match[1];
        }
    }
    
    // Method 3: Look for username in text content
    const pageText = document.body.textContent;
    const usernameMatch = pageText.match(/@([a-zA-Z0-9._]+)/);
    if (usernameMatch) {
        return usernameMatch[1];
    }
    
    return 'unknown';
}

// Get random delay between 0.7 and 2.5 seconds
function getRandomDelay() {
    return Math.random() * (2.5 - 0.7) + 0.7;
}

// Find follow buttons with compatible selector
function findFollowButtons() {
    // Look for buttons with Instagram's specific class structure
    const buttons = document.querySelectorAll('button');
    return Array.from(buttons).filter(button => {
        // Check if button contains a div with the specific Instagram classes
        const followDiv = button.querySelector('div._ap3a._aaco._aacw._aad6._aade');
        if (followDiv) {
            const buttonText = followDiv.textContent.toLowerCase();
            return buttonText.includes('follow') && !buttonText.includes('following');
        }
        
        // Fallback: check button text directly
        const buttonText = button.textContent.toLowerCase();
        return buttonText.includes('follow') && !buttonText.includes('following');
    });
}

// Find following buttons with compatible selector
function findFollowingButtons() {
    const buttons = document.querySelectorAll('button');
    return Array.from(buttons).filter(button => {
        // Check if button contains a div with the specific Instagram classes
        const followDiv = button.querySelector('div._ap3a._aaco._aacw._aad6._aade');
        if (followDiv) {
            const buttonText = followDiv.textContent.toLowerCase();
            return buttonText.includes('following');
        }
        
        // Fallback: check button text directly
        const buttonText = button.textContent.toLowerCase();
        return buttonText.includes('following');
    });
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
            const followButtons = findFollowButtons();
            
            updateStatus(`🔍 Found ${followButtons.length} follow buttons (attempt ${attempts + 1})`);
            
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
                        
                        // Random delay before clicking
                        const delay = getRandomDelay();
                        updateStatus(`⏳ Waiting ${delay.toFixed(1)}s before following @${username}...`);
                        await sleep(delay * 1000);
                        
                        // Click follow button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500);
                        button.click();
                        followed++;
                        
                        updateStatus(`✅ Followed @${username} (${followed}/${count})`);
                        
                        // Random delay between follows
                        const nextDelay = getRandomDelay();
                        updateStatus(`⏳ Waiting ${nextDelay.toFixed(1)}s before next follow...`);
                        await sleep(nextDelay * 1000);
                    } else {
                        updateStatus(`⚠️ Could not extract username from button`);
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
            const followingButtons = findFollowingButtons();
            
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
                        
                        // Random delay before clicking
                        const delay = getRandomDelay();
                        updateStatus(`⏳ Waiting ${delay.toFixed(1)}s before unfollowing @${username}...`);
                        await sleep(delay * 1000);
                        
                        // Click following button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500);
                        button.click();
                        
                        // Wait for and click unfollow confirmation
                        await sleep(1000);
                        const unfollowBtn = findUnfollowButton();
                        if (unfollowBtn) {
                            unfollowBtn.click();
                        }
                        
                        unfollowed++;
                        updateStatus(`✅ Unfollowed @${username} (${unfollowed}/${count})`);
                        
                        // Random delay between unfollows
                        const nextDelay = getRandomDelay();
                        updateStatus(`⏳ Waiting ${nextDelay.toFixed(1)}s before next unfollow...`);
                        await sleep(nextDelay * 1000);
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

// Find unfollow button in confirmation dialog
function findUnfollowButton() {
    const buttons = document.querySelectorAll('button');
    return Array.from(buttons).find(button => {
        const buttonText = button.textContent.toLowerCase();
        return buttonText.includes('unfollow');
    });
}

// Get username from a follow/following button
function getUsernameFromButton(button) {
    try {
        // Method 1: Look for username in the same container as the button
        const userContainer = button.closest('div[role="dialog"] div');
        if (userContainer) {
            // Look for any link that contains a username
            const links = userContainer.querySelectorAll('a[href*="/"]');
            for (let link of links) {
                const href = link.href;
                const match = href.match(/instagram\.com\/([^\/\?]+)/);
                if (match && match[1] && match[1] !== 'p' && match[1] !== 'explore') {
                    return match[1];
                }
            }
        }
        
        // Method 2: Look for username in parent containers
        let parent = button.parentElement;
        for (let i = 0; i < 5; i++) { // Check up to 5 levels up
            if (!parent) break;
            
            const links = parent.querySelectorAll('a[href*="/"]');
            for (let link of links) {
                const href = link.href;
                const match = href.match(/instagram\.com\/([^\/\?]+)/);
                if (match && match[1] && match[1] !== 'p' && match[1] !== 'explore') {
                    return match[1];
                }
            }
            parent = parent.parentElement;
        }
        
        // Method 3: Look for username in nearby elements
        const nearbyLinks = document.querySelectorAll('a[href*="/"]');
        for (let link of nearbyLinks) {
            const href = link.href;
            const match = href.match(/instagram\.com\/([^\/\?]+)/);
            if (match && match[1] && match[1] !== 'p' && match[1] !== 'explore') {
                // Check if this link is close to our button
                const rect1 = button.getBoundingClientRect();
                const rect2 = link.getBoundingClientRect();
                const distance = Math.sqrt(
                    Math.pow(rect1.left - rect2.left, 2) + 
                    Math.pow(rect1.top - rect2.top, 2)
                );
                if (distance < 200) { // Within 200px
                    return match[1];
                }
            }
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

// Test function for URL detection
function testUrlDetection() {
    console.log('🧪 === TESTING URL DETECTION ===');
    
    // Test with your specific URL
    const testUrl = 'https://www.instagram.com/1001tracklists/followers/';
    console.log('Testing URL:', testUrl);
    
    // Test URL checking
    console.log('URL includes /followers/:', testUrl.includes('/followers/'));
    console.log('URL includes /following/:', testUrl.includes('/following/'));
    
    // Test username extraction
    const username = extractUsernameFromUrl(testUrl);
    console.log('Extracted username:', username);
    
    // Test page detection
    const result = {
        pageType: testUrl.includes('/followers/') ? 'followers' : 
                  testUrl.includes('/following/') ? 'following' : 'other',
        pageInfo: testUrl.includes('/followers/') ? `Followers of @${username}` :
                  testUrl.includes('/following/') ? `Following of @${username}` : 'Unknown'
    };
    
    console.log('Page detection result:', result);
    console.log('🧪 === END TEST ===');
    return result;
}

// Make test function available globally
window.testUrlDetection = testUrlDetection; 