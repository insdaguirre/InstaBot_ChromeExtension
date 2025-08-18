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
                await sleep(2000);
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
                await sleep(2000);
                attempts++;
                continue;
            }
            
            // Process visible follow buttons
            for (let button of followButtons) {
                if (followed >= count) break;
                
                try {
                    // Get username (optional)
                    let username = getUsernameFromButton(button, modal);
                    const displayName = username || 'unknown';
                    
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
                    await sleep(500);
                    button.click();
                    
                    // Wait a moment and first check the clicked button itself
                    await sleep(1200);
                    let newText = (getButtonText(button) || '').toLowerCase();
                    
                    // If not changed yet, retry a few times and optionally search nearby
                    if (!(newText.includes('following') || newText.includes('requested'))) {
                        let updatedButton = null;
                        let buttonAttempts = 0;
                        const maxButtonAttempts = 4;
                        while (!updatedButton && buttonAttempts < maxButtonAttempts) {
                            const buttons = (userRow || modal).querySelectorAll('button');
                            for (let btn of buttons) {
                                const t = (getButtonText(btn) || '').toLowerCase();
                                if (t !== originalText && (t.includes('following') || t.includes('requested'))) {
                                    updatedButton = btn; break;
                                }
                            }
                            if (!updatedButton) { await sleep(400); buttonAttempts++; }
                        }
                        if (updatedButton) newText = (getButtonText(updatedButton) || '').toLowerCase();
                    }
                    
                    if (newText.includes('following')) {
                        // Public account - successfully followed
                        followed++;
                        updateStatus(`✅ Followed @${displayName} (public account) (${followed}/${count})`);
                    } else if (newText.includes('requested')) {
                        // Private account - unfollow it
                        updateStatus(`⚠️ @${displayName} is private, unfollowing...`);
                        
                        await sleep(800);
                        // Click again to open confirm, then find Unfollow
                        button.click();
                        await sleep(800);
                        let unfollowBtn = null;
                        const allButtons = document.querySelectorAll('button');
                        for (let btn of allButtons) {
                            const t = (getButtonText(btn) || '').toLowerCase();
                            if (t.includes('unfollow')) { unfollowBtn = btn; break; }
                        }
                        if (!unfollowBtn) {
                            const dialogs = document.querySelectorAll('div[role="dialog"]');
                            for (let d of dialogs) {
                                for (let b of d.querySelectorAll('button')) {
                                    const t = (getButtonText(b) || '').toLowerCase();
                                    if (t.includes('unfollow')) { unfollowBtn = b; break; }
                                }
                                if (unfollowBtn) break;
                            }
                        }
                        if (unfollowBtn) {
                            unfollowBtn.click();
                            await sleep(400);
                            updateStatus(`🔄 Unfollowed @${displayName} (private account)`);
                        } else {
                            updateStatus(`❌ Could not find unfollow confirmation for @${displayName}`);
                        }
                    } else {
                        updateStatus(`❓ Button state unchanged for @${displayName}. Skipping.`);
                    }
                    
                    // Wait between follows
                    await sleep(700);
                } catch (error) {
                    console.log('Error following user:', error);
                }
            }
            
            // Scroll to load more users if needed
            if (followed < count) {
                scrollModal(modal);
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
                await sleep(300);
                detectionAttempts++;
            }
        }
        
        resolve(updatedButton);
    });
}

// Make the function available globally for testing
window.detectButtonStateChange = detectButtonStateChange; 
window.detectButtonStateChange = detectButtonStateChange; 