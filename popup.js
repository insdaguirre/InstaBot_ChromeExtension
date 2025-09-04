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
                }
                startFollowBtn.disabled = false;
            });
        });
    });

    // Load and display batches
    function loadBatches() {
        batchesList.innerHTML = '<div style="text-align: center; color: #666; font-style: italic;">Loading batches...</div>';
        
        // For now, we'll show a message that batches need to be managed through the desktop app
        // In a full implementation, you'd fetch this from a backend or local storage
        batchesList.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="color: #666; font-size: 11px; margin-bottom: 10px;">
                    📋 Batch management is available in the desktop app
                </div>
                <div style="color: #000080; font-size: 10px; font-weight: bold;">
                    Run: python3 instagram_gui.py
                </div>
                <div style="color: #666; font-size: 9px; margin-top: 5px;">
                    The desktop app shows all your timestamped batches with unfollow options
                </div>
            </div>
        `;
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