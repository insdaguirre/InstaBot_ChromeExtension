#!/usr/bin/env python3
"""
Build Autonomous Instagram Bot as macOS Application
Complete build script for professional autonomous Instagram growth tool
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import plistlib

def create_app_bundle():
    """Create the complete macOS app bundle"""
    app_name = "Instagram Bot"
    bundle_name = f"{app_name}.app"
    bundle_path = Path(bundle_name)
    
    print(f"🚀 Creating {bundle_name}...")
    
    # Remove existing bundle if it exists
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
        print("🗑️ Removed existing app bundle")
    
    # Create bundle directory structure
    contents = bundle_path / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    for dir_path in [contents, macos, resources]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("📁 Created app bundle structure")
    
    # Create Info.plist with comprehensive metadata and dock integration
    info_plist = {
        "CFBundleName": app_name,
        "CFBundleDisplayName": "Instagram Bot",
        "CFBundleIdentifier": "com.instagrambot.autonomous",
        "CFBundleVersion": "2.1.0",
        "CFBundleShortVersionString": "2.1.0", 
        "CFBundleExecutable": "Instagram Bot",
        "CFBundleIconFile": "AppIcon.icns",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "IGBA",
        "LSMinimumSystemVersion": "10.15.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSUIElement": False,  # Shows in dock normally
        "NSSupportsAutomaticTermination": False,  # Don't auto-terminate
        "NSSupportsSuddenTermination": False,     # Don't sudden-terminate
        "LSMultipleInstancesProhibited": True,    # Only one instance
        "NSHumanReadableCopyright": "© 2024 Instagram Bot - Autonomous Growth Tool",
        "CFBundleDocumentTypes": [],
        "NSApplication": {
            "NSMainNibFile": "",
            "NSPrincipalClass": "NSApplication"
        },
        "NSAppTransportSecurity": {
            "NSAllowsArbitraryLoads": True  # Allow Instagram connections
        },
        # Support dock icon reopen events
        "NSAppleEventsUsageDescription": "Instagram Bot uses Apple Events for dock integration",
        "CFBundleInfoDictionaryVersion": "6.0"
    }
    
    # Write Info.plist
    with open(contents / "Info.plist", 'wb') as f:
        plistlib.dump(info_plist, f)
    
    print("📄 Created Info.plist")
    
    # Read the autonomous bot main script
    if not Path('autonomous_bot_main.py').exists():
        print("❌ autonomous_bot_main.py not found!")
        return None
    
    with open('autonomous_bot_main.py', 'r') as f:
        main_script_content = f.read()
    
    # Create the main executable - REVERT TO ORIGINAL WORKING METHOD
    executable_path = macos / "Instagram Bot"
    with open(executable_path, 'w') as f:
        f.write(main_script_content)
    
    # Make executable
    os.chmod(executable_path, 0o755)
    print("💻 Created main executable")
    
    # Handle application icon - use custom icon.png
    icon_created = False
    if Path('icon.png').exists():
        try:
            # Convert PNG to ICNS using system tools
            icns_path = resources / "AppIcon.icns"
            result = subprocess.run([
                'sips', '-s', 'format', 'icns', 
                'icon.png', '--out', str(icns_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and icns_path.exists():
                print("🎨 Converted custom icon.png to ICNS format")
                icon_created = True
            else:
                # Fallback: copy PNG as icon
                shutil.copy2('icon.png', resources / "AppIcon.png")
                print("🎨 Used custom icon.png as fallback")
                icon_created = True
                
        except Exception as e:
            print(f"⚠️ Icon processing failed: {e}")
    
    if not icon_created:
        print("⚠️ No custom icon found - app will use default icon")
    
    print(f"✅ App bundle created successfully: {bundle_path}")
    return bundle_path

def create_installer_script():
    """Create script to install app to Applications folder"""
    installer_content = f'''#!/bin/bash
# Instagram Bot - Applications Folder Installer

APP_NAME="Instagram Bot.app"
CURRENT_DIR="{Path.cwd()}"
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
'''
    
    installer_path = Path("install_instagram_bot.sh")
    with open(installer_path, 'w') as f:
        f.write(installer_content)
    
    # Make installer executable
    os.chmod(installer_path, 0o755)
    print(f"✅ Installer script created: {installer_path}")
    return installer_path

def main():
    """Main build function"""
    print("🤖 Building Autonomous Instagram Bot for macOS")
    print("=" * 60)
    
    # Platform check
    if sys.platform != 'darwin':
        print("❌ This script is designed for macOS only")
        sys.exit(1)
    
    # Dependency check
    required_files = ['instagram_gui.py', 'autonomous_bot_main.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Required files missing: {', '.join(missing_files)}")
        print("   Please ensure all necessary files are present")
        sys.exit(1)
    
    print("✅ All required files found")
    
    # Check for custom icon
    if Path('icon.png').exists():
        print("✅ Custom icon.png found")
    else:
        print("⚠️ Custom icon.png not found - app will use default icon")
    
    try:
        print("\n🔨 Building application...")
        
        # Create the app bundle
        bundle_path = create_app_bundle()
        if not bundle_path:
            print("❌ Failed to create app bundle")
            sys.exit(1)
        
        # Create installer script
        installer_path = create_installer_script()
        
        print("\n" + "=" * 60)
        print("🎉 AUTONOMOUS INSTAGRAM BOT BUILD COMPLETE!")
        print("=" * 60)
        
        print(f"\n📱 **App Bundle**: {bundle_path}")
        print(f"🚀 **Installer**: {installer_path}")
        
        print("\n🤖 **Features of Your Autonomous Bot**:")
        print("   • Set-it-and-forget-it operation")
        print("   • Professional macOS integration")
        print("   • Background operation with dock icon")
        print("   • Real-time analytics dashboard")
        print("   • Safe Instagram rate limiting")
        print("   • Intelligent follower targeting")
        
        print("\n🔹 **Next Steps**:")
        print("   1. Install to Applications: ./install_instagram_bot.sh")
        print("   2. Launch from Applications folder")
        print("   3. Configure Instagram credentials")
        print("   4. Set target accounts for growth")
        print("   5. Click 'Start Autonomous Mode'")
        print("   6. Close window - bot runs in background")
        print("   7. Click dock icon to check progress anytime")
        
        print("\n💡 **Pro Tip**: This is now a completely autonomous system.")
        print("   Once configured and started, you only need to check in")
        print("   periodically to monitor progress and adjust targets!")
        
        # Offer immediate installation
        response = input("\n🚀 Install to Applications folder now? (y/n): ").lower()
        if response in ['y', 'yes', '']:
            print("🚀 Running installer...")
            result = subprocess.run(['bash', str(installer_path)], capture_output=False)
            if result.returncode == 0:
                print("\n✅ Installation complete! Check your Applications folder.")
            else:
                print("\n⚠️ Installation may have had issues. Try running manually:")
                print(f"   bash {installer_path}")
        else:
            print(f"\n💾 Ready to install! Run: ./{installer_path}")
        
        print("\n🤖 Your autonomous Instagram growth tool is ready!")
        
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
 