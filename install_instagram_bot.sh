#!/bin/bash
# Instagram Bot - Applications Folder Installer

APP_NAME="Instagram Bot.app"
CURRENT_DIR="/Users/diegoaguirre/instagram automation"
APPLICATIONS_DIR="/Applications"

echo "📱 Installing Instagram Bot to Applications folder..."
echo ""

# Check if app bundle exists
if [ ! -d "$CURRENT_DIR/$APP_NAME" ]; then
    echo "❌ Error: $APP_NAME not found in current directory"
    echo "   Please run the build script first to create the app"
    exit 1
fi

echo "📦 Found app bundle: $APP_NAME"

# Attempt to copy to Applications folder
echo "🚀 Installing to $APPLICATIONS_DIR..."

if cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS_DIR/" 2>/dev/null; then
    echo "✅ Successfully installed to Applications folder"
else
    echo "🔐 Installation requires administrator permission..."
    sudo cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS_DIR/"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully installed to Applications folder"
        # Set proper permissions
        sudo chmod -R 755 "$APPLICATIONS_DIR/$APP_NAME"
        echo "🔒 Set proper file permissions"
    else
        echo "❌ Installation failed"
        echo "   Please try running with sudo or check permissions"
        exit 1
    fi
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📱 Instagram Bot is now available in:"
echo "   • Applications folder (find it in Finder)"
echo "   • Launchpad (search for 'Instagram Bot')"
echo "   • Spotlight search (⌘+Space, type 'Instagram Bot')"
echo ""
echo "💡 Usage Tips:"
echo "   • Drag to Dock for easy access"
echo "   • Configure your Instagram credentials"
echo "   • Click 'Start Autonomous Mode' and close window"
echo "   • Bot continues running in background"
echo "   • Click dock icon to check progress anytime"
echo ""

# Ask if user wants to launch immediately
read -p "🚀 Launch Instagram Bot now? (y/n): " launch_now
if [[ $launch_now =~ ^[Yy]$ ]]; then
    echo "🚀 Launching Instagram Bot..."
    open "$APPLICATIONS_DIR/$APP_NAME"
    echo "✅ Instagram Bot launched! Check your dock."
else
    echo "👍 You can launch Instagram Bot from Applications folder anytime"
fi

echo ""
echo "🤖 Ready for autonomous Instagram growth!"
