#!/bin/bash
# Fix and Reinstall Instagram Bot
set -e

echo "🔧 Instagram Bot - Fix and Reinstall Script"
echo "=========================================="
echo ""

# Remove broken version from Applications
echo "🗑️ Removing broken version from Applications..."
if [ -d "/Applications/Instagram Bot.app" ]; then
    sudo rm -rf "/Applications/Instagram Bot.app"
    echo "✅ Removed broken version from Applications"
else
    echo "ℹ️ No existing version found in Applications"
fi

# Remove broken version from current directory
echo "🗑️ Removing broken version from current directory..."
if [ -d "Instagram Bot.app" ]; then
    rm -rf "Instagram Bot.app"
    echo "✅ Removed broken version from current directory"
fi

echo ""
echo "🛠️ Creating fixed app bundle..."

# Create the fixed app bundle using Python
python3 -c "
import sys
import os
from pathlib import Path

# Ensure we're in the right directory
os.chdir('$(pwd)')
sys.path.insert(0, '$(pwd)')

print('🚀 Building fixed Instagram Bot app...')

try:
    # Import the autonomous app creation module
    from autonomous_instagram_app import create_app_bundle, create_installer
    
    # Create the app bundle
    bundle_path = create_app_bundle()
    print(f'✅ Created app bundle: {bundle_path}')
    
    # Create installer script
    installer_path = create_installer()
    print(f'✅ Created installer: {installer_path}')
    
    print('🎉 Build completed successfully!')
    
except Exception as e:
    print(f'❌ Build failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Check if build was successful
if [ ! -d "Instagram Bot.app" ]; then
    echo "❌ Build failed - app bundle not created"
    exit 1
fi

echo ""
echo "📋 Making executable files executable..."
chmod +x "Instagram Bot.app/Contents/MacOS/Instagram Bot"

echo ""
echo "🚀 Installing fixed version to Applications..."

# Copy to Applications directory
if cp -R "Instagram Bot.app" "/Applications/" 2>/dev/null; then
    echo "✅ Successfully installed to Applications folder"
else
    echo "🔐 Installation requires administrator permission..."
    sudo cp -R "Instagram Bot.app" "/Applications/"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully installed to Applications folder"
        # Set proper permissions
        sudo chmod -R 755 "/Applications/Instagram Bot.app"
        echo "🔒 Set proper file permissions"
    else
        echo "❌ Installation failed"
        exit 1
    fi
fi

echo ""
echo "✅ Instagram Bot has been fixed and reinstalled!"
echo ""
echo "🎯 FIXES APPLIED:"
echo "   1. ✅ Fixed app launch issue from dock icon"
echo "   2. ✅ Enhanced error handling for automation failures"
echo "   3. ✅ Improved login process with better error detection"
echo "   4. ✅ Fixed macOS threading issues"
echo "   5. ✅ Added comprehensive debugging and screenshots"
echo ""
echo "📱 The app is now available in:"
echo "   • Applications folder (find it in Finder)"
echo "   • Launchpad (search for 'Instagram Bot')"
echo "   • Spotlight search (⌘+Space, type 'Instagram Bot')"
echo ""
echo "💡 Usage Tips:"
echo "   • Click the app icon to launch"
echo "   • Configure your Instagram credentials"
echo "   • Click 'Start Autonomous Mode'"
echo "   • Close window to run in background"
echo "   • Click dock icon to check progress anytime"
echo ""

# Ask if user wants to launch immediately
read -p "🚀 Launch Instagram Bot now? (y/n): " launch_now
if [[ $launch_now =~ ^[Yy]$ ]]; then
    echo "🚀 Launching Instagram Bot..."
    open "/Applications/Instagram Bot.app"
    echo "✅ Instagram Bot launched! Check your dock."
else
    echo "👍 You can launch Instagram Bot from Applications folder anytime"
fi

echo ""
echo "🤖 Instagram Bot is ready for autonomous operation!" 