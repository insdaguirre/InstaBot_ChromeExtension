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
    """Create a professional app icon"""
    try:
        # Create icon using PIL if available
        icon_code = '''
from PIL import Image, ImageDraw
import math

# Create 512x512 icon with Instagram-style gradient
size = 512
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Create gradient background
center = size // 2
max_radius = size // 2

# Gradient from purple to orange
for r in range(max_radius, 0, -2):
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

# Add robot symbol
robot_size = size // 3
# Robot head
head_radius = robot_size // 4
head_color = (255, 255, 255, 230)
draw.ellipse([center - head_radius, center - head_radius - robot_size//8,
              center + head_radius, center + head_radius - robot_size//8],
             fill=head_color)

# Robot body
body_width = robot_size // 3
body_height = robot_size // 3
body_top = center - robot_size//16
draw.rounded_rectangle([center - body_width//2, body_top,
                       center + body_width//2, body_top + body_height],
                      radius=15, fill=head_color)

# Eyes
eye_size = 8
eye_y = center - head_radius + 15
eye_color = (80, 80, 80, 255)
draw.ellipse([center - 20 - eye_size//2, eye_y - eye_size//2,
              center - 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)
draw.ellipse([center + 20 - eye_size//2, eye_y - eye_size//2,
              center + 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)

# Antenna
antenna_top = center - head_radius - robot_size//8 - 20
draw.line([center, center - head_radius - robot_size//8,
           center, antenna_top], fill=head_color, width=4)
draw.ellipse([center-6, antenna_top-6, center+6, antenna_top+6], fill=head_color)

img.save('bot_icon.png')
print("✅ Professional icon created")
'''
        
        try:
            exec(icon_code)
            if Path('bot_icon.png').exists():
                return 'bot_icon.png'
        except ImportError:
            print("⚠️ PIL not available, creating simple icon...")
            
        # Fallback: create basic icon
        fallback_code = '''
from PIL import Image, ImageDraw
img = Image.new('RGBA', (512, 512), (131, 58, 180, 255))
draw = ImageDraw.Draw(img)
# Simple robot shape
draw.rectangle([156, 156, 356, 356], fill=(255, 255, 255, 200))
draw.ellipse([206, 180, 306, 280], fill=(80, 80, 80))
img.save('bot_icon.png')
'''
        exec(fallback_code)
        return 'bot_icon.png'
        
    except Exception as e:
        print(f"⚠️ Icon creation failed: {e}")
        return None

