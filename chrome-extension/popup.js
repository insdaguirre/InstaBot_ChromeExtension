// popup.js - Handles the extension popup interface

document.addEventListener('DOMContentLoaded', function() {
    const followSection = document.getElementById('followSection');
    const unfollowSection = document.getElementById('unfollowSection');
    const currentPageDiv = document.getElementById('currentPage');
    const pageInfoDiv = document.getElementById('pageInfo');
    const statusDiv = document.getElementById('status');
    const startFollowBtn = document.getElementById('startFollow');
    const startUnfollowBtn = document.getElementById('startUnfollow');
    // Add Delete button if not present (uses same section styling)
    let deleteBtn = document.getElementById('deleteBatch');
    if (!deleteBtn) {
        deleteBtn = document.createElement('button');
        deleteBtn.id = 'deleteBatch';
        deleteBtn.textContent = 'DELETE SELECTED BATCH';
        const unfollowSectionEl = document.getElementById('unfollowSection');
        if (unfollowSectionEl) {
            const sectionInner = unfollowSectionEl.querySelector('.section');
            if (sectionInner) {
                sectionInner.appendChild(document.createElement('br'));
                sectionInner.appendChild(document.createElement('br'));
                sectionInner.appendChild(deleteBtn);
            }
        }
    }
    const followCountInput = document.getElementById('followCount');
    const batchesListDiv = document.getElementById('batchesList');
    const batchSelect = document.getElementById('batchSelect');

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
        
        // Get followed batches
        chrome.tabs.sendMessage(tabs[0].id, {action: 'getFollowedBatches'}, function(response) {
            if (response) {
                updateBatchesList(response.batches);
            }
        });
    });

    // Update batches list display
    function updateBatchesList(batches) {
        if (batchesListDiv) {
            if (batches && batches.length > 0) {
                let totalUsers = 0;
                let emptyBatches = 0;
                batches.forEach(batch => {
                    totalUsers += batch.count;
                    if (batch.usernames && batch.usernames.length === 0) {
                        emptyBatches++;
                    }
                });
                
                let statusText = `📋 ${batches.length} batches, ${totalUsers} total users`;
                if (emptyBatches > 0) {
                    statusText += ` (${emptyBatches} empty)`;
                }
                batchesListDiv.textContent = statusText;
            } else {
                batchesListDiv.innerHTML = `
                    <div style="text-align: center; padding: 8px;">
                        <div style="color: #666; font-size: 11px;">📋 No batches found</div>
                        <div style="color: #666; font-size: 9px; margin-top: 4px;">Create a batch by using Follow on a followers list (in this extension)</div>
                    </div>
                `;
            }
        }
        
        // Update batch select dropdown
        if (batchSelect) {
            batchSelect.innerHTML = '';
            if (batches && batches.length > 0) {
                batches.forEach((batch, index) => {
                    const date = new Date(batch.timestamp);
                    const timeStr = date.toLocaleString();
                    const option = document.createElement('option');
                    option.value = index;
                    
                    // Show if batch is empty
                    const isEmpty = batch.usernames && batch.usernames.length === 0;
                    const status = isEmpty ? ' (EMPTY)' : '';
                    
                    option.textContent = `Batch ${index + 1}: ${batch.count} users${status} (${timeStr})`;
                    batchSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No batches available';
                batchSelect.appendChild(option);
            }
        }
    }

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
            statusDiv.textContent = "Ready to unfollow users. Enter number and click START UNFOLLOWING.";
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
                    // Update batches list after following
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'getFollowedBatches'}, function(batchesResponse) {
                        if (batchesResponse) {
                            updateBatchesList(batchesResponse.batches);
                        }
                    });
                }
                startFollowBtn.disabled = false;
            });
        });
    });

    // Start unfollowing users
    startUnfollowBtn.addEventListener('click', function() {
        const batchIndex = parseInt(batchSelect.value);
        
        if (batchIndex === undefined || batchIndex < 0) {
            updateStatus("❌ Please select a batch to unfollow from");
            return;
        }

        startUnfollowBtn.disabled = true;
        updateStatus(`🚀 Starting to unfollow entire batch ${batchIndex + 1}...`);

        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'unfollowBatch',
                batchIndex: batchIndex,
                count: -1 // -1 indicates unfollow entire batch
            }, function(response) {
                if (response) {
                    updateStatus(response.message);
                    // Update batches list after unfollowing
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'getFollowedBatches'}, function(batchesResponse) {
                        if (batchesResponse) {
                            updateBatchesList(batchesResponse.batches);
                        }
                    });
                }
                startUnfollowBtn.disabled = false;
            });
        });
    });

    // Delete selected batch manually
    deleteBtn.addEventListener('click', function() {
        const batchIndex = parseInt(batchSelect.value);
        if (isNaN(batchIndex) || batchIndex < 0) {
            updateStatus("❌ Please select a batch to delete");
            return;
        }
        if (!confirm('Delete the selected batch? This cannot be undone.')) {
            return;
        }
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: 'deleteBatch',
                batchIndex: batchIndex
            }, function(response) {
                if (response) {
                    updateStatus(response.message);
                    // Refresh batches after deletion
                    chrome.tabs.sendMessage(tabs[0].id, {action: 'getFollowedBatches'}, function(batchesResponse) {
                        if (batchesResponse) {
                            updateBatchesList(batchesResponse.batches);
                        }
                    });
                }
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