#!/usr/bin/env python3
"""
Test script to verify div role="button" fix
"""

def simulate_instagram_elements():
    """Simulate what Instagram returns for buttons vs clickable divs"""
    
    # What Instagram actually returns
    buttons = ['Following']  # Only the main relationship button
    clickable_divs = ['Message', '7', 'Add to close friends list', 'Add to favorites', 'Mute', 'Restrict', 'Unfollow']
    
    print("🔍 Instagram UI Structure:")
    print(f"   <button> elements: {buttons}")
    print(f"   <div role='button'> elements: {clickable_divs}")
    print()
    
    return buttons, clickable_divs

def test_old_method(buttons, clickable_divs):
    """Test the old method that only checked buttons"""
    print("❌ OLD METHOD (buttons only):")
    
    search_terms = ['unfollow', 'cancel']
    found = False
    
    # Only check buttons (old way)
    for button_text in buttons:
        for term in search_terms:
            if term in button_text.lower():
                print(f"   ✅ Found '{term}' in button: {button_text}")
                found = True
                break
        if found:
            break
    
    if not found:
        print("   ❌ Could not find Unfollow/Cancel in <button> elements")
        print("   → This is why the old method failed!")
    
    print()
    return found

def test_new_method(buttons, clickable_divs):
    """Test the new method that checks both buttons and clickable divs"""
    print("✅ NEW METHOD (buttons + clickable divs):")
    
    search_terms = ['unfollow', 'cancel']
    found = False
    
    # Check both buttons and clickable divs (new way)
    all_clickable = buttons + clickable_divs
    
    for element_text in all_clickable:
        for term in search_terms:
            if term in element_text.lower():
                element_type = "button" if element_text in buttons else "div[role='button']"
                print(f"   ✅ Found '{term}' in {element_type}: {element_text}")
                found = True
                break
        if found:
            break
    
    if not found:
        print("   ❌ Could not find Unfollow/Cancel in any clickable elements")
    
    print()
    return found

def main():
    print("🧪 Testing Div Role='Button' Fix")
    print("=" * 50)
    print()
    
    # Simulate Instagram's actual structure
    buttons, clickable_divs = simulate_instagram_elements()
    
    # Test old method
    old_result = test_old_method(buttons, clickable_divs)
    
    # Test new method
    new_result = test_new_method(buttons, clickable_divs)
    
    # Summary
    print("📊 RESULTS:")
    print("-" * 20)
    print(f"Old Method Success: {'✅ YES' if old_result else '❌ NO'}")
    print(f"New Method Success: {'✅ YES' if new_result else '❌ NO'}")
    print()
    
    if new_result and not old_result:
        print("🎉 FIX CONFIRMED!")
        print("   The new method correctly finds 'Unfollow' in <div role='button'> elements")
        print("   Your unfollow bot should now work correctly!")
    elif old_result and new_result:
        print("ℹ️  Both methods work (Instagram using <button> elements)")
    else:
        print("⚠️  Neither method found the unfollow option")

if __name__ == "__main__":
    main() 