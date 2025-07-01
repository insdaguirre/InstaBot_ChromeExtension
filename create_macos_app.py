#!/usr/bin/env python3
"""
Create Instagram Bot as a Professional macOS Application
Enhanced version focused on autonomous operation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import plistlib

def create_professional_icon():
    """Create a professional app icon"""
    icon_script = '''#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont
import colorsys

# Create a 512x512 icon with Instagram-style gradient
def create_icon():
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create Instagram-style gradient background
    for y in range(size):
        for x in range(size):
            # Calculate distance from center
            dx = x - size/2
            dy = y - size/2
            distance = (dx*dx + dy*dy) ** 0.5
            max_distance = size * 0.7
            
            if distance <= max_distance:
                # Gradient from purple to pink to orange
                t = distance / max_distance
                if t < 0.3:
                    # Purple to magenta
                    r = int(131 + (237-131) * (t/0.3))
                    g = int(58 + (117-58) * (t/0.3)) 
                    b = int(180 + (180-180) * (t/0.3))
                elif t < 0.7:
                    # Magenta to orange
                    t2 = (t - 0.3) / 0.4
                    r = int(237 + (252-237) * t2)
                    g = int(117 + (175-117) * t2)
                    b = int(180 + (69-180) * t2)
                else:
                    # Orange fade
                    t2 = (t - 0.7) / 0.3
                    r = int(252 - 50 * t2)
                    g = int(175 - 50 * t2)
                    b = int(69 - 30 * t2)
                
                alpha = int(255 * (1 - t * 0.1))
                img.putpixel((x, y), (r, g, b, alpha))
    
    # Add rounded corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=size//8, fill=255)
    
    # Apply mask
    img.putalpha(mask)
    
    # Add robot/automation icon in center
    center = size // 2
    icon_size = size // 3
    
    # Draw robot head
    robot_color = (255, 255, 255, 220)
    head_radius = icon_size // 3
    draw.ellipse([center - head_radius, center - head_radius - icon_size//6, 
                  center + head_radius, center + head_radius - icon_size//6], 
                 fill=robot_color)
    
    # Draw robot body  
    body_width = icon_size // 2
    body_height = icon_size // 2
    draw.rounded_rectangle([center - body_width//2, center - icon_size//12,
                           center + body_width//2, center + body_height - icon_size//12],
                          radius=10, fill=robot_color)
    
    # Draw eyes
    eye_radius = 6
    eye_offset = 15
    draw.ellipse([center - eye_offset - eye_radius, center - head_radius + 10,
                  center - eye_offset + eye_radius, center - head_radius + 10 + eye_radius*2],
                 fill=(100, 100, 100))
    draw.ellipse([center + eye_offset - eye_radius, center - head_radius + 10,
                  center + eye_offset + eye_radius, center - head_radius + 10 + eye_radius*2],
                 fill=(100, 100, 100))
    
    # Draw antenna
    draw.line([center, center - head_radius - icon_size//6, center, center - head_radius - icon_size//4], 
              fill=robot_color, width=3)
    draw.ellipse([center-4, center - head_radius - icon_size//4 - 4,
                  center+4, center - head_radius - icon_size//4 + 4], fill=robot_color)
    
    img.save('icon.png')
    print("✅ Professional icon created")

if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"⚠️ Icon creation failed: {e}")
        # Create simple fallback
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (512, 512), (131, 58, 180, 255))
        draw = ImageDraw.Draw(img)
        draw.text((256, 256), '🤖', font=None, anchor='mm', fill='white')
        img.save('icon.png')
'''
    
    try:
        with open('temp_icon_creator.py', 'w') as f:
            f.write(icon_script)
        
        subprocess.run([sys.executable, 'temp_icon_creator.py'], capture_output=True)
        os.remove('temp_icon_creator.py')
        
        if Path('icon.png').exists():
            return str(Path('icon.png').absolute())
    except Exception as e:
        print(f"⚠️ Professional icon creation failed: {e}")
    
    return None

def create_autonomous_app_script():
    """Create the main app script focused on autonomous operation"""
    app_script = '''#!/usr/bin/env python3
"""
Instagram Bot - Autonomous macOS Application
Professional app focused on autonomous operation with periodic check-ins
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import signal
import threading
import time
import json
from pathlib import Path
from datetime import datetime

