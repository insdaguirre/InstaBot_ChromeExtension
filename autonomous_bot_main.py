#!/usr/bin/env python3
"""
Instagram Bot - Autonomous macOS Application
Professional autonomous Instagram growth tool - Set it and forget it!
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import signal
import threading
import time
import json
import random
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
    """Handle macOS app signals for show/hide/quit"""
    global app_should_quit
    if signum == signal.SIGUSR1:
        # Show window signal
        if hasattr(handle_signals, 'root') and handle_signals.root:
            try:
                handle_signals.root.deiconify()
                handle_signals.root.lift()
                handle_signals.root.focus_force()
                print("🔼 App restored from dock click")
            except Exception as e:
                print(f"⚠️ Error restoring window: {e}")
    elif signum == signal.SIGUSR2:
        # Quit app signal
        app_should_quit = True
        if hasattr(handle_signals, 'root') and handle_signals.root:
            try:
                handle_signals.root.quit()
                print("👋 App quit from dock")
            except Exception as e:
                print(f"⚠️ Error quitting app: {e}")

# Set up signal handlers for macOS integration
try:
    signal.signal(signal.SIGUSR1, handle_signals)
    signal.signal(signal.SIGUSR2, handle_signals)
    print("🔧 macOS signal handlers configured")
except Exception as e:
    print(f"⚠️ Could not set up signal handlers: {e}")

class AutonomousInstagramBot:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Instagram Bot - Autonomous Mode")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # Configure modern styling
        self.setup_styles()
        
        # Enhanced macOS integration - make it behave like a proper Mac app
        try:
            # Handle dock icon clicks and app restoration
            self.root.createcommand('tk::mac::ReopenDocument', self.show_window)
            self.root.createcommand('tk::mac::Quit', self.quit_application)
            
            # Handle window close button (hide to background instead of quit)
            self.root.protocol("WM_DELETE_WINDOW", self.hide_to_background)
            
            # Set proper app focus behavior
            self.root.lift()
            self.root.focus_force()
            
            # Configure for proper dock integration
            self.root.wm_attributes('-modified', False)
            
            print("🍎 macOS integration configured successfully")
        except Exception as e:
            print(f"⚠️ macOS integration setup failed: {e}")
            # Fallback - still set essential handlers
            self.root.protocol("WM_DELETE_WINDOW", self.hide_to_background)
        
        # App state
        self.settings = {}
        self.stats = {"daily_follows": 0, "daily_unfollows": 0, "total_follows": 0}
        self.password_visible = False
        
        # Setup UI and load data
        self.setup_ui()
        self.load_settings()
        self.start_status_updates()
        
        print("🤖 Autonomous Instagram Bot initialized")
        
    def setup_styles(self):
        """Configure modern UI styling"""
        style = ttk.Style()
        
        # Configure modern button styles - using built-in styles
        style.configure('Accent.TButton', 
                       font=('SF Pro Display', 12, 'bold'))
        
        # Use default styles for other elements
        
    def setup_ui(self):
        """Create the modern autonomous-focused user interface with scrollable content"""
        
        # Create main scrollable container
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollable elements
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Cross-platform mouse wheel binding
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)  # Windows/Linux
            widget.bind("<Button-4>", lambda e: self.main_canvas.yview_scroll(-1, "units"))  # Linux
            widget.bind("<Button-5>", lambda e: self.main_canvas.yview_scroll(1, "units"))   # Linux
        
        # Bind mousewheel to canvas and all child widgets
        bind_mousewheel(self.main_canvas)
        bind_mousewheel(self.scrollable_frame)
        
        # Update canvas scroll region when window size changes
        def configure_canvas(event):
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.main_canvas.bind('<Configure>', configure_canvas)
        
        # Main content container with padding inside scrollable frame
        main_container = ttk.Frame(self.scrollable_frame, padding="30")
        main_container.pack(fill="both", expand=True)
        
        # Header Section with modern styling
        self.create_modern_header(main_container)
        
        # Status Dashboard with enhanced design
        self.create_enhanced_status_dashboard(main_container)
        
        # Quick Action Controls with modern buttons
        self.create_modern_action_controls(main_container)
        
        # Enhanced Settings Panel (always accessible via scrolling)
        self.create_enhanced_settings_panel(main_container)
        
        # Modern Footer
        self.create_modern_footer(main_container)
        
        # Initial scroll region setup
        self.root.after(100, lambda: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        
    def create_modern_header(self, parent):
        """Create modern header section"""
        header = ttk.Frame(parent, padding="0 0 20 0")
        header.pack(fill="x")
        
        # Robot emoji and title
        title_frame = ttk.Frame(header)
        title_frame.pack()
        
        title = ttk.Label(title_frame, text="🤖 Instagram Bot", 
                         font=("SF Pro Display", 36, "bold"))
        title.pack()
        
        subtitle = ttk.Label(title_frame, text="Autonomous Instagram Growth • Set it and forget it",
                           font=("SF Pro Display", 14), foreground="#666666")
        subtitle.pack(pady=(5, 0))
        
        # Separator line
        separator = ttk.Separator(header, orient='horizontal')
        separator.pack(fill='x', pady=(15, 0))
        
    def create_enhanced_status_dashboard(self, parent):
        """Create enhanced status dashboard with modern design"""
        dashboard_frame = ttk.LabelFrame(parent, text="📊 Bot Status Dashboard", 
                                        padding="25")
        dashboard_frame.pack(fill="x", pady=(20, 15))
        
        # Status indicator with modern styling
        status_container = ttk.Frame(dashboard_frame)
        status_container.pack(fill="x", pady=(0, 20))
        
        self.status_text = tk.StringVar(value="⚪ Ready to start autonomous operation")
        status_label = ttk.Label(status_container, textvariable=self.status_text, 
                                font=("SF Pro Display", 18, "bold"),
                                foreground="#2563eb")
        status_label.pack()
        
        # Enhanced Statistics Grid with cards
        stats_container = ttk.Frame(dashboard_frame)
        stats_container.pack(fill="x")
        
        # Today's Activity Card
        today_card = ttk.LabelFrame(stats_container, text="📈 Today's Activity", 
                                   padding="15")
        today_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.today_follows = tk.StringVar(value="New Follows: 0")
        self.today_unfollows = tk.StringVar(value="Unfollows: 0")
        
        ttk.Label(today_card, textvariable=self.today_follows, 
                 font=("SF Pro Display", 12)).pack(anchor="w", pady=2)
        ttk.Label(today_card, textvariable=self.today_unfollows, 
                 font=("SF Pro Display", 12)).pack(anchor="w", pady=2)
        
        # All Time Stats Card
        total_card = ttk.LabelFrame(stats_container, text="🎯 All Time Stats", 
                                   padding="15")
        total_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.total_follows = tk.StringVar(value="Total Follows: 0")
        self.last_activity = tk.StringVar(value="Last Activity: Never")
        
        ttk.Label(total_card, textvariable=self.total_follows, 
                 font=("SF Pro Display", 12)).pack(anchor="w", pady=2)
        ttk.Label(total_card, textvariable=self.last_activity, 
                 font=("SF Pro Display", 12)).pack(anchor="w", pady=2)
        
    def create_modern_action_controls(self, parent):
        """Create modern action control buttons"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Bot Controls", 
                                      padding="25")
        control_frame.pack(fill="x", pady=(15, 15))
        
        # Button container with proper spacing
        button_container = ttk.Frame(control_frame)
        button_container.pack()
        
        # Modern action buttons with enhanced styling
        self.start_button = ttk.Button(button_container, text="▶️ Start Autonomous Mode", 
                                      command=self.start_automation,
                                      style="Accent.TButton",
                                      width=20)
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_container, text="⏸️ Stop Bot", 
                                     command=self.stop_automation,
                                     width=12)
        self.stop_button.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_container, text="📊 Detailed Stats", 
                  command=self.show_detailed_stats,
                  width=14).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_container, text="⚙️ Configuration", 
                  command=self.toggle_settings,
                  width=14).pack(side="left")
        
    def create_enhanced_settings_panel(self, parent):
        """Create enhanced settings configuration panel"""
        self.settings_frame = ttk.LabelFrame(parent, text="⚙️ Bot Configuration", 
                                           padding="25")
        self.settings_visible = False
        
        # Instagram Account Credentials Section
        creds_section = ttk.LabelFrame(self.settings_frame, text="Instagram Account", 
                                     padding="20")
        creds_section.pack(fill="x", pady=(0, 15))
        
        # Username field
        user_frame = ttk.Frame(creds_section)
        user_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(user_frame, text="Username:", font=("SF Pro Display", 12, "bold")).pack(anchor="w")
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var, 
                                  width=50, font=("SF Pro Display", 12))
        username_entry.pack(fill="x", pady=(5, 0))
        
        # Password field with show/hide toggle
        pass_frame = ttk.Frame(creds_section)
        pass_frame.pack(fill="x", pady=(0, 10))
        
        pass_label_frame = ttk.Frame(pass_frame)
        pass_label_frame.pack(fill="x")
        ttk.Label(pass_label_frame, text="Password:", font=("SF Pro Display", 12, "bold")).pack(side="left")
        
        self.show_password_var = tk.BooleanVar()
        self.show_password_btn = ttk.Checkbutton(pass_label_frame, text="Show password", 
                                                variable=self.show_password_var,
                                                command=self.toggle_password_visibility)
        self.show_password_btn.pack(side="right")
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(pass_frame, textvariable=self.password_var, 
                                       show="*", width=50, font=("SF Pro Display", 12))
        self.password_entry.pack(fill="x", pady=(5, 0))
        
        # Growth Strategy Section
        strategy_section = ttk.LabelFrame(self.settings_frame, text="Growth Strategy", 
                                        padding="20")
        strategy_section.pack(fill="x", pady=(0, 15))
        
        # Target accounts field
        targets_frame = ttk.Frame(strategy_section)
        targets_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(targets_frame, text="Target Accounts:", font=("SF Pro Display", 12, "bold")).pack(anchor="w")
        self.targets_var = tk.StringVar(value="deadmau5,skrillex,housemusic")
        targets_entry = ttk.Entry(targets_frame, textvariable=self.targets_var, 
                                 width=50, font=("SF Pro Display", 12))
        targets_entry.pack(fill="x", pady=(5, 0))
        
        ttk.Label(targets_frame, 
                 text="💡 Tip: Choose accounts with engaged followers in your niche (comma-separated)",
                 font=("SF Pro Display", 10), foreground="gray").pack(anchor="w", pady=(5, 0))
        
        # Enhanced Follow Range Section
        range_section = ttk.LabelFrame(strategy_section, text="Follow Range Per Account", 
                                     padding="15")
        range_section.pack(fill="x", pady=(0, 15))
        
        range_frame = ttk.Frame(range_section)
        range_frame.pack(fill="x")
        
        # Min followers
        min_frame = ttk.Frame(range_frame)
        min_frame.pack(side="left", fill="x", expand=True, padx=(0, 15))
        ttk.Label(min_frame, text="Minimum per account:", font=("SF Pro Display", 12, "bold")).pack(anchor="w")
        self.min_follows_var = tk.StringVar(value="3")
        min_values = [str(i) for i in range(1, 21)]  # 1 to 20
        min_combobox = ttk.Combobox(min_frame, textvariable=self.min_follows_var, 
                                   values=min_values, width=8, font=("SF Pro Display", 12),
                                   state="readonly", height=10)
        min_combobox.pack(anchor="w", pady=(5, 0))
        
        # Max followers  
        max_frame = ttk.Frame(range_frame)
        max_frame.pack(side="right", fill="x", expand=True, padx=(15, 0))
        ttk.Label(max_frame, text="Maximum per account:", font=("SF Pro Display", 12, "bold")).pack(anchor="w")
        self.max_follows_var = tk.StringVar(value="8")
        max_values = [str(i) for i in range(1, 51)]  # 1 to 50
        max_combobox = ttk.Combobox(max_frame, textvariable=self.max_follows_var, 
                                   values=max_values, width=8, font=("SF Pro Display", 12),
                                   state="readonly", height=10)
        max_combobox.pack(anchor="w", pady=(5, 0))
        
        # Range explanation
        ttk.Label(range_section, 
                 text="🎲 The bot will randomly pick a number between min and max for each account",
                 font=("SF Pro Display", 10), foreground="gray").pack(anchor="w", pady=(10, 0))
        
        # Daily Limit Section
        limit_section = ttk.LabelFrame(strategy_section, text="Daily Safety Limits", 
                                     padding="15")
        limit_section.pack(fill="x")
        
        limit_frame = ttk.Frame(limit_section)
        limit_frame.pack(fill="x")
        ttk.Label(limit_frame, text="Daily Follow Limit:", font=("SF Pro Display", 12, "bold")).pack(anchor="w")
        self.daily_limit_var = tk.StringVar(value="25")
        limit_values = [str(i) for i in range(5, 101, 5)]  # 5, 10, 15, ... 100
        limit_combobox = ttk.Combobox(limit_frame, textvariable=self.daily_limit_var, 
                                     values=limit_values, width=8, font=("SF Pro Display", 12),
                                     state="readonly", height=10)
        limit_combobox.pack(anchor="w", pady=(5, 0))
        
        ttk.Label(limit_frame, 
                 text="🛡️ Maximum total follows per day (recommended: 25 for safety)",
                 font=("SF Pro Display", 10), foreground="gray").pack(anchor="w", pady=(5, 0))
        
        # Save configuration button
        save_frame = ttk.Frame(self.settings_frame, padding="15 0 0 0")
        save_frame.pack(fill="x")
        
        save_button = ttk.Button(save_frame, text="💾 Save Configuration", 
                               command=self.save_settings,
                               style="Accent.TButton")
        save_button.pack()
        
    def create_modern_footer(self, parent):
        """Create modern footer"""
        footer = ttk.Frame(parent, padding="20 15 0 0")
        footer.pack(fill="x", side="bottom")
        
        # Separator line
        separator = ttk.Separator(footer, orient='horizontal')
        separator.pack(fill='x', pady=(0, 10))
        
        footer_text = ttk.Label(footer, 
                               text="💡 Close window = background mode • ⌘Q = quit completely • Click dock icon = reopen",
                               font=("SF Pro Display", 10), foreground="gray")
        footer_text.pack()
        
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
        
    def toggle_settings(self):
        """Show/hide the settings configuration panel"""
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(fill="x", pady=(15, 0))
            self.settings_visible = True
    
    def start_automation(self):
        """Start the autonomous Instagram automation"""
        global automation_running
        
        if not self.validate_settings():
            messagebox.showerror("Configuration Required", 
                               "Please configure your Instagram username, password, and target accounts first.\n\n"
                               "Click 'Configuration' to set up your bot.")
            self.toggle_settings()
            return
        
        if automation_running:
            messagebox.showinfo("Already Running", 
                               "🤖 Bot is already running autonomously!\n\n"
                               "You can close this window and it will continue in the background.")
            return
        
        # Update UI state
        automation_running = True
        self.status_text.set("🟢 Running autonomously - following Instagram users")
        self.start_button.config(state="disabled")
        
        # Start automation in background thread
        threading.Thread(target=self.run_automation_loop, daemon=True).start()
        
        # Show success message with range info
        min_val = self.min_follows_var.get()
        max_val = self.max_follows_var.get()
        daily_limit = self.daily_limit_var.get()
        
        messagebox.showinfo("🚀 Bot Started!", 
                           f"✅ Instagram Bot is now running autonomously!\n\n"
                           f"💡 Configuration:\n"
                           f"• Follow range: {min_val}-{max_val} users per account\n"
                           f"• Daily limit: {daily_limit} total follows\n"
                           f"• Target accounts: {len(self.targets_var.get().split(','))} accounts\n\n"
                           f"🔒 The bot follows Instagram's rate limits for safety.\n"
                           f"You can close this window - bot continues in background!")
        
    def stop_automation(self):
        """Stop the autonomous automation"""
        global automation_running
        automation_running = False
        self.status_text.set("⚪ Automation stopped")
        self.start_button.config(state="normal")
        
        messagebox.showinfo("Bot Stopped", "🛑 Autonomous operation has been stopped.")
        
    def run_automation_loop(self):
        """Run the actual Instagram automation loop with range selection"""
        global automation_running, last_activity
        
        try:
            # Import the Instagram automation GUI (fix import path)
            sys.path.insert(0, str(Path.cwd()))
            
            # Try multiple import strategies
            try:
                from instagram_gui import InstagramAutomationGUI
            except ImportError:
                # Try from current directory
                import importlib.util
                spec = importlib.util.spec_from_file_location("instagram_gui", "instagram_gui.py")
                if spec and spec.loader:
                    instagram_gui = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(instagram_gui)
                    InstagramAutomationGUI = instagram_gui.InstagramAutomationGUI
                else:
                    raise ImportError("Could not find instagram_gui.py module")
            
            # Create a hidden automation window
            automation_root = tk.Tk()
            automation_root.withdraw()  # Hide the automation window
            
            # Create automation instance
            automation = InstagramAutomationGUI(automation_root)
            
            # Apply our autonomous settings
            automation.username_var.set(self.username_var.get())
            automation.password_var.set(self.password_var.get())
            automation.target_accounts_var.set(self.targets_var.get())
            
            # Set up range-based following
            min_follows = int(self.min_follows_var.get())
            max_follows = int(self.max_follows_var.get())
            daily_limit = int(self.daily_limit_var.get())
            
            # Override the automation's settings with our range
            automation.users_per_account_min_var.set(str(min_follows))
            automation.users_per_account_max_var.set(str(max_follows))
            automation.daily_follow_limit_var.set(str(daily_limit))
            
            # Start the automation scheduler
            automation.toggle_scheduler()
            
            # Keep the automation running while status is active
            while automation_running:
                automation_root.update()
                last_activity = datetime.now().strftime("%H:%M")
                time.sleep(1)
                
        except ImportError as e:
            automation_running = False
            self.status_text.set("🔴 Error - Missing instagram_gui module")
            self.root.after(0, lambda: messagebox.showerror("Module Error", 
                               f"Could not import instagram automation module.\n\n"
                               f"Error: {str(e)}\n\n"
                               f"Please ensure instagram_gui.py is in the project directory."))
            
        except Exception as e:
            automation_running = False
            self.status_text.set("🔴 Error occurred - automation stopped")
            self.root.after(0, lambda: messagebox.showerror("Automation Error", 
                               f"An error occurred during automation:\n\n{str(e)}\n\n"
                               f"Please check your Instagram credentials and internet connection."))
            
    def validate_settings(self):
        """Check if all required settings are configured"""
        username_ok = self.username_var.get().strip()
        password_ok = self.password_var.get().strip()
        targets_ok = self.targets_var.get().strip()
        
        # Validate range values
        try:
            min_val = int(self.min_follows_var.get())
            max_val = int(self.max_follows_var.get())
            daily_val = int(self.daily_limit_var.get())
            
            if min_val > max_val:
                messagebox.showerror("Invalid Range", "Minimum follows cannot be greater than maximum follows!")
                return False
                
            if min_val < 1 or max_val < 1 or daily_val < 1:
                messagebox.showerror("Invalid Values", "All follow values must be greater than 0!")
                return False
                
        except ValueError:
            messagebox.showerror("Invalid Numbers", "Please enter valid numbers for follow ranges!")
            return False
        
        return username_ok and password_ok and targets_ok
    
    def save_settings(self):
        """Save configuration to file"""
        self.settings = {
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "target_accounts": self.targets_var.get(),
            "min_follows": self.min_follows_var.get(),
            "max_follows": self.max_follows_var.get(),
            "daily_limit": self.daily_limit_var.get(),
            "saved_at": datetime.now().isoformat()
        }
        
        try:
            with open('autonomous_bot_config.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
            messagebox.showinfo("Configuration Saved", 
                               f"✅ Your bot configuration has been saved!\n\n"
                               f"Follow range: {self.min_follows_var.get()}-{self.max_follows_var.get()} per account\n"
                               f"Daily limit: {self.daily_limit_var.get()} total follows")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save configuration:\n\n{e}")
    
    def load_settings(self):
        """Load configuration from file"""
        try:
            config_file = Path('autonomous_bot_config.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.settings = json.load(f)
                
                # Apply loaded settings to UI
                self.username_var.set(self.settings.get("username", ""))
                self.password_var.set(self.settings.get("password", ""))
                self.targets_var.set(self.settings.get("target_accounts", "deadmau5,skrillex,housemusic"))
                self.min_follows_var.set(self.settings.get("min_follows", "3"))
                self.max_follows_var.set(self.settings.get("max_follows", "8"))
                self.daily_limit_var.set(self.settings.get("daily_limit", "25"))
                
                print("✅ Configuration loaded from file")
        except Exception as e:
            print(f"⚠️ Could not load configuration: {e}")
    
    def start_status_updates(self):
        """Start periodic status and statistics updates"""
        self.update_stats()
        # Schedule next update in 10 seconds
        self.root.after(10000, self.start_status_updates)
    
    def update_stats(self):
        """Update statistics display from bot data files"""
        global last_activity
        
        try:
            # Load follow statistics from bot data
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows_data = json.load(f)
                    total_follows = len(follows_data)
                    self.total_follows.set(f"Total Follows: {total_follows}")
            
            # Update last activity time
            if last_activity:
                self.last_activity.set(f"Last Activity: {last_activity}")
                
        except Exception as e:
            print(f"⚠️ Stats update error: {e}")
    
    def show_detailed_stats(self):
        """Show detailed statistics in a new window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Instagram Bot - Detailed Statistics")
        stats_window.geometry("750x550")
        
        # Create scrollable text area for stats
        text_frame = ttk.Frame(stats_window, padding="20")
        text_frame.pack(fill="both", expand=True)
        
        text_area = tk.Text(text_frame, wrap=tk.WORD, font=("SF Mono", 12))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Generate and display statistics report
        stats_content = self.generate_stats_report()
        text_area.insert(tk.END, stats_content)
        text_area.config(state=tk.DISABLED)
    
    def generate_stats_report(self):
        """Generate comprehensive statistics report"""
        global automation_running
        
        report = "📊 INSTAGRAM BOT - DETAILED STATISTICS REPORT\n"
        report += "=" * 70 + "\n\n"
        
        try:
            # Account Configuration
            report += "📱 ACCOUNT CONFIGURATION\n"
            report += f"Instagram Username: {self.username_var.get() or 'Not configured'}\n"
            report += f"Target Accounts: {self.targets_var.get() or 'Not configured'}\n"
            report += f"Follow Range: {self.min_follows_var.get()}-{self.max_follows_var.get()} per account\n"
            report += f"Daily Limit: {self.daily_limit_var.get()} total follows\n"
            report += f"Configuration Status: {'✅ Complete' if self.validate_settings() else '❌ Incomplete'}\n\n"
            
            # Follow Statistics
            if Path('instagram_data/follows.json').exists():
                with open('instagram_data/follows.json', 'r') as f:
                    follows_data = json.load(f)
                
                total_follows = len(follows_data)
                following = sum(1 for user in follows_data.values() 
                               if user.get('status') == 'following')
                unfollowed = sum(1 for user in follows_data.values() 
                               if user.get('status') == 'unfollowed')
                
                report += "📈 FOLLOW STATISTICS\n"
                report += f"Total users ever followed: {total_follows}\n"
                report += f"Currently following: {following}\n"
                report += f"Previously unfollowed: {unfollowed}\n"
                if total_follows > 0:
                    report += f"Follow retention rate: {(following/total_follows*100):.1f}%\n\n"
                
                # Source account breakdown
                sources = {}
                for user_data in follows_data.values():
                    source = user_data.get('source_account', 'Unknown')
                    sources[source] = sources.get(source, 0) + 1
                
                if sources:
                    report += "📊 FOLLOWS BY SOURCE ACCOUNT\n"
                    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                        report += f"  {source}: {count} follows\n"
                    report += "\n"
            
            # Recent Activity Log
            if Path('instagram_data/action_log.json').exists():
                with open('instagram_data/action_log.json', 'r') as f:
                    action_log = json.load(f)
                
                if action_log:
                    report += "🕐 RECENT ACTIVITY (Last 15 actions)\n"
                    recent_actions = sorted(action_log, key=lambda x: x['timestamp'])[-15:]
                    
                    for action in recent_actions:
                        timestamp = action['timestamp'][:16].replace('T', ' ')
                        action_type = action['action'].title()
                        target = action['target']
                        details = action.get('details', '')
                        
                        report += f"  {timestamp}: {action_type} @{target}"
                        if details:
                            report += f" - {details}"
                        report += "\n"
                    report += "\n"
            
            # Bot Status and Health
            report += "🤖 BOT STATUS & HEALTH\n"
            report += f"Current Status: {'🟢 Running' if automation_running else '⚪ Stopped'}\n"
            report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"Data Directory: {'✅ Found' if Path('instagram_data').exists() else '❌ Missing'}\n"
            
        except Exception as e:
            report += f"❌ Error generating statistics report: {e}\n"
        
        return report
    
    def hide_to_background(self):
        """Hide window but keep application running in background"""
        global app_should_quit
        if not app_should_quit:
            try:
                self.root.withdraw()
                print("🔽 Instagram Bot minimized to background - continues running autonomously")
                print("💡 Click the dock icon anytime to reopen the window")
            except Exception as e:
                print(f"⚠️ Error hiding window: {e}")
        else:
            self.quit_application()
    
    def show_window(self):
        """Show the application window (called when clicking dock icon)"""
        try:
            # Ensure window is visible and focused
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # Bring to front on macOS
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            print("🔼 Instagram Bot window restored from dock")
        except Exception as e:
            print(f"⚠️ Error showing window: {e}")
            # Fallback
            try:
                self.root.deiconify()
            except:
                pass
    
    def quit_application(self):
        """Quit the application completely"""
        global app_should_quit, automation_running
        app_should_quit = True
        automation_running = False
        self.root.quit()
        print("👋 Instagram Bot application quit")

def main():
    """Main application entry point"""
    try:
        # Create the main Tkinter window
        root = tk.Tk()
        handle_signals.root = root
        
        # Set application icon if available
        try:
            if Path('icon.png').exists():
                icon_image = tk.PhotoImage(file='icon.png')
                root.iconphoto(True, icon_image)
                print("🎨 Custom icon.png loaded for window")
        except Exception as e:
            print(f"⚠️ Could not load custom icon: {e}")
        
        # Create the autonomous Instagram bot application
        app = AutonomousInstagramBot(root)
        
        # Position window in center of screen
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 750) // 2
        y = (screen_height - 700) // 2
        root.geometry(f"750x700+{x}+{y}")
        
        # Startup messages
        print("🚀 Instagram Bot - Autonomous Mode Started")
        print("📱 Configure your Instagram credentials and target accounts")
        print("🎲 Set follow ranges for randomized targeting")
        print("▶️ Click 'Start Autonomous Mode' to begin")
        print("🔽 Close window to run in background")
        print("👆 Click dock icon anytime to check progress")
        print("⌘Q to quit completely")
        
        # Start the application main loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
 