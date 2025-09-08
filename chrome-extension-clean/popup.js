// popup.js - Handles the extension popup interface

document.addEventListener('DOMContentLoaded', function() {
    const followSection = document.getElementById('followSection');
    const unfollowSection = document.getElementById('unfollowSection');
    const currentPageDiv = document.getElementById('currentPage');
    const pageInfoDiv = document.getElementById('pageInfo');
    const statusDiv = document.getElementById('status');
    const startFollowBtn = document.getElementById('startFollow');
    const followCountInput = document.getElementById('followCount');
    const batchesList = document.getElementById('batchesList');
    const refreshBatchesBtn = document.getElementById('refreshBatches');
    const unfollowSelectedBtn = document.getElementById('unfollowSelected');

    // Check current page when popup opens
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'checkPage'}, function(response) {
            if (response) {
                updateUI(response.pageType, response.pageInfo);
            }
        });
    });

    // Update UI based on current page
    function updateUI(pageType, pageInfo) {
        currentPageDiv.textContent = pageInfo;
        
        if (pageType === 'followers') {
            // On someone's followers page - show follow option
            followSection.classList.add('show');
            unfollowSection.classList.remove('show');
            pageInfoDiv.textContent = "✅ Ready to follow users from this followers list (private accounts will be skipped)";
            statusDiv.textContent = "Ready to follow users. Enter number and click START FOLLOWING.";
        } else if (pageType === 'following') {
            // On user's following page - show unfollow option
            followSection.classList.remove('show');
            unfollowSection.classList.add('show');
            pageInfoDiv.textContent = "✅ Ready to unfollow users from your following list";
            statusDiv.textContent = "Ready to unfollow users. Select a batch below to unfollow.";
            loadBatches();
        } else {
            // Not on a relevant page
            followSection.classList.remove('show');
            unfollowSection.classList.remove('show');
            pageInfoDiv.textContent = "❌ Navigate to Instagram followers or following page";
            statusDiv.textContent = "Navigate to:\n• Someone's followers page (to follow - private accounts will be skipped)\n• Your following page (to unfollow)";
        }
    }

    // Start following users
    startFollowBtn.addEventListener('click', function() {
        const count = parseInt(followCountInput.value);
        if (!count || count < 1 || count > 50) {
            updateStatus("❌ Please enter a number between 1 and 50");
            return;
        }

        startFollowBtn.disabled = true;
        updateStatus(`🚀 Starting to follow ${count} users...`);

        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'startFollowing',
                count: count
            }, function(response) {
                if (response) {
                    updateStatus(response.message);
                    // Refresh batches list after following
                    setTimeout(() => loadBatches(), 1000);
                }
                startFollowBtn.disabled = false;
            });
        });
    });

    // Load and display batches
    function loadBatches() {
        batchesList.innerHTML = '<div style="text-align: center; color: #666; font-style: italic;">Loading batches...</div>';
        
        // Get batches from Chrome storage via content script
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: 'getBatches'}, function(response) {
                if (response && response.batches) {
                    console.log('Loaded batches in popup:', response.batches.length, 'total batches');
                    displayBatches(response.batches);
                } else {
                    console.log('No batches received from content script');
                    batchesList.innerHTML = `
                        <div style="text-align: center; padding: 20px;">
                            <div style="color: #666; font-size: 11px; margin-bottom: 10px;">
                                📋 No batches found
                            </div>
                            <div style="color: #666; font-size: 10px;">
                                Follow some users to create batches
                            </div>
                        </div>
                    `;
                }
            });
        });
    }

    // Display batches in the UI
    function displayBatches(batches) {
        if (!batches || batches.length === 0) {
            batchesList.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div style="color: #666; font-size: 11px;">
                        📋 No batches found
                    </div>
                    <div style="color: #666; font-size: 9px; margin-top: 5px;">
                        Create batches using the desktop app first
                    </div>
                </div>
            `;
            return;
        }

        // Sort batches by timestamp (newest first)
        const sortedBatches = batches.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        console.log('Displaying all batches:', sortedBatches.length, 'total');
        
        let html = '';
        sortedBatches.forEach((batch, index) => { // Show ALL batches
            const date = new Date(batch.timestamp);
            const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            const totalUsers = batch.users ? batch.users.length : 0;
            const unfollowed = batch.users ? batch.users.filter(u => u.unfollowed).length : 0;
            const usersToUnfollow = totalUsers - unfollowed;
            
            const sources = batch.source_accounts ? batch.source_accounts.join(', ') : 'Unknown';
            
            html += `
                <div style="border: 1px solid #808080; margin: 5px 0; padding: 8px; background: #f9f9f9; font-size: 10px;">
                    <div style="font-weight: bold; color: #000080; margin-bottom: 4px;">
                        ${dateStr}
                    </div>
                    <div style="color: #666; margin-bottom: 4px;">
                        Users: ${totalUsers} • Unfollowed: ${unfollowed}
                    </div>
                    <div style="color: #666; margin-bottom: 6px; font-size: 9px;">
                        Sources: ${sources}
                    </div>
                    ${usersToUnfollow > 0 ? `
                        <div style="margin-top: 6px;">
                            <input type="checkbox" id="batchCheck${index}" value="${index}" style="margin-right: 6px;">
                            <label for="batchCheck${index}" style="font-size: 9px; cursor: pointer;">
                                Select to unfollow ${usersToUnfollow} users
                            </label>
                        </div>
                    ` : `
                        <div style="color: #00aa00; font-size: 9px; font-weight: bold;">
                            ✓ All unfollowed
                        </div>
                    `}
                </div>
            `;
        });

        batchesList.innerHTML = html;
    }

    // Unfollow selected batches
    unfollowSelectedBtn.addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        
        if (checkboxes.length === 0) {
            updateStatus("❌ Please select at least one batch to unfollow");
            return;
        }
        
        updateStatus(`🚀 Starting to unfollow ${checkboxes.length} selected batch(es)...`);
        
        // Process each selected batch
        let processed = 0;
        checkboxes.forEach(checkbox => {
            const batchIndex = parseInt(checkbox.value);
            
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {
                    action: 'unfollowBatch',
                    batchIndex: batchIndex
                }, function(response) {
                    processed++;
                    if (response) {
                        updateStatus(response.message);
                    }
                    
                    // Refresh when all batches are processed
                    if (processed === checkboxes.length) {
                        setTimeout(() => loadBatches(), 1000);
                    }
                });
            });
        });
    });

    // Refresh batches
    refreshBatchesBtn.addEventListener('click', function() {
        loadBatches();
        updateStatus("🔄 Refreshed batch list");
    });

    // Update status display
    function updateStatus(message) {
        const timestamp = new Date().toLocaleTimeString();
        statusDiv.textContent = `[${timestamp}] ${message}`;
        statusDiv.scrollTop = statusDiv.scrollHeight;
    }

    // Listen for progress updates from content script
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'updateStatus') {
            updateStatus(request.message);
        }
    });
}); 