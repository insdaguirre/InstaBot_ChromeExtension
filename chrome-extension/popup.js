// popup.js - Handles the extension popup interface

document.addEventListener('DOMContentLoaded', function() {
    const followSection = document.getElementById('followSection');
    const unfollowSection = document.getElementById('unfollowSection');
    const currentPageDiv = document.getElementById('currentPage');
    const pageInfoDiv = document.getElementById('pageInfo');
    const statusDiv = document.getElementById('status');
    const startFollowBtn = document.getElementById('startFollow');
    const startUnfollowBtn = document.getElementById('startUnfollow');
    const followCountInput = document.getElementById('followCount');
    const unfollowCountInput = document.getElementById('unfollowCount');

    // Check current page when popup opens
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: 'checkPage'}, function(response) {
            console.log('Popup received page check response:', response);
            if (response) {
                updateUI(response.pageType, response.pageInfo);
            } else {
                console.log('No response from content script');
                updateUI('other', 'Could not detect page type');
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
            pageInfoDiv.textContent = "✅ Ready to follow users from this followers list";
            statusDiv.textContent = "Ready to follow users. Enter number and click START FOLLOWING.";
        } else if (pageType === 'following') {
            // On user's following page - show unfollow option
            followSection.classList.remove('show');
            unfollowSection.classList.add('show');
            pageInfoDiv.textContent = "✅ Ready to unfollow users from your following list";
            statusDiv.textContent = "Ready to unfollow users. Enter number and click START UNFOLLOWING.";
        } else {
            // Not on a relevant page
            followSection.classList.remove('show');
            unfollowSection.classList.remove('show');
            pageInfoDiv.textContent = "❌ Navigate to Instagram followers or following page";
            statusDiv.textContent = "Navigate to:\n• Someone's followers page (to follow)\n• Your following page (to unfollow)";
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

    // Start unfollowing users
    startUnfollowBtn.addEventListener('click', function() {
        const count = parseInt(unfollowCountInput.value);
        if (!count || count < 1 || count > 50) {
            updateStatus("❌ Please enter a number between 1 and 50");
            return;
        }

        startUnfollowBtn.disabled = true;
        updateStatus(`🚀 Starting to unfollow ${count} users...`);

        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'startUnfollowing',
                count: count
            }, function(response) {
                if (response) {
                    updateStatus(response.message);
                }
                startUnfollowBtn.disabled = false;
            });
        });
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