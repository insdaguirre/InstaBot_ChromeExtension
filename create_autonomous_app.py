#!/usr/bin/env python3
"""
Create Instagram Bot as a Professional Autonomous macOS Application
Enhanced version focused on set-it-and-forget-it operation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import plistlib

def create_professional_icon():
    """Create a professional app icon using system tools"""
    try:
        # Create a basic icon using built-in tools
        icon_script = '''
from PIL import Image, ImageDraw
import math

# Create 512x512 icon
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Instagram-style gradient background
center = size // 2
max_radius = size // 2

# Create gradient circles
for r in range(max_radius, 0, -2):
    # Color gradient from purple to orange
    t = 1 - (r / max_radius)
    if t < 0.5:
        # Purple to magenta
        red = int(131 + (237-131) * (t*2))
        green = int(58 + (117-58) * (t*2))
        blue = int(180)
    else:
        # Magenta to orange
        t2 = (t - 0.5) * 2
        red = int(237 + (252-237) * t2)
        green = int(117 + (175-117) * t2)
        blue = int(180 - 111 * t2)
    
    alpha = int(255 * (0.9 - t * 0.1))
    color = (red, green, blue, alpha)
    
    draw.ellipse([center-r, center-r, center+r, center+r], fill=color)

# Add robot/automation symbol
robot_size = size // 3
robot_center = center

# Robot head (circle)
head_radius = robot_size // 4
head_color = (255, 255, 255, 230)
draw.ellipse([robot_center - head_radius, robot_center - head_radius - robot_size//8,
              robot_center + head_radius, robot_center + head_radius - robot_size//8],
             fill=head_color)

# Robot body (rounded rectangle)
body_width = robot_size // 3
body_height = robot_size // 3
body_top = robot_center - robot_size//16
body_bottom = body_top + body_height
draw.rounded_rectangle([robot_center - body_width//2, body_top,
                       robot_center + body_width//2, body_bottom],
                      radius=15, fill=head_color)

# Robot eyes
eye_size = 8
eye_y = robot_center - head_radius + 15
eye_color = (80, 80, 80, 255)
draw.ellipse([robot_center - 20 - eye_size//2, eye_y - eye_size//2,
              robot_center - 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)
draw.ellipse([robot_center + 20 - eye_size//2, eye_y - eye_size//2,
              robot_center + 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)

# Antenna
antenna_top = robot_center - head_radius - robot_size//8 - 20
draw.line([robot_center, robot_center - head_radius - robot_size//8,
           robot_center, antenna_top], fill=head_color, width=4)
draw.ellipse([robot_center-6, antenna_top-6, robot_center+6, antenna_top+6], fill=head_color)

# Save icon
img.save('app_icon.png')
print("✅ Professional icon created")
'''
        
        # Try to use PIL if available
        try:
            exec(icon_script)
            if Path('app_icon.png').exists():
                return str(Path('app_icon.png').absolute())
        except ImportError:
            print("⚠️ PIL not available, creating simple icon...")
            
        # Fallback: create simple icon using system tools
        subprocess.run([
            'python3', '-c', 
            '''
import base64
from pathlib import Path

# Simple PNG icon data (robot emoji-style)
icon_data = "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVHic7d1RbhMxEAXQl9ArcAX2BuQK7Qm4Ajm..."

# This is just a placeholder - in reality we'd have a proper base64 encoded PNG
with open("app_icon.png", "wb") as f:
    # Create a simple colored square as fallback
    simple_png = bytes([137, 80, 78, 71, 13, 10, 26, 10] + [0] * 50)
    
# Actually create a proper simple icon
from PIL import Image, ImageDraw
img = Image.new('RGBA', (512, 512), (131, 58, 180, 255))
draw = ImageDraw.Draw(img)

# Add simple robot shape
draw.rectangle([156, 156, 356, 356], fill=(255, 255, 255, 200))
draw.ellipse([206, 180, 306, 280], fill=(80, 80, 80))
draw.rectangle([176, 220, 336, 380], fill=(255, 255, 255, 200))

img.save('app_icon.png')
print("✅ Simple fallback icon created")
'''
        ], capture_output=True)
        
        if Path('app_icon.png').exists():
            return str(Path('app_icon.png').absolute())
            
    except Exception as e:
        print(f"⚠️ Icon creation failed: {e}")
    
    return None

def create_autonomous_main_script():
    """Create the main autonomous app script"""
    return '''#!/usr/bin/env python3
"""
Instagram Bot - Autonomous macOS Application
Professional autonomous Instagram growth tool
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

