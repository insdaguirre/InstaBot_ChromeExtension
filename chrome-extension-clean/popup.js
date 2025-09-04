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
                    displayBatches(response.batches);
                } else {
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
        
        let html = '';
        sortedBatches.slice(0, 5).forEach((batch, index) => { // Show only first 5 batches
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
                        <button id="unfollowBtn${index}" style="
                            background: #f0f0f0; 
                            border: 1px solid #808080; 
                            padding: 4px 8px; 
                            font-size: 9px; 
                            cursor: pointer;
                            color: black;
                        ">
                            Unfollow (${usersToUnfollow})
                        </button>
                    ` : `
                        <div style="color: #00aa00; font-size: 9px; font-weight: bold;">
                            ✓ All unfollowed
                        </div>
                    `}
                </div>
            `;
        });

        if (sortedBatches.length > 5) {
            html += `
                <div style="text-align: center; color: #666; font-size: 9px; margin-top: 8px;">
                    ... and ${sortedBatches.length - 5} more batches
                </div>
            `;
        }

        batchesList.innerHTML = html;
        
        // Add simple click handlers like the working buttons
        for (let i = 0; i < sortedBatches.slice(0, 5).length; i++) {
            const unfollowBtn = document.getElementById(`unfollowBtn${i}`);
            if (unfollowBtn) {
                unfollowBtn.addEventListener('click', function() {
                    updateStatus(`🚀 Starting unfollow for batch ${i + 1}...`);
                    
                    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                        chrome.tabs.sendMessage(tabs[0].id, {
                            action: 'unfollowBatch',
                            batchIndex: i
                        }, function(response) {
                            if (response) {
                                updateStatus(response.message);
                                setTimeout(() => loadBatches(), 1000);
                            }
                        });
                    });
                });
            }
        }
    }

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