def create_autonomous_app_script():
    """Create the main autonomous app script"""
    return '''#!/usr/bin/env python3
"""
Instagram Bot - Autonomous macOS Application
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

# App setup
app_dir = Path(__file__).parent.parent.parent
os.chdir(app_dir)
sys.path.insert(0, str(app_dir))

app_should_quit = False
automation_running = False

def handle_signals(signum, frame):
    global app_should_quit
    if signum == signal.SIGUSR1:
        if hasattr(handle_signals, 'root'):
            handle_signals.root.deiconify()
            handle_signals.root.lift()
    elif signum == signal.SIGUSR2:
        app_should_quit = True
        if hasattr(handle_signals, 'root'):
            handle_signals.root.quit()

signal.signal(signal.SIGUSR1, handle_signals)
signal.signal(signal.SIGUSR2, handle_signals)

class AutonomousInstagramBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Instagram Bot - Autonomous")
        self.root.geometry("650x550")
        
        # macOS integration
        self.root.createcommand('tk::mac::ReopenDocument', self.show_window)
        self.root.createcommand('tk::mac::Quit', self.quit_app)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.settings = {}
        self.setup_ui()
        self.load_settings()
        self.start_updates()
        
    def setup_ui(self):
        # Header
        header = ttk.Frame(self.root, padding="20")
        header.pack(fill="x")
        
        ttk.Label(header, text="🤖 Instagram Bot", 
                 font=("SF Pro Display", 28, "bold")).pack()
        ttk.Label(header, text="Autonomous Instagram Growth • Set it and forget it",
                 font=("SF Pro Display", 12), foreground="gray").pack()
        
        # Status Panel
        status_frame = ttk.LabelFrame(self.root, text="📊 Bot Status", padding="20")
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_text = tk.StringVar(value="⚪ Ready to start")
        ttk.Label(status_frame, textvariable=self.status_text, 
                 font=("SF Pro Display", 16, "bold")).pack()
        
        # Stats
        stats_grid = ttk.Frame(status_frame)
        stats_grid.pack(fill="x", pady=15)
        
        today_frame = ttk.Frame(stats_grid)
        today_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(today_frame, text="📈 Today", font=("SF Pro Display", 12, "bold")).pack()
        self.today_follows = tk.StringVar(value="Follows: 0")
        ttk.Label(today_frame, textvariable=self.today_follows).pack()
        
        total_frame = ttk.Frame(stats_grid)
        total_frame.pack(side="right", fill="x", expand=True)
        ttk.Label(total_frame, text="🎯 Total", font=("SF Pro Display", 12, "bold")).pack()
        self.total_follows = tk.StringVar(value="Follows: 0")
        self.last_activity = tk.StringVar(value="Last: Never")
        ttk.Label(total_frame, textvariable=self.total_follows).pack()
        ttk.Label(total_frame, textvariable=self.last_activity).pack()
        
        # Controls
        control_frame = ttk.LabelFrame(self.root, text="🎛️ Quick Actions", padding="20")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        button_row = ttk.Frame(control_frame)
        button_row.pack()
        
        self.start_btn = ttk.Button(button_row, text="▶️ Start Bot", 
                                   command=self.start_automation,
                                   style="Accent.TButton")
        self.start_btn.pack(side="left", padx=5)
        
        ttk.Button(button_row, text="⏸️ Stop", command=self.stop_automation).pack(side="left", padx=5)
        ttk.Button(button_row, text="📊 Stats", command=self.show_stats).pack(side="left", padx=5)
        ttk.Button(button_row, text="⚙️ Settings", command=self.toggle_settings).pack(side="left", padx=5)
        
        # Settings Panel
        self.settings_frame = ttk.LabelFrame(self.root, text="⚙️ Configuration", padding="20")
        self.settings_visible = False
        
        # Username
        user_row = ttk.Frame(self.settings_frame)
        user_row.pack(fill="x", pady=2)
        ttk.Label(user_row, text="Username:", width=12).pack(side="left")
        self.username_var = tk.StringVar()
        ttk.Entry(user_row, textvariable=self.username_var, width=25).pack(side="right")
        
        # Password
        pass_row = ttk.Frame(self.settings_frame)
        pass_row.pack(fill="x", pady=2)
        ttk.Label(pass_row, text="Password:", width=12).pack(side="left")
        self.password_var = tk.StringVar()
        ttk.Entry(pass_row, textvariable=self.password_var, show="*", width=25).pack(side="right")
        
        # Targets
        target_row = ttk.Frame(self.settings_frame)
        target_row.pack(fill="x", pady=2)
        ttk.Label(target_row, text="Target Accounts:", width=15).pack(side="left")
        self.targets_var = tk.StringVar(value="deadmau5,skrillex,housemusic")
        ttk.Entry(target_row, textvariable=self.targets_var, width=40).pack(side="right")
        
        ttk.Button(self.settings_frame, text="💾 Save", command=self.save_settings).pack(pady=10)
        
        # Footer
        footer = ttk.Frame(self.root, padding="10")
        footer.pack(fill="x", side="bottom")
        ttk.Label(footer, text="💡 Close window = background mode • ⌘Q = quit",
                 font=("SF Pro Display", 10), foreground="gray").pack()
    
    def toggle_settings(self):
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(fill="x", padx=20, pady=10)
            self.settings_visible = True
    
    def start_automation(self):
        if not self.validate_settings():
            messagebox.showerror("Setup Required", 
                               "Please configure username, password, and target accounts.")
            self.toggle_settings()
            return
        
        global automation_running
        if automation_running:
            return
        
        automation_running = True
        self.status_text.set("🟢 Running autonomously")
        self.start_btn.config(state="disabled")
        
        threading.Thread(target=self.run_automation, daemon=True).start()
        
        messagebox.showinfo("Bot Started!", 
                           "✅ Instagram Bot is now running!\\n\\n"
                           "You can close this window and it will continue in the background.")
    
    def stop_automation(self):
        global automation_running
        automation_running = False
        self.status_text.set("⚪ Stopped")
        self.start_btn.config(state="normal")
    
    def run_automation(self):
        try:
            from instagram_gui import InstagramAutomationGUI
            
            automation_root = tk.Tk()
            automation_root.withdraw()
            
            automation = InstagramAutomationGUI(automation_root)
            automation.username_var.set(self.username_var.get())
            automation.password_var.set(self.password_var.get())
            automation.target_accounts_var.set(self.targets_var.get())
            
            automation.toggle_scheduler()
            
            global automation_running
            while automation_running:
                automation_root.update()
                time.sleep(1)
                
        except Exception as e:
            global automation_running
            automation_running = False
            self.status_text.set("🔴 Error")
            messagebox.showerror("Error", f"Automation error: {e}")
    
    def validate_settings(self):
        return (self.username_var.get().strip() and 
                self.password_var.get().strip() and 
                self.targets_var.get().strip())
    
    def save_settings(self):
        settings = {
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "target_accounts": self.targets_var.get()
        }
        
        try:
            with open('autonomous_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Saved", "Settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def load_settings(self):
        try:
            if Path('autonomous_settings.json').exists():
                with open('autonomous_settings.json', 'r') as f:
                    settings = json.load(f)
                self.username_var.set(settings.get("username", ""))
                self.password_var.set(settings.get("password", ""))
                self.targets_var.set(settings.get("target_accounts", "deadmau5,skrillex,housemusic"))
        except:
            pass
    
    def start_updates(self):
        self.update_stats()
        self.root.after(10000, self.start_updates)
    
    def update_stats(self):
        try:
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows = json.load(f)
                    self.total_follows.set(f"Follows: {len(follows)}")
        except:
            pass
    
    def show_stats(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistics")
        stats_window.geometry("600x400")
        
        text_area = tk.Text(stats_window, wrap=tk.WORD, font=("SF Mono", 11))
        text_area.pack(fill="both", expand=True, padx=15, pady=15)
        
        stats_content = "📊 INSTAGRAM BOT STATISTICS\\n" + "="*50 + "\\n\\n"
        
        try:
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows = json.load(f)
                stats_content += f"Total follows: {len(follows)}\\n"
                following = sum(1 for u in follows.values() if u.get('status') == 'following')
                stats_content += f"Currently following: {following}\\n\\n"
            
            if Path('instagram_data/action_log.json').exists():
                with open('instagram_data/action_log.json', 'r') as f:
                    actions = json.load(f)
                    recent = sorted(actions, key=lambda x: x['timestamp'])[-10:]
                    stats_content += "Recent activity:\\n"
                    for action in recent:
                        timestamp = action['timestamp'][:16].replace('T', ' ')
                        stats_content += f"{timestamp}: {action['action']} @{action['target']}\\n"
        except:
            stats_content += "No data available yet\\n"
        
        text_area.insert(tk.END, stats_content)
        text_area.config(state=tk.DISABLED)
    
    def hide_window(self):
        global app_should_quit
        if not app_should_quit:
            self.root.withdraw()
        else:
            self.quit_app()
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def quit_app(self):
        global app_should_quit, automation_running
        app_should_quit = True
        automation_running = False
        self.root.quit()

def main():
    try:
        root = tk.Tk()
        handle_signals.root = root
        
        if Path('bot_icon.png').exists():
            try:
                icon = tk.PhotoImage(file='bot_icon.png')
                root.iconphoto(True, icon)
            except:
                pass
        
        app = AutonomousInstagramBot(root)
        
        root.update_idletasks()
        x = (root.winfo_screenwidth() - 650) // 2
        y = (root.winfo_screenheight() - 550) // 2
        root.geometry(f"650x550+{x}+{y}")
        
        print("🚀 Instagram Bot - Autonomous Mode")
        print("Configure settings and click 'Start Bot'")
        print("Close window to run in background")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''

def create_app_bundle():
    """Create the app bundle"""
    app_name = "Instagram Bot"
    bundle_name = f"{app_name}.app"
    bundle_path = Path(bundle_name)
    
    print(f"🚀 Creating {bundle_name}...")
    
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    
    # Create structure
    contents = bundle_path / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    
    for dir_path in [contents, macos, resources]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Info.plist
    info_plist = {
        "CFBundleName": app_name,
        "CFBundleDisplayName": "Instagram Bot",
        "CFBundleIdentifier": "com.instagrambot.autonomous",
        "CFBundleVersion": "2.0.0",
        "CFBundleShortVersionString": "2.0.0", 
        "CFBundleExecutable": "Instagram Bot",
        "CFBundleIconFile": "AppIcon.icns",
        "CFBundlePackageType": "APPL",
        "LSMinimumSystemVersion": "10.15.0",
        "NSHighResolutionCapable": True,
        "LSUIElement": False,
        "NSHumanReadableCopyright": "© 2024 Instagram Bot"
    }
    
    with open(contents / "Info.plist", 'wb') as f:
        plistlib.dump(info_plist, f)
    
    # Executable
    main_script = create_autonomous_app_script()
    executable_path = macos / "Instagram Bot"
    
    with open(executable_path, 'w') as f:
        f.write(main_script)
    
    os.chmod(executable_path, 0o755)
    
    # Icon
    icon_path = create_professional_icon()
    if icon_path:
        try:
            icns_path = resources / "AppIcon.icns"
            subprocess.run(['sips', '-s', 'format', 'icns', icon_path, '--out', str(icns_path)], 
                          capture_output=True)
            if not icns_path.exists():
                shutil.copy2(icon_path, resources / "AppIcon.png")
        except:
            pass
    
    print(f"✅ Created: {bundle_path}")
    return bundle_path

def create_installer():
    """Create installer script"""
    script = f'''#!/bin/bash