# Ensure proper path setup
app_dir = Path(__file__).parent.parent.parent
os.chdir(app_dir)
sys.path.insert(0, str(app_dir))

# Global app state
app_should_quit = False
automation_running = False
last_activity = None

def handle_signals(signum, frame):
    """Handle macOS app signals"""
    global app_should_quit
    if signum == signal.SIGUSR1:
        # Show window
        if hasattr(handle_signals, 'root'):
            handle_signals.root.deiconify()
            handle_signals.root.lift()
    elif signum == signal.SIGUSR2:
        # Quit app
        app_should_quit = True
        if hasattr(handle_signals, 'root'):
            handle_signals.root.quit()

# Set up signal handlers
signal.signal(signal.SIGUSR1, handle_signals)
signal.signal(signal.SIGUSR2, handle_signals)

class AutonomousInstagramBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Instagram Bot - Autonomous")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        
        # macOS integration
        self.root.createcommand('tk::mac::ReopenDocument', self.show_window)
        self.root.createcommand('tk::mac::Quit', self.quit_application)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_background)
        
        # App state
        self.settings = {}
        self.stats = {"daily_follows": 0, "daily_unfollows": 0, "total_follows": 0}
        
        self.setup_ui()
        self.load_settings()
        self.start_status_updates()
        
    def setup_ui(self):
        """Create the autonomous-focused user interface"""
        
        # Header
        header = ttk.Frame(self.root, padding="20")
        header.pack(fill="x")
        
        title = ttk.Label(header, text="🤖 Instagram Bot", 
                         font=("SF Pro Display", 28, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header, text="Autonomous Instagram Growth • Set it and forget it",
                           font=("SF Pro Display", 12), foreground="gray")
        subtitle.pack()
        
        # Status Panel
        self.create_status_panel()
        
        # Quick Actions
        self.create_action_panel()
        
        # Settings (collapsible)
        self.create_settings_panel()
        
        # Footer
        footer = ttk.Frame(self.root, padding="10")
        footer.pack(fill="x", side="bottom")
        
        footer_text = ttk.Label(footer, 
                               text="💡 Close window = background mode • ⌘Q = quit completely",
                               font=("SF Pro Display", 10), foreground="gray")
        footer_text.pack()
        
    def create_status_panel(self):
        """Create status overview panel"""
        status_frame = ttk.LabelFrame(self.root, text="📊 Bot Status", padding="20")
        status_frame.pack(fill="x", padx=20, pady=10)
        
        # Status indicator
        status_row = ttk.Frame(status_frame)
        status_row.pack(fill="x", pady=5)
        
        self.status_text = tk.StringVar(value="⚪ Ready to start")
        status_label = ttk.Label(status_row, textvariable=self.status_text, 
                                font=("SF Pro Display", 16, "bold"))
        status_label.pack(side="left")
        
        # Stats grid
        stats_grid = ttk.Frame(status_frame)
        stats_grid.pack(fill="x", pady=15)
        
        # Today's stats
        today_frame = ttk.Frame(stats_grid)
        today_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(today_frame, text="📈 Today", font=("SF Pro Display", 12, "bold")).pack()
        self.today_follows = tk.StringVar(value="Follows: 0")
        self.today_unfollows = tk.StringVar(value="Unfollows: 0")
        ttk.Label(today_frame, textvariable=self.today_follows).pack()
        ttk.Label(today_frame, textvariable=self.today_unfollows).pack()
        
        # All time stats
        total_frame = ttk.Frame(stats_grid)
        total_frame.pack(side="right", fill="x", expand=True)
        
        ttk.Label(total_frame, text="🎯 Total", font=("SF Pro Display", 12, "bold")).pack()
        self.total_follows = tk.StringVar(value="Follows: 0")
        self.last_activity = tk.StringVar(value="Last run: Never")
        ttk.Label(total_frame, textvariable=self.total_follows).pack()
        ttk.Label(total_frame, textvariable=self.last_activity).pack()
        
    def create_action_panel(self):
        """Create quick action buttons"""
        action_frame = ttk.LabelFrame(self.root, text="🎛️ Quick Actions", padding="20")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        button_row = ttk.Frame(action_frame)
        button_row.pack()
        
        # Main action buttons
        self.start_button = ttk.Button(button_row, text="▶️ Start Bot", 
                                      command=self.start_automation,
                                      style="Accent.TButton")
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(button_row, text="⏸️ Stop Bot", 
                                     command=self.stop_automation)
        self.stop_button.pack(side="left", padx=5)
        
        # Info buttons
        ttk.Button(button_row, text="📊 Detailed Stats", 
                  command=self.show_stats).pack(side="left", padx=5)
        
        ttk.Button(button_row, text="⚙️ Settings", 
                  command=self.toggle_settings).pack(side="left", padx=5)
        
    def create_settings_panel(self):
        """Create settings configuration panel"""
        self.settings_frame = ttk.LabelFrame(self.root, text="⚙️ Bot Configuration", padding="20")
        self.settings_visible = False
        
        # Credentials section
        creds_section = ttk.LabelFrame(self.settings_frame, text="Instagram Account", padding="10")
        creds_section.pack(fill="x", pady=5)
        
        # Username
        user_row = ttk.Frame(creds_section)
        user_row.pack(fill="x", pady=2)
        ttk.Label(user_row, text="Username:", width=12).pack(side="left")
        self.username_var = tk.StringVar()
        ttk.Entry(user_row, textvariable=self.username_var, width=25).pack(side="right")
        
        # Password
        pass_row = ttk.Frame(creds_section)
        pass_row.pack(fill="x", pady=2)
        ttk.Label(pass_row, text="Password:", width=12).pack(side="left")
        self.password_var = tk.StringVar()
        ttk.Entry(pass_row, textvariable=self.password_var, show="*", width=25).pack(side="right")
        
        # Target accounts section
        targets_section = ttk.LabelFrame(self.settings_frame, text="Growth Strategy", padding="10")
        targets_section.pack(fill="x", pady=5)
        
        # Target accounts
        targets_row = ttk.Frame(targets_section)
        targets_row.pack(fill="x", pady=2)
        ttk.Label(targets_row, text="Target Accounts:", width=15).pack(side="left")
        self.targets_var = tk.StringVar(value="deadmau5,skrillex,housemusic")
        targets_entry = ttk.Entry(targets_row, textvariable=self.targets_var, width=40)
        targets_entry.pack(side="right")
        
        # Help text
        help_text = ttk.Label(targets_section, 
                             text="💡 Tip: Choose accounts with engaged followers in your niche",
                             font=("SF Pro Display", 10), foreground="gray")
        help_text.pack(pady=5)
        
        # Save button
        save_row = ttk.Frame(self.settings_frame)
        save_row.pack(fill="x", pady=10)
        
        ttk.Button(save_row, text="💾 Save Configuration", 
                  command=self.save_settings).pack()
        
    def toggle_settings(self):
        """Show/hide settings panel"""
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(fill="x", padx=20, pady=10)
            self.settings_visible = True
    
    def start_automation(self):
        """Start the autonomous automation"""
        if not self.validate_settings():
            messagebox.showerror("Configuration Required", 
                               "Please configure your Instagram username, password, and target accounts first.")
            self.toggle_settings()
            return
        
        global automation_running
        if automation_running:
            messagebox.showinfo("Already Running", "Bot is already running autonomously!")
            return
        
        # Update UI
        automation_running = True
        self.status_text.set("🟢 Running autonomously")
        self.start_button.config(state="disabled")
        
        # Start automation thread
        threading.Thread(target=self.run_automation, daemon=True).start()
        
        # Show success message
        messagebox.showinfo("Bot Started!", 
                           "✅ Instagram Bot is now running autonomously!\\n\\n"
                           "💡 You can close this window and the bot will continue running in the background.\\n"
                           "👆 Click the dock icon anytime to check progress.")
        
    def stop_automation(self):
        """Stop the automation"""
        global automation_running
        automation_running = False
        self.status_text.set("⚪ Stopped")
        self.start_button.config(state="normal")
        
    def run_automation(self):
        """Run the actual automation loop"""
        try:
            # Import and setup the actual Instagram automation
            from instagram_gui import InstagramAutomationGUI
            
            # Create hidden automation window
            automation_root = tk.Tk()
            automation_root.withdraw()
            
            # Create automation instance
            automation = InstagramAutomationGUI(automation_root)
            
            # Apply our settings
            automation.username_var.set(self.username_var.get())
            automation.password_var.set(self.password_var.get())
            automation.target_accounts_var.set(self.targets_var.get())
            
            # Start the scheduler
            automation.toggle_scheduler()
            
            global automation_running, last_activity
            while automation_running:
                automation_root.update()
                last_activity = datetime.now().strftime("%H:%M")
                time.sleep(1)
                
        except Exception as e:
            global automation_running
            automation_running = False
            self.status_text.set("🔴 Error occurred")
            messagebox.showerror("Automation Error", f"An error occurred: {str(e)}")
            
    def validate_settings(self):
        """Check if required settings are configured"""
        return (self.username_var.get().strip() and 
                self.password_var.get().strip() and 
                self.targets_var.get().strip())
    
    def save_settings(self):
        """Save configuration to file"""
        self.settings = {
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "target_accounts": self.targets_var.get(),
            "saved_at": datetime.now().isoformat()
        }
        
        try:
            with open('autonomous_bot_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
            messagebox.showinfo("Settings Saved", "✅ Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save settings: {e}")
    
    def load_settings(self):
        """Load configuration from file"""
        try:
            settings_file = Path('autonomous_bot_settings.json')
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
                
                # Apply loaded settings
                self.username_var.set(self.settings.get("username", ""))
                self.password_var.set(self.settings.get("password", ""))
                self.targets_var.set(self.settings.get("target_accounts", "deadmau5,skrillex,housemusic"))
                
        except Exception as e:
            print(f"⚠️ Could not load settings: {e}")
    
    def start_status_updates(self):
        """Start periodic status updates"""
        self.update_stats()
        self.root.after(10000, self.start_status_updates)  # Update every 10 seconds
    
    def update_stats(self):
        """Update statistics display"""
        try:
            # Load stats from bot data files
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows_data = json.load(f)
                    total_follows = len(follows_data)
                    self.total_follows.set(f"Follows: {total_follows}")
            
            # Update last activity
            global last_activity
            if last_activity:
                self.last_activity.set(f"Last activity: {last_activity}")
                
        except Exception as e:
            print(f"⚠️ Stats update error: {e}")
    
    def show_stats(self):
        """Show detailed statistics window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Instagram Bot Statistics")
        stats_window.geometry("600x450")
        
        # Create scrollable text area
        text_frame = ttk.Frame(stats_window, padding="15")
        text_frame.pack(fill="both", expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SF Mono", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generate stats content
        stats_content = self.generate_stats_report()
        text_area.insert(tk.END, stats_content)
        text_area.config(state=tk.DISABLED)
    
    def generate_stats_report(self):
        """Generate detailed statistics report"""
        report = "📊 INSTAGRAM BOT - DETAILED STATISTICS\\n"
        report += "=" * 50 + "\\n\\n"
        
        try:
            # Account summary
            report += "📱 ACCOUNT OVERVIEW\\n"
            report += f"Username: {self.username_var.get() or 'Not configured'}\\n"
            report += f"Target Accounts: {self.targets_var.get() or 'Not configured'}\\n\\n"
            
            # Follow statistics
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows_data = json.load(f)
                
                total_follows = len(follows_data)
                following = sum(1 for user in follows_data.values() 
                               if user.get('status') == 'following')
                unfollowed = sum(1 for user in follows_data.values() 
                               if user.get('status') == 'unfollowed')
                
                report += "📈 FOLLOW STATISTICS\\n"
                report += f"Total users followed: {total_follows}\\n"
                report += f"Currently following: {following}\\n"
                report += f"Previously unfollowed: {unfollowed}\\n\\n"
            
            # Recent activity
            if Path('instagram_data/action_log.json').exists():
                with open('instagram_data/action_log.json', 'r') as f:
                    action_log = json.load(f)
                
                if action_log:
                    report += "🕐 RECENT ACTIVITY (Last 10 actions)\\n"
                    recent = sorted(action_log, key=lambda x: x['timestamp'])[-10:]
                    
                    for action in recent:
                        timestamp = action['timestamp'][:16].replace('T', ' ')
                        report += f"{timestamp}: {action['action']} @{action['target']}\\n"
                    report += "\\n"
            
            # Bot status
            global automation_running
            report += "🤖 BOT STATUS\\n"
            report += f"Currently running: {'Yes' if automation_running else 'No'}\\n"
            report += f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
            
        except Exception as e:
            report += f"❌ Error generating report: {e}\\n"
        
        return report
    
    def hide_to_background(self):
        """Hide window but keep app running"""
        global app_should_quit
        if not app_should_quit:
            self.root.withdraw()
            print("🔽 App minimized to background - continues running")
        else:
            self.quit_application()
    
    def show_window(self):
        """Show the app window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_application(self):
        """Quit the application completely"""
        global app_should_quit, automation_running
        app_should_quit = True
        automation_running = False
        self.root.quit()

def main():
    """Main application entry point"""
    try:
        # Create main window
        root = tk.Tk()
        handle_signals.root = root
        
        # Set window icon if available
        try:
            if Path('app_icon.png').exists():
                icon_img = tk.PhotoImage(file='app_icon.png')
                root.iconphoto(True, icon_img)
        except:
            pass
        
        # Create the autonomous bot app
        app = AutonomousInstagramBot(root)
        
        # Position window
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 650) // 2
        y = (root.winfo_screenheight() - 550) // 2
        root.geometry(f"650x550+{x}+{y}")
        
        print("🚀 Instagram Bot - Autonomous Mode")
        print("📱 Configure your settings and click 'Start Bot'")
        print("🔽 Close window to run in background")
        print("👆 Click dock icon to reopen anytime")
        print("⌘Q to quit completely")
        
        # Start the app
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''

def create_enhanced_app_bundle():
    """Create the enhanced autonomous app bundle"""
    app_name = "Instagram Bot"
    bundle_name = f"{app_name}.app"
    bundle_path = Path(bundle_name)
    
    print(f"🚀 Creating Autonomous Instagram Bot App...")
    
    # Remove existing bundle
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    
    # Create bundle structure
    contents = bundle_path / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    for dir_path in [contents, macos, resources]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create enhanced Info.plist
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
        "NSRequiresAquaSystemAppearance": False,
        "LSUIElement": False,
        "NSHumanReadableCopyright": "© 2024 Instagram Bot - Autonomous Growth",
        "CFBundleDocumentTypes": [],
        "NSApplication": {
            "NSMainNibFile": "",
            "NSPrincipalClass": "NSApplication"
        }
    }
    
    # Write Info.plist
    with open(contents / "Info.plist", 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Create main executable
    main_script = create_autonomous_main_script()
    executable_path = macos / "Instagram Bot"
    
    with open(executable_path, 'w') as f:
        f.write(main_script)
    
    os.chmod(executable_path, 0o755)
    
    # Handle icon
    icon_path = create_professional_icon()
    if icon_path:
        try:
            icns_path = resources / "AppIcon.icns"
            subprocess.run(['sips', '-s', 'format', 'icns', icon_path, '--out', str(icns_path)], 
                          capture_output=True)
            if icns_path.exists():
                print("✅ App icon converted to ICNS")
            else:
                shutil.copy2(icon_path, resources / "AppIcon.png")
        except:
            pass
    
    print(f"✅ Enhanced app bundle created: {bundle_path}")
    return bundle_path

def create_installer():
    """Create installer script for Applications folder"""
    installer_script = f'''#!/bin/bash
# Instagram Bot - Applications Installer

APP_NAME="Instagram Bot.app"
CURRENT_DIR="{Path.cwd()}"
APPLICATIONS="/Applications"

echo "📱 Installing Instagram Bot to Applications folder..."

if [ ! -d "$CURRENT_DIR/$APP_NAME" ]; then
    echo "❌ $APP_NAME not found"
    exit 1
fi

# Install to Applications
echo "📦 Installing to $APPLICATIONS..."
if cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS/" 2>/dev/null; then
    echo "✅ Installed successfully"
else
    echo "🔐 Requesting permission..."
    sudo cp -R "$CURRENT_DIR/$APP_NAME" "$APPLICATIONS/"
    if [ $? -eq 0 ]; then
        echo "✅ Installed successfully"
        sudo chmod -R 755 "$APPLICATIONS/$APP_NAME"
    else
        echo "❌ Installation failed"
        exit 1
    fi
fi

echo ""
echo "🎉 Installation Complete!"
echo "📱 Instagram Bot is now available in:"
echo "   • Applications folder"
echo "   • Launchpad"
echo "   • Spotlight search"
echo ""

read -p "🚀 Launch Instagram Bot now? (y/n): " launch
if [[ $launch =~ ^[Yy]$ ]]; then
    open "$APPLICATIONS/$APP_NAME"
    echo "✅ Launched!"
fi
'''
    
    installer_path = Path("install_to_applications.sh")
    with open(installer_path, 'w') as f:
        f.write(installer_script)
    
    os.chmod(installer_path, 0o755)
    print(f"✅ Installer created: {installer_path}")
    return installer_path

def main():
    """Main creation function"""
    print("🤖 Creating Autonomous Instagram Bot for macOS")
    print("=" * 60)
    
    if sys.platform != 'darwin':
        print("❌ This script is for macOS only")
        sys.exit(1)
    
    if not Path('instagram_gui.py').exists():
        print("❌ instagram_gui.py not found!")
        sys.exit(1)
    
    try:
        # Try to install Pillow for better icons
        try:
            from PIL import Image
        except ImportError:
            print("📦 Installing Pillow for professional icons...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], 
                          capture_output=True)
        
        # Create the app
        bundle_path = create_enhanced_app_bundle()
        installer_path = create_installer()
        
        print("\n🎉 Autonomous Instagram Bot Created!")
        print("=" * 60)
        print(f"📱 App: {bundle_path}")
        print(f"🚀 Installer: {installer_path}")
        print("")
        print("🤖 Features:")
        print("  • Set-it-and-forget-it autonomous operation")
        print("  • Professional macOS integration")
        print("  • Background operation with dock icon")
        print("  • Simple periodic check-ins")
        print("  • No technical knowledge required")
        print("")
        print("🔹 Next Steps:")
        print("  1. Run installer: ./install_to_applications.sh")
        print("  2. Launch from Applications folder")
        print("  3. Configure Instagram credentials")
        print("  4. Click 'Start Bot' for autonomous operation")
        print("  5. Close window - bot continues in background")
        
        # Offer installation
        response = input("\n🚀 Install to Applications now? (y/n): ").lower()
        if response in ['y', 'yes', '']:
            subprocess.run(['bash', str(installer_path)])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 