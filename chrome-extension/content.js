// content.js - Runs on Instagram pages and performs automation

let isRunning = false;
let followedBatches = []; // Store batches of followed users with timestamps

// Load followed batches from storage
chrome.storage.local.get(['followedBatches'], function(result) {
    if (result.followedBatches) {
        followedBatches = result.followedBatches;
        console.log('📋 Loaded', followedBatches.length, 'followed batches from storage');
    }
});

// Save followed batches to storage
function saveFollowedBatches() {
    chrome.storage.local.set({followedBatches: followedBatches}, function() {
        console.log('💾 Saved', followedBatches.length, 'followed batches to storage');
    });
}

// Get all usernames from all batches
function getAllFollowedUsernames() {
    let allUsernames = [];
    followedBatches.forEach(batch => {
        allUsernames = allUsernames.concat(batch.usernames);
    });
    return allUsernames;
}

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
    } else if (request.action === 'getFollowedBatches') {
        sendResponse({batches: followedBatches});
    } else if (request.action === 'clearFollowedBatches') {
        followedBatches = [];
        saveFollowedBatches();
        sendResponse({message: "🗑️ Cleared all followed batches"});
    } else if (request.action === 'unfollowBatch') {
        if (!isRunning) {
            startUnfollowingBatch(request.batchIndex, request.count).then(result => {
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
    
    // ENHANCED URL-BASED DETECTION
    console.log('🔍 Checking URL patterns...');
    console.log('URL includes /followers/:', url.includes('/followers/'));
    console.log('URL includes /following/:', url.includes('/following/'));
    
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
    
    // FALLBACK: Check for modal dialog and its content
    console.log('🔍 Checking for modal dialog...');
    const modal = document.querySelector('div[role="dialog"]');
    if (modal) {
        console.log('✅ Found modal dialog');
        const modalText = modal.textContent.toLowerCase();
        console.log('Modal text contains "followers":', modalText.includes('followers'));
        console.log('Modal text contains "following":', modalText.includes('following'));
        
        if (modalText.includes('followers')) {
            const username = extractUsernameFromPage();
            console.log('✅ DETECTED: Followers page via modal for @', username);
            return {
                pageType: 'followers',
                pageInfo: `Followers of @${username}`
            };
        }
        
        if (modalText.includes('following')) {
            const username = extractUsernameFromPage();
            console.log('✅ DETECTED: Following page via modal for @', username);
            return {
                pageType: 'following',
                pageInfo: `Following of @${username}`
            };
        }
    }
    
    // FALLBACK: Check for follow buttons (if URL doesn't work)
    console.log('🔍 Checking for follow buttons...');
    const followButtons = findFollowButtons();
    const followingButtons = findFollowingButtons();
    
    console.log('🔍 Found follow buttons:', followButtons.length);
    console.log('🔍 Found following buttons:', followingButtons.length);
    
    // If we found buttons, we're definitely on the right page
    if (followButtons.length > 0) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Followers page via buttons for @', username);
        console.log('✅ Button detection successful - found', followButtons.length, 'follow buttons');
        return {
            pageType: 'followers',
            pageInfo: `Followers of @${username}`
        };
    }
    
    if (followingButtons.length > 0) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Following page via buttons for @', username);
        console.log('✅ Button detection successful - found', followingButtons.length, 'following buttons');
        return {
            pageType: 'following',
            pageInfo: `Following of @${username}`
        };
    }
    
    // FINAL FALLBACK: Check page title
    console.log('🔍 Checking page title...');
    const pageTitle = document.title.toLowerCase();
    console.log('Page title:', pageTitle);
    
    if (pageTitle.includes('followers')) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Followers page via title for @', username);
        return {
            pageType: 'followers',
            pageInfo: `Followers of @${username}`
        };
    }
    
    if (pageTitle.includes('following')) {
        const username = extractUsernameFromPage();
        console.log('✅ DETECTED: Following page via title for @', username);
        return {
            pageType: 'following',
            pageInfo: `Following of @${username}`
        };
    }
    
    // ULTIMATE FALLBACK: Check for any button with "Follow" text anywhere
    console.log('🔍 ULTIMATE FALLBACK: Checking all buttons on page...');
    const allButtons = document.querySelectorAll('button');
    console.log('Total buttons on page:', allButtons.length);
    
    for (let i = 0; i < Math.min(allButtons.length, 10); i++) {
        const button = allButtons[i];
        const buttonText = button.textContent.toLowerCase().trim();
        console.log(`Button ${i + 1} text: "${buttonText}"`);
        
        if (buttonText === 'follow') {
            const username = extractUsernameFromPage();
            console.log('✅ DETECTED: Followers page via ultimate fallback for @', username);
            return {
                pageType: 'followers',
                pageInfo: `Followers of @${username}`
            };
        }
    }
    
    console.log('❌ Could not detect page type');
    console.log('URL was:', url);
    console.log('Page title was:', document.title);
    console.log('Total buttons found:', allButtons.length);
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
    console.log('🔍 Looking for follow buttons...');
    
    // Method 1: Look for buttons with "Follow" text
    const buttons = document.querySelectorAll('button');
    const followButtons = Array.from(buttons).filter(button => {
        const buttonText = button.textContent.toLowerCase().trim();
        console.log('🔍 Button text:', buttonText);
        
        // Check for "Follow" (not "Following" or "Requested")
        return buttonText === 'follow' || 
               buttonText.includes('follow') && 
               !buttonText.includes('following') && 
               !buttonText.includes('requested');
    });
    
    console.log('✅ Found follow buttons:', followButtons.length);
    
    // Method 2: Look for buttons with specific Instagram structure
    if (followButtons.length === 0) {
        console.log('🔍 Trying alternative button detection...');
        const allButtons = document.querySelectorAll('button');
        const alternativeButtons = Array.from(allButtons).filter(button => {
            // Look for buttons with div containing "Follow"
            const divs = button.querySelectorAll('div');
            for (let div of divs) {
                const divText = div.textContent.toLowerCase().trim();
                if (divText === 'follow') {
                    console.log('✅ Found follow button via div structure');
                    return true;
                }
            }
            return false;
        });
        
        if (alternativeButtons.length > 0) {
            console.log('✅ Found follow buttons via alternative method:', alternativeButtons.length);
            return alternativeButtons;
        }
    }
    
    return followButtons;
}