APP_NAME="Instagram Bot.app"
APPLICATIONS="/Applications"

echo "📱 Installing Instagram Bot..."

if [ ! -d "{Path.cwd()}/$APP_NAME" ]; then
    echo "❌ App not found"
    exit 1
fi

if cp -R "{Path.cwd()}/$APP_NAME" "$APPLICATIONS/" 2>/dev/null; then
    echo "✅ Installed to Applications"
else
    sudo cp -R "{Path.cwd()}/$APP_NAME" "$APPLICATIONS/"
    sudo chmod -R 755 "$APPLICATIONS/$APP_NAME"
    echo "✅ Installed to Applications (with admin permission)"
fi

echo ""
echo "🎉 Installation Complete!"
echo "Find 'Instagram Bot' in Applications folder"

read -p "Launch now? (y/n): " launch
if [[ $launch =~ ^[Yy]$ ]]; then
    open "$APPLICATIONS/$APP_NAME"
fi
'''
    
    installer_path = Path("install_app.sh")
    with open(installer_path, 'w') as f:
        f.write(script)
    os.chmod(installer_path, 0o755)
    return installer_path

def main():
    """Main function"""
    print("🤖 Creating Autonomous Instagram Bot for macOS")
    print("=" * 50)
    
    if sys.platform != 'darwin':
        print("❌ macOS only")
        sys.exit(1)
    
    if not Path('instagram_gui.py').exists():
        print("❌ instagram_gui.py not found")
        sys.exit(1)
    
    try:
        # Install PIL if needed
        try:
            from PIL import Image
        except ImportError:
            print("📦 Installing Pillow...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'Pillow'], 
                          capture_output=True)
        
        # Create app
        bundle_path = create_app_bundle()
        installer_path = create_installer()
        
        print("\n🎉 Autonomous Instagram Bot Created!")
        print("=" * 50)
        print(f"📱 App: {bundle_path}")
        print(f"🚀 Installer: {installer_path}")
        print("")
        print("Features:")
        print("• Autonomous operation - set it and forget it")
        print("• Runs in background when window closed")
        print("• Simple configuration and monitoring")
        print("• Professional macOS integration")
        print("")
        print("Usage:")
        print("1. Install to Applications folder")
        print("2. Configure Instagram credentials")
        print("3. Click 'Start Bot'")
        print("4. Close window - continues in background")
        print("5. Click dock icon to check progress")
        
        response = input("\n🚀 Install to Applications now? (y/n): ").lower()
        if response in ['y', 'yes', '']:
            subprocess.run(['bash', str(installer_path)])
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 