#!/usr/bin/env python3
"""
Speed Test Script - Compare Old vs New Unfollow Methods
"""

import time
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def simulate_old_method():
    """Simulate the old slow method with all its delays"""
    start_time = time.time()
    
    print("🐌 OLD METHOD - Step by step:")
    
    # Navigate to profile
    print("   1. Navigating to profile...")
    time.sleep(2)  # Old method page load wait
    
    # Find relationship button  
    print("   2. Finding relationship button...")
    time.sleep(1)  # Old method button search
    
    # Click relationship button
    print("   3. Clicking Following/Requested button...")
    time.sleep(1.5)  # Old method menu wait
    
    # Search for unfollow button (THE SLOW PART)
    print("   4. 🔍 Looking for Unfollow button (OLD WAY)...")
    print("      - Method 1: XPath exact matches...")
    time.sleep(1.2)  # WebDriverWait + multiple XPath attempts
    print("      - Method 2: Scanning all visible buttons...")
    time.sleep(0.8)  # Button scanning loops
    print("      - Method 3: Menu container searches...")
    time.sleep(1.0)  # Multiple selector attempts
    print("      - Method 4: CSS selector patterns...")
    time.sleep(0.7)  # CSS selector loops
    
    # Click unfollow
    print("   5. Clicking Unfollow button...")
    time.sleep(1)  # Old method click waits
    
    # Confirmation
    print("   6. Handling confirmation...")
    time.sleep(0.5)  # Confirmation wait
    
    # Verification with page refresh
    print("   7. Verifying with page refresh...")
    time.sleep(4)  # Page refresh
    time.sleep(4)  # Wait after refresh
    
    total_time = time.time() - start_time
    print(f"   ⏱️  OLD METHOD TOTAL: {total_time:.1f} seconds")
    return total_time

def simulate_new_method():
    """Simulate the new fast method"""
    start_time = time.time()
    
    print("\n⚡ NEW METHOD - Optimized:")
    
    # Navigate to profile
    print("   1. Navigating to profile...")
    time.sleep(1)  # Reduced page load wait
    
    # Find relationship button
    print("   2. Finding relationship button...")
    time.sleep(0.3)  # Fast button search
    
    # Click relationship button
    print("   3. Clicking Following/Requested button...")
    time.sleep(0.3)  # Minimal menu wait
    
    # Fast search for unfollow button (THE OPTIMIZED PART)
    print("   4. ⚡ Fast search for action button...")
    time.sleep(0.3)  # Single fast scan method
    
    # Fast click
    print("   5. Fast click...")
    time.sleep(0.2)  # Minimal click wait
    
    # Fast confirmation
    print("   6. Fast confirmation check...")
    time.sleep(0.1)  # Quick confirmation
    
    # No page refresh verification
    print("   7. Quick verification (no refresh)...")
    time.sleep(0.1)  # No refresh needed
    
    total_time = time.time() - start_time
    print(f"   ⚡ NEW METHOD TOTAL: {total_time:.1f} seconds")
    return total_time

def main():
    print("🏁 Instagram Unfollow Speed Test")
    print("=" * 50)
    
    # Test old method
    old_time = simulate_old_method()
    
    # Test new method  
    new_time = simulate_new_method()
    
    # Calculate improvement
    improvement = old_time / new_time if new_time > 0 else 0
    time_saved = old_time - new_time
    
    print("\n📊 RESULTS SUMMARY:")
    print("=" * 50)
    print(f"🐌 Old Method:     {old_time:.1f} seconds per account")
    print(f"⚡ New Method:     {new_time:.1f} seconds per account")
    print(f"⏱️  Time Saved:     {time_saved:.1f} seconds per account")
    print(f"🚀 Speed Improvement: {improvement:.1f}x faster")
    print()
    
    # Project savings for different batch sizes
    batch_sizes = [10, 50, 100, 500, 1000]
    print("💰 TIME SAVINGS PROJECTION:")
    print("-" * 50)
    for size in batch_sizes:
        old_total = (old_time * size) / 60  # Convert to minutes
        new_total = (new_time * size) / 60
        saved = old_total - new_total
        
        if saved >= 60:
            saved_hours = saved / 60
            print(f"{size:4d} accounts: Save {saved_hours:.1f} hours ({old_total:.1f}min → {new_total:.1f}min)")
        else:
            print(f"{size:4d} accounts: Save {saved:.1f} minutes ({old_total:.1f}min → {new_total:.1f}min)")

if __name__ == "__main__":
    main() 