// Find following buttons with compatible selector
function findFollowingButtons() {
    console.log('🔍 Looking for following buttons...');
    
    // Method 1: Look for buttons with "Following" text
    const buttons = document.querySelectorAll('button');
    const followingButtons = Array.from(buttons).filter(button => {
        const buttonText = button.textContent.toLowerCase().trim();
        console.log('🔍 Button text:', buttonText);
        
        // Check for "Following"
        return buttonText === 'following' || 
               buttonText.includes('following');
    });
    
    console.log('✅ Found following buttons:', followingButtons.length);
    
    // Method 2: Look for buttons with specific Instagram structure
    if (followingButtons.length === 0) {
        console.log('🔍 Trying alternative following button detection...');
        const allButtons = document.querySelectorAll('button');
        const alternativeButtons = Array.from(allButtons).filter(button => {
            // Look for buttons with div containing "Following"
            const divs = button.querySelectorAll('div');
            for (let div of divs) {
                const divText = div.textContent.toLowerCase().trim();
                if (divText === 'following') {
                    console.log('✅ Found following button via div structure');
                    return true;
                }
            }
            return false;
        });
        
        if (alternativeButtons.length > 0) {
            console.log('✅ Found following buttons via alternative method:', alternativeButtons.length);
            return alternativeButtons;
        }
    }
    
    return followingButtons;
}

