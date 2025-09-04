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

// Add randomization helper function at the top
function randomDelay(min, max) {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
}

// Start following users
async function startFollowing(count) {
    isRunning = true;
    let followed = 0;
    let privateAccountsUnfollowed = 0;
    
    updateStatus(`🎯 Looking for follow buttons...`);
    
    try {
        // Wait for modal to be ready - try multiple selectors
        let modal = null;
        try {
            modal = await waitForElement('div[role="dialog"]', 3000);
        } catch (e) {
            // Try alternative modal selectors
            modal = document.querySelector('div[role="dialog"]') || 
                   document.querySelector('[data-testid="modal"]') ||
                   document.querySelector('.modal') ||
                   document.querySelector('[class*="modal"]') ||
                   document.querySelector('[class*="dialog"]');
            
            if (!modal) {
                // Wait a bit more and try again
                await sleep(2000, true);
                modal = document.querySelector('div[role="dialog"]') || 
                       document.querySelector('[data-testid="modal"]') ||
                       document.querySelector('.modal') ||
                       document.querySelector('[class*="modal"]') ||
                       document.querySelector('[class*="dialog"]');
            }
        }
        
        if (!modal) {
            throw new Error('Could not find Instagram modal - make sure you are on a followers/following page');
        }
        
        let attempts = 0;
        let maxAttempts = 20;
        
        while (followed < count && attempts < maxAttempts) {
            // Find visible Follow buttons in the modal (exclude Following/Requested)
            const buttonsInModal = Array.from(modal.querySelectorAll('button'));
            let followButtons = buttonsInModal.filter(button => {
                const text = (getButtonText(button) || '').toLowerCase();
                return text.includes('follow') && !text.includes('following') && !text.includes('requested');
            });
            
            updateStatus(`🔍 Found ${followButtons.length} follow buttons (attempt ${attempts + 1}/${maxAttempts})`);
            
            if (followButtons.length === 0) {
                updateStatus(`📜 Scrolling to find more users...`);
                scrollModal(modal);
                await sleep(2000, true);
                attempts++;
                continue;
            }
            
            // Process visible follow buttons
            for (let button of followButtons) {
                if (followed >= count) break;
                
                try {
                    // Extract username for this specific button
                    let displayName = extractUsernameSimple(button, modal);
                    console.log(`Button ${followed + 1}: Extracted username = "${displayName}"`);
                    
                    if (!displayName) {
                        displayName = `user_${followed + 1}`;
                        console.log(`Button ${followed + 1}: Using fallback name = "${displayName}"`);
                    }
                    
                    // Update status with current username
                    console.log(`Button ${followed + 1}: Final display name = "${displayName}"`);
                    updateStatus(`⏳ Following @${displayName} (${followed + 1}/${count})`);
                    
                    // Store original button text and find the user row for reliable button tracking
                    const originalText = (getButtonText(button) || '').toLowerCase();
                    const userRow = button.closest('div[role="dialog"] div') || 
                                  button.closest('li') ||
                                  button.closest('div') || 
                                  button.parentElement;
                    
                    if (!userRow) {
                        updateStatus(`⚠️ Could not find user row for @${displayName}, proceeding anyway...`);
                    }
                    
                    // Click follow button
                    button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    await sleep(500, true);
                    button.click();
                    
                    // Wait longer for button state to change and check multiple times
                    let newText = '';
                    let buttonStateChanged = false;
                    let maxWaitAttempts = 8; // Increased from 4
                    
                    for (let waitAttempt = 0; waitAttempt < maxWaitAttempts; waitAttempt++) {
                        await sleep(800, true); // Increased wait time
                        
                        // Check the original button first
                        newText = (getButtonText(button) || '').toLowerCase();
                        
                        if (newText !== originalText && (newText.includes('following') || newText.includes('requested'))) {
                            buttonStateChanged = true;
                            break;
                        }
                        
                        // If original button hasn't changed, look for updated button in user row
                        if (userRow) {
                            const buttons = userRow.querySelectorAll('button');
                            for (let btn of buttons) {
                                const btnText = (getButtonText(btn) || '').toLowerCase();
                                if (btnText !== originalText && (btnText.includes('following') || btnText.includes('requested'))) {
                                    newText = btnText;
                                    buttonStateChanged = true;
                                    break;
                                }
                            }
                        }
                        
                        if (buttonStateChanged) break;
                    }
                    
                    if (buttonStateChanged && newText.includes('following')) {
                        // Public account - successfully followed
                        followed++;
                        updateStatus(`✅ Followed @${displayName} (public account) (${followed}/${count})`);
                    } else if (buttonStateChanged && newText.includes('requested')) {
                        // Private account - unfollow it
                        updateStatus(`⚠️ @${displayName} is private, unfollowing...`);
                        
                        // Click the button again to open the unfollow confirmation
                        button.click();
                        await sleep(1000, true);
                        
                        // Look for unfollow button with multiple strategies
                        let unfollowBtn = null;
                        
                        // Strategy 1: Look for button with "Unfollow" text
                        const allButtons = document.querySelectorAll('button');
                        for (let btn of allButtons) {
                            const btnText = (getButtonText(btn) || '').toLowerCase();
                            if (btnText.includes('unfollow')) { 
                                unfollowBtn = btn; 
                                break; 
                            }
                        }
                        
                        // Strategy 2: Look in dialogs
                        if (!unfollowBtn) {
                            const dialogs = document.querySelectorAll('div[role="dialog"]');
                            for (let d of dialogs) {
                                for (let b of d.querySelectorAll('button')) {
                                    const btnText = (getButtonText(b) || '').toLowerCase();
                                    if (btnText.includes('unfollow')) { 
                                        unfollowBtn = b; 
                                        break; 
                                    }
                                }
                                if (unfollowBtn) break;
                            }
                        }
                        
                        // Strategy 3: Look for any button containing "unfollow" case-insensitive
                        if (!unfollowBtn) {
                            for (let btn of allButtons) {
                                if (btn.textContent.toLowerCase().includes('unfollow')) {
                                    unfollowBtn = btn;
                                    break;
                                }
                            }
                        }
                        
                        if (unfollowBtn) {
                            unfollowBtn.click();
                            await sleep(600, true);
                            privateAccountsUnfollowed++;
                            updateStatus(`🔄 Unfollowed @${displayName} (private account) (${privateAccountsUnfollowed} private accounts processed)`);
                        } else {
                            updateStatus(`❌ Could not find unfollow confirmation for @${displayName}`);
                        }
                    } else {
                        updateStatus(`❓ Button state unchanged for @${displayName}. Skipping.`);
                    }
                    
                    // Wait between follows with additional randomization
                    await sleep(700, true);
                    // Add extra random delay to make pattern less predictable
                    await randomDelay(200, 800);
                } catch (error) {
                    console.log('Error following user:', error);
                    updateStatus(`❌ Error processing user: ${error.message}`);
                }
            }
            
            // Scroll to load more users if needed
            if (followed < count) {
                scrollModal(modal);
                await sleep(2000, true);
            }
            
            attempts++;
        }
        
        const message = followed === count 
            ? `🎉 Successfully followed ${followed} public users! (${privateAccountsUnfollowed} private accounts were unfollowed)`
            : `⚠️ Followed ${followed}/${count} public users (${privateAccountsUnfollowed} private accounts were unfollowed)`;
            
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
        const modal = await waitForElement('div[role="dialog"]', 5000);
        
        let attempts = 0;
        let maxAttempts = 20;
        
        while (unfollowed < count && attempts < maxAttempts) {
            // Find Following buttons more reliably
            const allButtons = Array.from(modal.querySelectorAll('button'));
            const followingButtons = allButtons.filter(button => {
                const text = (getButtonText(button) || '').toLowerCase();
                return text.includes('following') && !text.includes('unfollow');
            });
            
            updateStatus(`🔍 Found ${followingButtons.length} following buttons (attempt ${attempts + 1}/${maxAttempts})`);
            
            if (followingButtons.length === 0) {
                updateStatus(`📜 Scrolling to find more users...`);
                scrollModal(modal);
                await sleep(2000, true);
                attempts++;
                continue;
            }
            
            // Process visible following buttons
            for (let button of followingButtons) {
                if (unfollowed >= count) break;
                
                try {
                    // Get username with a simpler, more reliable method
                    let displayName = extractUsernameSimple(button, modal);
                    
                    // If no username found, use a unique identifier
                    if (!displayName) {
                        displayName = `user_${unfollowed + 1}`;
                    }
                    
                    updateStatus(`⏳ Unfollowing @${displayName} (${unfollowed + 1}/${count})`);
                    
                    // Click following button
                    button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    await sleep(500, true);
                    button.click();
                    
                    // Wait for unfollow confirmation dialog
                    await sleep(1000, true);
                    
                    // Look for unfollow button with multiple strategies
                    let unfollowBtn = null;
                    
                    // Strategy 1: Look for button with "Unfollow" text
                    const allButtonsAfter = document.querySelectorAll('button');
                    for (let btn of allButtonsAfter) {
                        const btnText = (getButtonText(btn) || '').toLowerCase();
                        if (btnText.includes('unfollow')) { 
                            unfollowBtn = btn; 
                            break; 
                        }
                    }
                    
                    // Strategy 2: Look in dialogs
                    if (!unfollowBtn) {
                        const dialogs = document.querySelectorAll('div[role="dialog"]');
                        for (let d of dialogs) {
                            for (let b of d.querySelectorAll('button')) {
                                const btnText = (getButtonText(b) || '').toLowerCase();
                                if (btnText.includes('unfollow')) { 
                                    unfollowBtn = b; 
                                    break; 
                                }
                            }
                            if (unfollowBtn) break;
                        }
                    }
                    
                    // Strategy 3: Look for any button containing "unfollow" case-insensitive
                    if (!unfollowBtn) {
                        for (let btn of allButtonsAfter) {
                            if (btn.textContent.toLowerCase().includes('unfollow')) {
                                unfollowBtn = btn;
                                break;
                            }
                        }
                    }
                    
                    if (unfollowBtn) {
                        unfollowBtn.click();
                        await sleep(600, true);
                        unfollowed++;
                        updateStatus(`✅ Unfollowed @${displayName} (${unfollowed}/${count})`);
                    } else {
                        updateStatus(`❌ Could not find unfollow confirmation for @${displayName}`);
                    }
                    
                    // Wait between unfollows with additional randomization
                    await sleep(1000, true);
                    // Add extra random delay to make pattern less predictable
                    await randomDelay(300, 1000);
                } catch (error) {
                    console.log('Error unfollowing user:', error);
                    updateStatus(`❌ Error processing user: ${error.message}`);
                }
            }
            
            // Scroll to load more users if needed
            if (unfollowed < count) {
                scrollModal(modal);
                await sleep(2000, true);
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
function getUsernameFromButton(button, modalElement = null) {
    try {
        const modal = modalElement || document.querySelector('div[role="dialog"]');
        // Row that contains avatar, name and the button
        let row = button.closest('div[role="dialog"] li') || button.closest('li') || button.closest('div');

        const reserved = new Set(['p','reel','reels','stories','explore','accounts','direct','about','privacy','terms','developers','directory','web','ajax','i','s','emails','challenge','following','followers']);
        const isValidUser = (name) => /^[a-z0-9._]{1,30}$/i.test(name) && !reserved.has(name.toLowerCase());

        const extractFromAnchors = (root) => {
            const anchors = Array.from(root.querySelectorAll('a[href]'));
            for (const a of anchors) {
                let href = a.getAttribute('href') || '';
                if (!href) continue;
                if (!href.startsWith('http')) {
                    if (!href.startsWith('/')) href = '/' + href;
                }
                try {
                    const u = href.startsWith('http') ? new URL(href) : new URL(href, window.location.origin);
                    const path = u.pathname.replace(/^\/+|\/+$/g, '');
                    if (!path) continue;
                    const parts = path.split('/');
                    if (parts.length !== 1) continue; // only plain profile paths
                    const candidate = parts[0];
                    if (isValidUser(candidate)) return candidate.toLowerCase();
                } catch (_) { /* ignore malformed */ }
            }
            return null;
        };

        const extractFromSpans = (root) => {
            // 1) Exact class stack you provided
            let span = root.querySelector('span._ap3a._aaco._aacw._aacx._aad7._aade');
            if (span) {
                const txt = (span.textContent || '').trim();
                if (isValidUser(txt)) return txt.toLowerCase();
            }
            // 2) Any span with _ap3a and username-looking text
            const spans = Array.from(root.querySelectorAll('span._ap3a'));
            for (const s of spans) {
                const txt = (s.textContent || '').trim();
                if (isValidUser(txt)) return txt.toLowerCase();
            }
            return null;
        };

        // 1) Try within the row first (anchors then spans)
        if (row) {
            let found = extractFromAnchors(row);
            if (found) return found;
            found = extractFromSpans(row);
            if (found) return found;
        }
        // 2) Try within the modal as fallback
        if (modal) {
            let found = extractFromAnchors(modal);
            if (found) return found;
            found = extractFromSpans(modal);
            if (found) return found;
        }
        // 3) Walk up a few parents and try again
        let parent = button.parentElement;
        for (let i = 0; i < 4 && parent; i++) {
            let found = extractFromAnchors(parent);
            if (found) return found;
            found = extractFromSpans(parent);
            if (found) return found;
            parent = parent.parentElement;
        }
        // 4) Geometric fallback: pick nearest visible profile anchor to the button
        const targetRect = button.getBoundingClientRect();
        const candidates = Array.from((modal || document).querySelectorAll('a[href]')).filter(a => a.offsetParent !== null);
        let best = null; let bestDist = Infinity;
        for (const a of candidates) {
            let href = a.getAttribute('href') || '';
            if (!href) continue;
            if (!href.startsWith('http')) { if (!href.startsWith('/')) href = '/' + href; }
            try {
                const u = href.startsWith('http') ? new URL(href) : new URL(href, window.location.origin);
                const path = u.pathname.replace(/^\/+|\/+$/g, '');
                if (!path) continue;
                const parts = path.split('/');
                if (parts.length !== 1) continue;
                const candidate = parts[0];
                if (!isValidUser(candidate)) continue;
                const r = a.getBoundingClientRect();
                const dx = (r.left + r.width/2) - (targetRect.left + targetRect.width/2);
                const dy = (r.top + r.height/2) - (targetRect.top + targetRect.height/2);
                const d2 = dx*dx + dy*dy;
                if (d2 < bestDist) { bestDist = d2; best = candidate.toLowerCase(); }
            } catch (_) { /* ignore */ }
        }
        if (best) return best;
    } catch (error) {
        console.log('Error extracting username:', error);
    }
    return null;
}

// Simple and reliable username extraction
function extractUsernameSimple(button, modalElement = null) {
    try {
        // Find the user row containing this button - try multiple selectors
        let row = button.closest('li') || 
                  button.closest('div[role="dialog"] li') ||
                  button.closest('div[style*="display: flex"]') ||
                  button.closest('div[style*="display: flex"]') ||
                  button.closest('div');
        
        if (!row) {
            // If no row found, try to find any nearby link
            const modal = modalElement || document.querySelector('div[role="dialog"]');
            const buttonRect = button.getBoundingClientRect();
            const allLinks = Array.from(modal.querySelectorAll('a[href*="/"]'));
            
            for (let link of allLinks) {
                const linkRect = link.getBoundingClientRect();
                const distance = Math.sqrt(
                    Math.pow(linkRect.left - buttonRect.left, 2) + 
                    Math.pow(linkRect.top - buttonRect.top, 2)
                );
                
                if (distance < 100) { // Within 100px
                    const href = link.getAttribute('href');
                    if (href && href.startsWith('/') && !href.includes('/followers') && !href.includes('/following') && !href.includes('/p/') && !href.includes('/reel/')) {
                        const username = href.split('/')[1];
                        if (username && /^[a-z0-9._]{1,30}$/i.test(username)) {
                            return username;
                        }
                    }
                }
            }
            return null;
        }
        
        // Strategy 1: Look for the specific span with username class
        const usernameSpan = row.querySelector('span._ap3a._aaco._aacw._aacx._aad7._aade');
        console.log('Strategy 1 - Found span:', usernameSpan);
        if (usernameSpan) {
            const username = usernameSpan.textContent.trim();
            console.log('Strategy 1 - Username text:', username);
            if (username && /^[a-z0-9._]{1,30}$/i.test(username)) {
                console.log('Strategy 1 - Valid username found:', username);
                return username;
            }
        }
        
        // Strategy 2: Look for any span with the username class pattern
        const spans = row.querySelectorAll('span._ap3a');
        for (let span of spans) {
            const text = span.textContent.trim();
            if (text && /^[a-z0-9._]{1,30}$/i.test(text) && 
                !text.toLowerCase().includes('follow') && 
                !text.toLowerCase().includes('requested')) {
                return text;
            }
        }
        
        // Strategy 3: Look for profile links in the row
        const links = row.querySelectorAll('a[href*="/"]');
        for (let link of links) {
            const href = link.getAttribute('href');
            if (href && href.startsWith('/') && !href.includes('/followers') && !href.includes('/following') && !href.includes('/p/') && !href.includes('/reel/')) {
                const username = href.split('/')[1];
                if (username && /^[a-z0-9._]{1,30}$/i.test(username)) {
                    return username;
                }
            }
        }
        
        // Strategy 4: Look for any text that looks like a username
        const allText = row.textContent || '';
        const words = allText.split(/\s+/);
        
        for (let word of words) {
            const cleanWord = word.trim().replace(/[^\w._]/g, '');
            if (cleanWord && /^[a-z0-9._]{1,30}$/i.test(cleanWord) && 
                !cleanWord.toLowerCase().includes('follow') && 
                !cleanWord.toLowerCase().includes('requested') &&
                cleanWord.length > 1) {
                return cleanWord;
            }
        }
        
        return null;
    } catch (error) {
        return null;
    }
}


// Get button text from the div inside the button
function getButtonText(button) {
    try {
        const buttonDiv = button.querySelector('div._ap3a._aaco._aacw._aad6._aade');
        if (buttonDiv) {
            return buttonDiv.textContent.trim();
        }
        // Fallback to button text if div not found
        return button.textContent.trim();
    } catch (error) {
        console.log('Error getting button text:', error);
        return button.textContent.trim();
    }
}

// Scroll the modal to load more users
function scrollModal(modalElement = null) {
    const modal = modalElement || document.querySelector('div[role="dialog"]');
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

// Sleep function with optional randomization
function sleep(ms, randomize = false, minMultiplier = 0.8, maxMultiplier = 1.5) {
    if (randomize) {
        const multiplier = Math.random() * (maxMultiplier - minMultiplier) + minMultiplier;
        ms = Math.round(ms * multiplier);
    }
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Random delay helper function
function randomDelay(min, max) {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
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
        let detectionAttempts = 0;
        const maxDetectionAttempts = 10; // Increased attempts for better reliability
        
        while (!updatedButton && detectionAttempts < maxDetectionAttempts) {
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
                await sleep(300, true);
                detectionAttempts++;
            }
        }
        
        resolve(updatedButton);
    });
}

// Make the function available globally for testing
window.detectButtonStateChange = detectButtonStateChange; 
window.detectButtonStateChange = detectButtonStateChange; 
window.detectButtonStateChange = detectButtonStateChange; 