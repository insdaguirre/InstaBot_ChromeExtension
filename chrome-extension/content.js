// content.js - Runs on Instagram pages and performs automation

let isRunning = false;
let followedBatches = []; // Store batches of followed users with timestamps

// Add randomization helper functions at the top
function randomDelay(min, max) {
    const delay = Math.random() * (max - min) + min;
    return new Promise(resolve => setTimeout(resolve, delay));
}

// Enhanced sleep function with randomization
function sleep(ms, randomize = false, minMultiplier = 0.8, maxMultiplier = 1.5) {
    if (randomize) {
        const multiplier = Math.random() * (maxMultiplier - minMultiplier) + minMultiplier;
        ms = Math.round(ms * multiplier);
    }
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Load followed batches from storage
chrome.storage.local.get(['followedBatches'], function(result) {
    if (result.followedBatches) {
        followedBatches = result.followedBatches;
        console.log('📋 Loaded', followedBatches.length, 'followed batches from storage');
    }
});

// Save followed batches to storage
function saveFollowedBatches() {
    // Clean up empty batches before saving
    followedBatches = followedBatches.filter(batch => batch.usernames.length > 0);
    
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
    
    console.log('❌ Could not detect page type');
    return {
        pageType: 'other',
        pageInfo: 'Not on followers/following page'
    };
}

// Extract username from Instagram URL
function extractUsernameFromUrl(url) {
    const match = url.match(/instagram\.com\/([^\/]+)\/(followers|following)/);
    return match ? match[1] : 'unknown';
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

// Helper function to check if profile page has followers/following buttons
function checkProfilePageButtons() {
    const buttons = document.querySelectorAll('button');
    let hasFollowers = false;
    let hasFollowing = false;
    
    buttons.forEach(button => {
        const text = button.textContent.trim().toLowerCase();
        if (text.includes('followers')) {
            hasFollowers = true;
        }
        if (text.includes('following')) {
            hasFollowing = true;
        }
    });
    
    return { hasFollowers, hasFollowing };
}

// Make the function available globally for testing
window.checkProfilePageButtons = checkProfilePageButtons;

// Start following users
async function startFollowing(count) {
    isRunning = true;
    let followed = 0;
    let privateAccountsUnfollowed = 0;
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
                await sleep(2000, true);
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
                        
                        // Random delay before clicking
                        const delay = getRandomDelay();
                        updateStatus(`⏳ Waiting ${delay.toFixed(1)}s before following @${username}...`);
                        await sleep(delay * 1000);
                        
                        // Click follow button
                        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await sleep(500, true);
                        button.click();
                        
                        // Wait longer for Instagram's UI to update and stabilize
                        await sleep(2000, true);
                        
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
                                await sleep(500, true);
                                attempts++;
                            }
                        }
                        
                        if (!updatedButton) {
                            updateStatus(`❓ Could not detect button state change for @${username}, skipping...`);
                            continue;
                        }
                        
                        const newText = updatedButton.textContent.trim();
                        
                        console.log(`Button state change for @${username}: "${originalText}" -> "${newText}"`);
                        
                        if (newText.toLowerCase().includes("following")) {
                            // Public account - successfully followed
                        followed++;
                        
                            // Add to current batch only if successfully followed
                            if (!currentBatchUsernames.includes(username)) {
                                currentBatchUsernames.push(username);
                                console.log('📋 Added', username, 'to current batch (public account)');
                            }
                            
                            updateStatus(`✅ Followed @${username} (public account) (${followed}/${count})`);
                            
                            // Add random delay between users for more human-like behavior
                            const userDelay = getRandomDelay();
                            await sleep(userDelay * 1000);
                        } else if (newText.toLowerCase().includes("requested")) {
                            // Private account - unfollow it
                            updateStatus(`⚠️ @${username} is private, unfollowing...`);
                            
                            // Wait for the button to fully stabilize
                            await sleep(1500, true);
                            
                            // Click the button again to unfollow
                            updatedButton.click();
                            await sleep(1500, true);
                            
                            // Look for unfollow confirmation button with multiple methods
                            let unfollowBtn = null;
                            
                            // Method 1: Look for button with "Unfollow" text
                            unfollowBtn = findUnfollowButton();
                            
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
            updateStatus(`📦 Saved batch with ${currentBatchUsernames.length} public users`);
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
        const maxUsers = count === -1 ? batchUsernames.length : Math.min(count, batchUsernames.length);
        for (let i = 0; i < maxUsers; i++) {
            const username = batchUsernames[i];
            
            if (!username) continue;
            
            updateStatus(`🔍 Searching for @${username} (${unfollowed + 1}/${maxUsers})`);
            
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
            
            // Wait for search results to load
            updateStatus(`⏳ Waiting for search results to load...`);
            await sleep(2000); // Additional wait for search results
            
            // Look for the user in search results
            const userResult = findUserInSearchResults(username);
            if (userResult) {
                updateStatus(`⏳ Found @${username} in search results`);
                
                // Random delay between search and clicking follow button (1-2 seconds)
                const searchToClickDelay = Math.random() * (2 - 1) + 1;
                updateStatus(`⏳ Waiting ${searchToClickDelay.toFixed(1)}s between search and unfollow...`);
                await sleep(searchToClickDelay * 1000);
                
                updateStatus(`⏳ Unfollowing @${username} (${unfollowed + 1}/${maxUsers})`);
                
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
                        console.log('📋 Removed', username, 'from batch', batchIndex + 1);
                        updateStatus(`✅ Unfollowed @${username} (${unfollowed}/${maxUsers})`);
                        
                        // Check if batch is now empty and remove it
                        if (batch.usernames.length === 0) {
                            followedBatches.splice(batchIndex, 1);
                            saveFollowedBatches();
                            updateStatus(`🗑️ Auto-deleted empty batch ${batchIndex + 1}`);
                            console.log('🗑️ Auto-deleted empty batch', batchIndex + 1);
                            // Break out of the loop since the batch no longer exists
                            break;
                        } else {
                            // Save the updated batch
                            saveFollowedBatches();
                        }
                    }
                    
                    // Random delay between unfollows
                    const nextDelay = getRandomDelay();
                    updateStatus(`⏳ Waiting ${nextDelay.toFixed(1)}s before next user...`);
                    await sleep(nextDelay * 1000);
                } else {
                    updateStatus(`⚠️ Could not find unfollow confirmation for @${username}`);
                    // Remove from batch even if unfollow failed
                    const index = batch.usernames.indexOf(username);
                    if (index > -1) {
                        batch.usernames.splice(index, 1);
                        console.log('📋 Removed', username, 'from batch', batchIndex + 1, '(unfollow failed)');
                        saveFollowedBatches();
                        
                        // Check if batch is now empty and remove it
                        if (batch.usernames.length === 0) {
                            followedBatches.splice(batchIndex, 1);
                            saveFollowedBatches();
                            updateStatus(`🗑️ Auto-deleted empty batch ${batchIndex + 1}`);
                            console.log('🗑️ Auto-deleted empty batch', batchIndex + 1);
                            // Break out of the loop since the batch no longer exists
                            break;
                        }
                    }
                }
            } else {
                updateStatus(`⚠️ Could not find @${username} in search results`);
                // Remove from batch even if user not found
                const index = batch.usernames.indexOf(username);
                if (index > -1) {
                    batch.usernames.splice(index, 1);
                    console.log('📋 Removed', username, 'from batch', batchIndex + 1, '(user not found)');
                    saveFollowedBatches();
                    
                    // Check if batch is now empty and remove it
                    if (batch.usernames.length === 0) {
                        followedBatches.splice(batchIndex, 1);
                        saveFollowedBatches();
                        updateStatus(`🗑️ Auto-deleted empty batch ${batchIndex + 1}`);
                        console.log('🗑️ Auto-deleted empty batch', batchIndex + 1);
                        // Break out of the loop since the batch no longer exists
                        break;
                    }
                }
            }
            
            // Clear search for next iteration
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            await sleep(1000);
        }
        

        
        // Handle the case where count is -1 (unfollow entire batch)
        const targetCount = count === -1 ? batchUsernames.length : count;
        const message = unfollowed === targetCount 
            ? `🎉 Successfully unfollowed ${unfollowed} users from batch ${batchIndex + 1}!`
            : `⚠️ Unfollowed ${unfollowed}/${targetCount} users from batch ${batchIndex + 1} (no more available)`;
            
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
    
    // Debug: Log all buttons and their text
    const allButtons = document.querySelectorAll('button');
    console.log(`🔍 Found ${allButtons.length} total buttons on page`);
    allButtons.forEach((button, index) => {
        console.log(`Button ${index}: "${button.textContent.trim()}"`);
    });
    
    // Method 1: Look for buttons with "Following" text near the username
    const followingButtons = Array.from(allButtons).filter(button => {
        const buttonText = button.textContent.toLowerCase().trim();
        console.log(`🔍 Checking button: "${buttonText}"`);
        return buttonText === 'following' || buttonText.includes('following');
    });
    
    console.log(`🔍 Found ${followingButtons.length} following buttons`);
    
    // Check each following button to see if it's near the target username
    for (let button of followingButtons) {
        console.log(`🔍 Checking following button: "${button.textContent.trim()}"`);
        
        // Method 1A: Look for username in the same container
        const container = button.closest('div[role="dialog"] div');
        if (container) {
            const links = container.querySelectorAll('a[href*="/"]');
            console.log(`🔍 Found ${links.length} links in container`);
            for (let link of links) {
                const href = link.href;
                const match = href.match(/instagram\.com\/([^\/\?]+)/);
                if (match && match[1] === targetUsername) {
                    console.log(`✅ Found @${targetUsername} in search results via container`);
                    return button;
                }
            }
        }
        
        // Method 1B: Look for username in parent containers
        let parent = button.parentElement;
        for (let i = 0; i < 5; i++) {
            if (!parent) break;
            const links = parent.querySelectorAll('a[href*="/"]');
            for (let link of links) {
                const href = link.href;
                const match = href.match(/instagram\.com\/([^\/\?]+)/);
                if (match && match[1] === targetUsername) {
                    console.log(`✅ Found @${targetUsername} in search results via parent ${i}`);
                    return button;
                }
            }
            parent = parent.parentElement;
        }
    }
    
    // Method 2: Look for username in any link and find nearby following button
    const allLinks = document.querySelectorAll('a[href*="/"]');
    console.log(`🔍 Found ${allLinks.length} total links on page`);
    for (let link of allLinks) {
        const href = link.href;
        const match = href.match(/instagram\.com\/([^\/\?]+)/);
        if (match && match[1] === targetUsername) {
            console.log(`