// Start following users
async function startFollowing(count) {
    isRunning = true;
    let followed = 0;
    let currentBatchUsernames = []; // Store usernames for this batch
    
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
                        
                        // Add to current batch
                        if (!currentBatchUsernames.includes(username)) {
                            currentBatchUsernames.push(username);
                            console.log('📋 Added', username, 'to current batch');
                        }
                        
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
        
        // Save the batch if we followed any users
        if (currentBatchUsernames.length > 0) {
            const batch = {
                timestamp: new Date().toISOString(),
                count: currentBatchUsernames.length,
                usernames: currentBatchUsernames
            };
            followedBatches.push(batch);
            saveFollowedBatches();
            updateStatus(`📦 Saved batch with ${currentBatchUsernames.length} users`);
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

// Start unfollowing users from a specific batch using search within following list
async function startUnfollowingBatch(batchIndex, count) {
    isRunning = true;
    let unfollowed = 0;
    
    // Validate batch index
    if (batchIndex < 0 || batchIndex >= followedBatches.length) {
        updateStatus(`❌ Invalid batch index: ${batchIndex}`);
        return {message: `❌ Invalid batch index: ${batchIndex}`};
    }
    
    const batch = followedBatches[batchIndex];
    const batchUsernames = [...batch.usernames]; // Create a copy to work with
    
    updateStatus(`🎯 Starting search-based unfollow for batch ${batchIndex + 1}...`);
    updateStatus(`📋 Found ${batchUsernames.length} users in batch ${batchIndex + 1}`);
    
    try {
        // Wait for modal to be ready
        await waitForElement('div[role="dialog"]', 5000);
        
        // Process each username in the batch
        for (let i = 0; i < Math.min(count, batchUsernames.length); i++) {
            const username = batchUsernames[i];
            
            if (!username) continue;
            
            updateStatus(`🔍 Searching for @${username} (${unfollowed + 1}/${count})`);
            
            // Find and use the search input
            const searchInput = findSearchInput();
            if (!searchInput) {
                updateStatus(`❌ Could not find search input`);
                continue;
            }
            
            // Clear search input and type username
            searchInput.value = username;
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Random delay after searching (1-2.5 seconds)
            const searchDelay = getRandomDelay() + 0.5; // Add 0.5s to make it 1-2.5s
            updateStatus(`⏳ Waiting ${searchDelay.toFixed(1)}s after searching for @${username}...`);
            await sleep(searchDelay * 1000);
            
            // Look for the user in search results
            const userResult = findUserInSearchResults(username);
            if (userResult) {
                updateStatus(`⏳ Unfollowing @${username} (${unfollowed + 1}/${count})`);
                
                // Random delay before clicking follow button
                const clickDelay = getRandomDelay();
                updateStatus(`⏳ Waiting ${clickDelay.toFixed(1)}s before unfollowing @${username}...`);
                await sleep(clickDelay * 1000);
                
                // Click the following button
                userResult.scrollIntoView({ behavior: 'smooth', block: 'center' });
                await sleep(500);
                userResult.click();
                
                // Wait for and click unfollow confirmation
                await sleep(1000);
                const unfollowBtn = findUnfollowButton();
                if (unfollowBtn) {
                    unfollowBtn.click();
                    unfollowed++;
                    
                    // Remove from batch
                    const index = batch.usernames.indexOf(username);
                    if (index > -1) {
                        batch.usernames.splice(index, 1);
                        saveFollowedBatches();
                        console.log('📋 Removed', username, 'from batch', batchIndex + 1);
                    }
                    
                    updateStatus(`✅ Unfollowed @${username} (${unfollowed}/${count})`);
                    
                    // Random delay between unfollows
                    const nextDelay = getRandomDelay();
                    updateStatus(`⏳ Waiting ${nextDelay.toFixed(1)}s before next user...`);
                    await sleep(nextDelay * 1000);
                } else {
                    updateStatus(`⚠️ Could not find unfollow confirmation for @${username}`);
                }
            } else {
                updateStatus(`⚠️ Could not find @${username} in search results`);
            }
            
            // Clear search for next iteration
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            await sleep(1000);
        }
        
        // Remove empty batch
        if (batch.usernames.length === 0) {
            followedBatches.splice(batchIndex, 1);
            saveFollowedBatches();
            updateStatus(`🗑️ Removed empty batch ${batchIndex + 1}`);
        }
        
        const message = unfollowed === count 
            ? `🎉 Successfully unfollowed ${unfollowed} users from batch ${batchIndex + 1}!`
            : `⚠️ Unfollowed ${unfollowed}/${count} users from batch ${batchIndex + 1} (no more available)`;
            
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

// Find search input in the following modal
function findSearchInput() {
    console.log('🔍 Looking for search input...');
    
    // Method 1: Look for input with the specific class from the HTML you provided
    const searchInputs = document.querySelectorAll('input[aria-label="Search input"]');
    if (searchInputs.length > 0) {
        console.log('✅ Found search input via aria-label');
        return searchInputs[0];
    }
    
    // Method 2: Look for input with placeholder "Search"
    const placeholderInputs = document.querySelectorAll('input[placeholder="Search"]');
    if (placeholderInputs.length > 0) {
        console.log('✅ Found search input via placeholder');
        return placeholderInputs[0];
    }
    
    // Method 3: Look for input with specific class pattern
    const classInputs = document.querySelectorAll('input.x1lugfcp');
    if (classInputs.length > 0) {
        console.log('✅ Found search input via class');
        return classInputs[0];
    }
    
    console.log('❌ Could not find search input');
    return null;
}

// Find user in search results
function findUserInSearchResults(targetUsername) {
    console.log(`🔍 Looking for @${targetUsername} in search results...`);
    
    // Method 1: Look for buttons with "Following" text near the username
    const buttons = document.querySelectorAll('button');
    const followingButtons = Array.from(buttons).filter(button => {
        const buttonText = button.textContent.toLowerCase().trim();
        return buttonText === 'following' || buttonText.includes('following');
    });
    
    // Check each following button to see if it's near the target username
    for (let button of followingButtons) {
        // Look for username in the same container or nearby
        const container = button.closest('div[role="dialog"] div');
        if (container) {
            const links = container.querySelectorAll('a[href*="/"]');
            for (let link of links) {
                const href = link.href;
                const match = href.match(/instagram\.com\/([^\/\?]+)/);
                if (match && match[1] === targetUsername) {
                    console.log(`✅ Found @${targetUsername} in search results`);
                    return button;
                }
            }
        }
    }
    
    // Method 2: Look for username in any link and find nearby following button
    const allLinks = document.querySelectorAll('a[href*="/"]');
    for (let link of allLinks) {
        const href = link.href;
        const match = href.match(/instagram\.com\/([^\/\?]+)/);
        if (match && match[1] === targetUsername) {
            // Find the following button near this link
            const container = link.closest('div');
            if (container) {
                const nearbyButton = container.querySelector('button');
                if (nearbyButton) {
                    const buttonText = nearbyButton.textContent.toLowerCase().trim();
                    if (buttonText === 'following' || buttonText.includes('following')) {
                        console.log(`✅ Found @${targetUsername} in search results via link`);
                        return nearbyButton;
                    }
                }
            }
        }
    }
    
    console.log(`❌ Could not find @${targetUsername} in search results`);
    return null;
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

// Test function for comprehensive page detection debugging
function testPageDetection() {
    console.log('🧪 === COMPREHENSIVE PAGE DETECTION TEST ===');
    
    const url = window.location.href;
    console.log('1. URL Analysis:');
    console.log('   URL:', url);
    console.log('   Includes instagram.com:', url.includes('instagram.com'));
    console.log('   Includes /followers/:', url.includes('/followers/'));
    console.log('   Includes /following/:', url.includes('/following/'));
    
    console.log('\n2. Page Title Analysis:');
    console.log('   Title:', document.title);
    console.log('   Title includes "followers":', document.title.toLowerCase().includes('followers'));
    console.log('   Title includes "following":', document.title.toLowerCase().includes('following'));
    
    console.log('\n3. Modal Dialog Analysis:');
    const modal = document.querySelector('div[role="dialog"]');
    console.log('   Modal found:', !!modal);
    if (modal) {
        console.log('   Modal text (first 200 chars):', modal.textContent.substring(0, 200));
        console.log('   Modal contains "followers":', modal.textContent.toLowerCase().includes('followers'));
        console.log('   Modal contains "following":', modal.textContent.toLowerCase().includes('following'));
    }
    
    console.log('\n4. Button Analysis:');
    const followButtons = findFollowButtons();
    const followingButtons = findFollowingButtons();
    console.log('   Follow buttons found:', followButtons.length);
    console.log('   Following buttons found:', followingButtons.length);
    
    if (followButtons.length > 0) {
        console.log('   First follow button text:', followButtons[0].textContent);
    }
    if (followingButtons.length > 0) {
        console.log('   First following button text:', followingButtons[0].textContent);
    }
    
    console.log('\n5. Username Extraction:');
    const urlUsername = extractUsernameFromUrl(url);
    const pageUsername = extractUsernameFromPage();
    console.log('   Username from URL:', urlUsername);
    console.log('   Username from page:', pageUsername);
    
    console.log('\n6. Final Page Detection Result:');
    const result = checkCurrentPage();
    console.log('   Result:', result);
    
    console.log('🧪 === END TEST ===');
    return result;
}

// Make test function available globally
window.testPageDetection = testPageDetection; 