# Ensure we're in the right directory
app_dir = Path(__file__).parent.parent.parent
os.chdir(app_dir)
sys.path.insert(0, str(app_dir))

# Global state
app_should_quit = False
automation_thread = None
status_data = {
    "running": False,
    "last_activity": None,
    "daily_follows": 0,
    "daily_unfollows": 0,
    "total_follows": 0,
    "errors": []
}

def handle_signal(signum, frame):
    """Handle signals for show/hide"""
    global app_should_quit
    if signum == signal.SIGUSR1:
        if hasattr(handle_signal, 'root'):
            handle_signal.root.deiconify()
            handle_signal.root.lift()
            handle_signal.root.focus_force()
    elif signum == signal.SIGUSR2:
        app_should_quit = True
        if hasattr(handle_signal, 'root'):
            handle_signal.root.quit()

signal.signal(signal.SIGUSR1, handle_signal)
signal.signal(signal.SIGUSR2, handle_signal)

class AutonomousInstagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Bot - Autonomous Mode")
        self.root.geometry("600x500")
        
        # Make it a proper macOS app
        self.root.createcommand('tk::mac::ReopenDocument', lambda: self.show_window())
        self.root.createcommand('tk::mac::Quit', lambda: self.quit_app())
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.setup_gui()
        self.load_settings()
        self.update_status_loop()
        
    def setup_gui(self):
        """Create autonomous-focused GUI"""
        # Title
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill="x")
        
        title_label = ttk.Label(title_frame, text="🤖 Instagram Bot", 
                               font=("SF Pro Display", 24, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Autonomous Instagram Growth", 
                                  font=("SF Pro Display", 12))
        subtitle_label.pack()
        
        # Status Dashboard
        self.create_status_dashboard()
        
        # Quick Controls
        self.create_quick_controls()
        
        # Settings Panel
        self.create_settings_panel()
        
        # Footer
        footer_frame = ttk.Frame(self.root, padding="10")
        footer_frame.pack(fill="x", side="bottom")
        
        footer_label = ttk.Label(footer_frame, 
                                text="Close window to run in background • ⌘Q to quit completely",
                                font=("SF Pro Display", 10))
        footer_label.pack()
        
    def create_status_dashboard(self):
        """Create status overview dashboard"""
        status_frame = ttk.LabelFrame(self.root, text="📊 Status Dashboard", padding="15")
        status_frame.pack(fill="x", padx=20, pady=10)
        
        # Status indicator
        self.status_var = tk.StringVar(value="⚪ Stopped")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                     font=("SF Pro Display", 14, "bold"))
        self.status_label.pack()
        
        # Stats grid
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill="x", pady=10)
        
        # Daily stats
        daily_frame = ttk.Frame(stats_frame)
        daily_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(daily_frame, text="Today", font=("SF Pro Display", 12, "bold")).pack()
        self.daily_follows_var = tk.StringVar(value="Follows: 0")
        self.daily_unfollows_var = tk.StringVar(value="Unfollows: 0")
        ttk.Label(daily_frame, textvariable=self.daily_follows_var).pack()
        ttk.Label(daily_frame, textvariable=self.daily_unfollows_var).pack()
        
        # Total stats
        total_frame = ttk.Frame(stats_frame)
        total_frame.pack(side="right", fill="x", expand=True)
        
        ttk.Label(total_frame, text="Total", font=("SF Pro Display", 12, "bold")).pack()
        self.total_follows_var = tk.StringVar(value="Follows: 0")
        self.last_activity_var = tk.StringVar(value="Last: Never")
        ttk.Label(total_frame, textvariable=self.total_follows_var).pack()
        ttk.Label(total_frame, textvariable=self.last_activity_var).pack()
        
    def create_quick_controls(self):
        """Create quick control buttons"""
        control_frame = ttk.LabelFrame(self.root, text="🎛️ Quick Controls", padding="15")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        self.start_btn = ttk.Button(button_frame, text="▶️ Start", 
                                   command=self.start_automation,
                                   style="Accent.TButton")
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop", 
                                  command=self.stop_automation)
        self.stop_btn.pack(side="left", padx=5)
        
        self.stats_btn = ttk.Button(button_frame, text="📈 Stats", 
                                   command=self.show_detailed_stats)
        self.stats_btn.pack(side="left", padx=5)
        
        self.settings_btn = ttk.Button(button_frame, text="⚙️ Settings", 
                                      command=self.show_settings)
        self.settings_btn.pack(side="left", padx=5)
        
    def create_settings_panel(self):
        """Create collapsible settings panel"""
        self.settings_frame = ttk.LabelFrame(self.root, text="⚙️ Essential Settings", padding="15")
        self.settings_visible = False
        
        # Username/Password
        creds_frame = ttk.Frame(self.settings_frame)
        creds_frame.pack(fill="x", pady=5)
        
        ttk.Label(creds_frame, text="Username:").pack(side="left")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(creds_frame, textvariable=self.username_var, width=20)
        username_entry.pack(side="right")
        
        pass_frame = ttk.Frame(self.settings_frame)
        pass_frame.pack(fill="x", pady=5)
        
        ttk.Label(pass_frame, text="Password:").pack(side="left")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(pass_frame, textvariable=self.password_var, 
                                  show="*", width=20)
        password_entry.pack(side="right")
        
        # Target accounts
        targets_frame = ttk.Frame(self.settings_frame)
        targets_frame.pack(fill="x", pady=5)
        
        ttk.Label(targets_frame, text="Target Accounts:").pack(side="left")
        self.targets_var = tk.StringVar(value="deadmau5,skrillex,housemusic")
        targets_entry = ttk.Entry(targets_frame, textvariable=self.targets_var, width=30)
        targets_entry.pack(side="right")
        
        # Save button
        save_btn = ttk.Button(self.settings_frame, text="💾 Save Settings", 
                             command=self.save_settings)
        save_btn.pack(pady=10)
        
    def show_settings(self):
        """Toggle settings visibility"""
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(fill="x", padx=20, pady=10)
            self.settings_visible = True
            
    def start_automation(self):
        """Start autonomous automation"""
        if not self.validate_settings():
            messagebox.showerror("Error", "Please configure username, password, and target accounts")
            self.show_settings()
            return
        
        global automation_thread, status_data
        if automation_thread and automation_thread.is_alive():
            return
        
        status_data["running"] = True
        self.status_var.set("🟢 Running")
        
        automation_thread = threading.Thread(target=self.run_automation_loop, daemon=True)
        automation_thread.start()
        
        messagebox.showinfo("Started", "Automation started! You can now close this window and the bot will continue running in the background.")
        
    def stop_automation(self):
        """Stop automation"""
        global status_data
        status_data["running"] = False
        self.status_var.set("⚪ Stopped")
        
    def run_automation_loop(self):
        """Main automation loop"""
        try:
            # Import and run the actual Instagram automation
            from instagram_gui import InstagramAutomationGUI
            
            # Create a minimal root for the automation
            automation_root = tk.Tk()
            automation_root.withdraw()  # Hide the automation window
            
            # Create automation instance
            automation = InstagramAutomationGUI(automation_root)
            
            # Override settings with our values
            automation.username_var.set(self.username_var.get())
            automation.password_var.set(self.password_var.get())
            automation.target_accounts_var.set(self.targets_var.get())
            
            # Start scheduler
            automation.toggle_scheduler()
            
            # Keep running while status is active
            global status_data
            while status_data["running"]:
                automation_root.update()
                time.sleep(1)
                
        except Exception as e:
            status_data["errors"].append(f"{datetime.now()}: {str(e)}")
            status_data["running"] = False
            self.status_var.set("🔴 Error")
            
    def validate_settings(self):
        """Validate required settings"""
        return (self.username_var.get().strip() and 
                self.password_var.get().strip() and
                self.targets_var.get().strip())
        
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "target_accounts": self.targets_var.get()
        }
        
        try:
            with open('autonomous_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Saved", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            
    def load_settings(self):
        """Load settings from file"""
        try:
            if Path('autonomous_settings.json').exists():
                with open('autonomous_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.username_var.set(settings.get("username", ""))
                self.password_var.set(settings.get("password", ""))
                self.targets_var.set(settings.get("target_accounts", "deadmau5,skrillex,housemusic"))
        except Exception as e:
            print(f"⚠️ Could not load settings: {e}")
            
    def update_status_loop(self):
        """Update status display"""
        try:
            # Update status from automation data
            global status_data
            
            if status_data.get("last_activity"):
                self.last_activity_var.set(f"Last: {status_data['last_activity']}")
            
            self.daily_follows_var.set(f"Follows: {status_data.get('daily_follows', 0)}")
            self.daily_unfollows_var.set(f"Unfollows: {status_data.get('daily_unfollows', 0)}")
            self.total_follows_var.set(f"Follows: {status_data.get('total_follows', 0)}")
            
        except Exception as e:
            print(f"⚠️ Status update error: {e}")
        
        # Schedule next update
        self.root.after(5000, self.update_status_loop)
        
    def show_detailed_stats(self):
        """Show detailed statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📈 Detailed Statistics")
        stats_window.geometry("500x400")
        
        text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        
        # Load and display stats
        stats_text = "📊 Instagram Bot Statistics\\n\\n"
        
        try:
            # Load follow data
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows_data = json.load(f)
                    stats_text += f"Total Users Followed: {len(follows_data)}\\n"
                    
                    # Count by status
                    following = sum(1 for user in follows_data.values() 
                                  if user.get('status') == 'following')
                    unfollowed = sum(1 for user in follows_data.values() 
                                   if user.get('status') == 'unfollowed')
                    
                    stats_text += f"Currently Following: {following}\\n"
                    stats_text += f"Previously Unfollowed: {unfollowed}\\n\\n"
            
            # Load action log
            if Path('instagram_data/action_log.json').exists():
                with open('instagram_data/action_log.json', 'r') as f:
                    action_log = json.load(f)
                    
                    recent_actions = sorted(action_log, key=lambda x: x['timestamp'])[-10:]
                    stats_text += "Recent Activity:\\n"
                    for action in recent_actions:
                        timestamp = action['timestamp'][:16].replace('T', ' ')
                        stats_text += f"{timestamp}: {action['action']} @{action['target']}\\n"
            
        except Exception as e:
            stats_text += f"Error loading stats: {e}"
        
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        
    def hide_window(self):
        """Hide window but keep app running"""
        global app_should_quit
        if not app_should_quit:
            self.root.withdraw()
            print("🔽 Window hidden - app continues running in background")
        else:
            self.quit_app()
            
    def show_window(self):
        """Show window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def quit_app(self):
        """Quit application completely"""
        global app_should_quit, status_data
        app_should_quit = True
        status_data["running"] = False
        self.root.quit()

def main():
    """Main application entry point"""
    global app_should_quit
    
    try:
        # Create root window
        root = tk.Tk()
        handle_signal.root = root
        
        # Set app icon if available
        try:
            if Path('icon.png').exists():
                root.iconphoto(True, tk.PhotoImage(file='icon.png'))
        except:
            pass
        
        # Create autonomous app
        app = AutonomousInstagramApp(root)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (500 // 2)
        root.geometry(f"600x500+{x}+{y}")
        
        print("🚀 Instagram Bot - Autonomous Mode Started")
        print("📱 Configure settings and click Start for autonomous operation")
        print("🔽 Close window to run in background")
        print("👆 Click dock icon to reopen")
        print("⌘Q Quit completely")
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    return app_script

def create_enhanced_app_bundle():
    """Create enhanced app bundle with autonomous features"""
    app_name = "Instagram Bot"
    bundle_name = f"{app_name}.app"
    bundle_path = Path(bundle_name)
    
    print(f"🚀 Creating Enhanced Instagram Bot App...")
    
    # Remove existing bundle
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    
    # Create bundle structure
    contents = bundle_path / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    for dir_path in [contents, macos, resources]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Enhanced Info.plist with better integration
    info_plist = {
        "CFBundleName": app_name,
        "CFBundleDisplayName": "Instagram Bot",
        "CFBundleIdentifier": "com.instagrambot.autonomous",
        "CFBundleVersion": "2.0.0",
        "CFBundleShortVersionString": "2.0.0",
        "CFBundleExecutable": "Instagram Bot",
        "CFBundleIconFile": "AppIcon.icns",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "IGBA",
        "LSMinimumSystemVersion": "10.15.0",
        "NSHighResolutionCapable": True,
        "NSAppleScriptEnabled": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSUIElement": False,
        "NSHumanReadableCopyright": "© 2024 Instagram Bot - Autonomous Growth Tool",
        "CFBundleDocumentTypes": [],
        "NSApplication": {
            "NSMainNibFile": "",
            "NSPrincipalClass": "NSApplication"
        },
        "NSAppTransportSecurity": {
            "NSAllowsArbitraryLoads": True
        }
    }
    
    # Write Info.plist
    with open(contents / "Info.plist", 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create main executable
    main_script = create_autonomous_app_script()
    executable_path = macos / "Instagram Bot"
    
    with open(executable_path, 'w') as f:
        f.write(main_script)
    
    os.chmod(executable_path, 0o755)
    
    # Create professional icon
    icon_path = create_professional_icon()
    if icon_path:
        try:
            # Convert to ICNS format for macOS
            icns_path = resources / "AppIcon.icns"
            result = subprocess.run(['sips', '-s', 'format', 'icns', icon_path, '--out', str(icns_path)], 
                          capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Professional icon converted to ICNS format")
            else:
                # Fallback: copy as PNG
                shutil.copy2(icon_path, resources / "AppIcon.png")
                print("⚠️ Using PNG icon as fallback")
                
        except Exception as e:
            print(f"⚠️ Icon processing failed: {e}")
    
    print(f"✅ Enhanced app bundle created: {bundle_path}")
    return bundle_path

def create_installation_script():
    """Create script to install app to Applications folder"""
    install_script = f'''#!/bin/bash
# Instagram Bot - Application Installer
echo "📱 Installing Instagram Bot to Applications folder..."

APP_NAME="Instagram Bot.app"
CURRENT_DIR="{Path.cwd()}"
APPLICATIONS_DIR="/Applications"

# Check if app exists
if [ ! -d "$CURRENT_DIR/$APP_NAME" ]; then
    echo "❌ $APP_NAME not found in current directory"
    echo "   Please run create_macos_app.py first"
    exit 1
fi

# Copy to Applications (with sudo if needed)
echo "📦 Copying to $APPLICATIONS_DIR..."
if cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS_DIR/" 2>/dev/null; then
    echo "✅ Successfully installed to Applications folder"
else
    echo "🔐 Requesting admin permission..."
    sudo cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS_DIR/"
    if [ $? -eq 0 ]; then
        echo "✅ Successfully installed to Applications folder"
    else
        echo "❌ Installation failed"
        exit 1
    fi
fi

# Set proper permissions
sudo chmod -R 755 "$APPLICATIONS_DIR/$APP_NAME"

echo ""
echo "🎉 Installation Complete!"
echo "📱 You can now:"
echo "   • Find 'Instagram Bot' in Applications folder"
echo "   • Launch from Launchpad or Spotlight"
echo "   • Drag to Dock for easy access"
echo ""
echo "🚀 To launch now: open '/Applications/$APP_NAME'"

# Ask if user wants to launch
read -p "🚀 Launch Instagram Bot now? (y/n): " launch
if [[ $launch =~ ^[Yy]$ ]]; then
    open "$APPLICATIONS_DIR/$APP_NAME"
    echo "✅ Instagram Bot launched!"
fi
'''
    
    install_path = Path("install_to_applications.sh")
    with open(install_path, 'w') as f:
        f.write(install_script)
    
    os.chmod(install_path, 0o755)
    print(f"✅ Installation script created: {install_path}")
    return install_path

def create_readme():
    """Create README for the app"""
    readme_content = '''# Instagram Bot - macOS Application

## 🎯 Autonomous Instagram Growth

This application provides fully autonomous Instagram growth with minimal user interaction required.

### 🚀 Quick Start

1. **Launch the app** from Applications folder or double-click `Instagram Bot.app`
2. **Configure settings**: Enter your Instagram username, password, and target accounts
3. **Click Start**: The bot will run autonomously in the background
4. **Close window**: App continues running with dock icon visible
5. **Periodic check-ins**: Click dock icon to view progress and stats

### 🤖 Autonomous Features

- **Background Operation**: Runs continuously even when window is closed
- **Smart Scheduling**: Automatically follows/unfollows at optimal times
- **Growth Analytics**: Track daily and total progress
- **Error Recovery**: Handles rate limits and errors automatically
- **macOS Integration**: Native dock icon and menu integration

### ⚙️ Configuration

Essential settings you need to configure:
- **Username**: Your Instagram username
- **Password**: Your Instagram password  
- **Target Accounts**: Comma-separated list of accounts to follow followers from
  - Example: `deadmau5,skrillex,housemusic,1001tracklists`

### 📊 Monitoring

The app provides several ways to monitor progress:
- **Status Dashboard**: Real-time status and daily stats
- **Detailed Stats**: Complete history and activity log
- **Background Indicator**: Dock icon shows when running

### 🔒 Privacy & Security

- Settings stored locally on your device
- No external servers or data collection
- Instagram credentials only used for automation
- Follows Instagram's best practices to avoid detection

### 💡 Usage Tips

1. **Set it and forget it**: Configure once, runs autonomously
2. **Check weekly**: Review stats and adjust settings as needed
3. **Quality targets**: Choose accounts with engaged, relevant followers
4. **Patience**: Gradual growth is more sustainable and safer

### 📱 Installation

The app is designed to work like any other macOS application:
- Install to Applications folder
- Launch from Launchpad or Spotlight
- Add to Dock for easy access
- Runs independently without dependencies

Enjoy autonomous Instagram growth! 🚀
'''

    with open('APP_README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ App README created: APP_README.md")

def main():
    """Enhanced main setup function"""
    print("🤖 Creating Instagram Bot - Autonomous macOS App")
    print("=" * 60)
    
    # Check platform
    if sys.platform != 'darwin':
        print("❌ This script is for macOS only")
        sys.exit(1)
    
    # Check required files
    if not Path('instagram_gui.py').exists():
        print("❌ instagram_gui.py not found!")
        sys.exit(1)
    
    try:
        # Install dependencies if needed
        print("📦 Checking dependencies...")
        try:
            from PIL import Image
            print("✅ PIL available for icon creation")
        except ImportError:
            print("⚠️ Installing Pillow for professional icons...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], check=True)
        
        # Create enhanced app bundle
        bundle_path = create_enhanced_app_bundle()
        
        # Create installation script
        install_script = create_installation_script()
        
        # Create documentation
        create_readme()
        
        print("\n🎉 Enhanced Instagram Bot App Created!")
        print("=" * 60)
        print(f"📱 App Bundle: {bundle_path}")
        print(f"🚀 Installer: {install_script}")
        print("📖 Documentation: APP_README.md")
        print("")
        print("🔹 Next Steps:")
        print("  1. Run installer: ./install_to_applications.sh")
        print("  2. Or manually drag to Applications folder")
        print("  3. Launch from Applications or Launchpad")
        print("  4. Configure your Instagram credentials")
        print("  5. Click Start for autonomous operation!")
        print("")
        print("🤖 Features:")
        print("  • Runs autonomously in background")
        print("  • Professional macOS integration")
        print("  • Periodic check-ins via dock icon")
        print("  • No technical knowledge required")
        
        # Offer to install
        response = input("\n🚀 Install to Applications folder now? (y/n): ").lower()
        if response in ['y', 'yes', '']:
            print("🚀 Running installer...")
            subprocess.run(['bash', str(install_script)])
        else:
            print("💡 Run ./install_to_applications.sh when ready!")
        
    except Exception as e:
        print(f"❌ Error creating enhanced app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 