#!/usr/bin/env python3
"""
Instagram Bot GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
from datetime import datetime
import random
import threading

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Bot")
        self.root.geometry("800x600")
        
        # Initialize batches data first
        self.batches_file = Path('instagram_data/follow_batches.json')
        self.batches = self.load_batches()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_login_tab()
        self.create_control_tab()
        self.create_batch_unfollow_tab()
        self.create_stats_tab()
        
        # Load settings if they exist
        self.load_settings()
        
    def create_login_tab(self):
        """Create login and settings tab"""
        login_frame = ttk.Frame(self.notebook)
        self.notebook.add(login_frame, text="Login & Settings")
        
        # Instagram Credentials
        creds_frame = ttk.LabelFrame(login_frame, text="Instagram Credentials", padding=15)
        creds_frame.pack(fill="x", padx=20, pady=(20,10))
        
        ttk.Label(creds_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(creds_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky="w", padx=(10,0), pady=5)
        
        ttk.Label(creds_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(creds_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky="w", padx=(10,0), pady=5)
        
        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_cb = ttk.Checkbutton(creds_frame, text="Show Password", 
                                         variable=self.show_password_var, 
                                         command=self.toggle_password_visibility)
        show_password_cb.grid(row=1, column=2, sticky="w", padx=(10,0), pady=5)
        
        # Target Accounts
        accounts_frame = ttk.LabelFrame(login_frame, text="Target Accounts", padding=15)
        accounts_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(accounts_frame, text="Target Accounts (comma separated):").grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        self.target_accounts_var = tk.StringVar(value="deadmau5,skrillex,1001tracklists,housemusic.us")
        ttk.Entry(accounts_frame, textvariable=self.target_accounts_var, width=60).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Save/Load buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        ttk.Button(button_frame, text="💾 Save Settings", command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📂 Load Settings", command=self.load_settings).pack(side="left", padx=5)
    
    def create_control_tab(self):
        """Create control tab"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control")
        
        # Status display
        status_frame = ttk.LabelFrame(control_frame, text="Status", padding=15)
        status_frame.pack(fill="x", padx=20, pady=(20,10))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, font=("SF Pro Display", 14, "bold")).pack()
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(button_frame, text="▶️ Start Automation", command=self.start_automation).pack(side="left", padx=5)
        ttk.Button(button_frame, text="⏹️ Stop", command=self.stop_automation).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🧪 Test Connection", command=self.test_connection).pack(side="left", padx=5)
    
    def create_batch_unfollow_tab(self):
        """Create batch unfollow tab"""
        unfollow_frame = ttk.Frame(self.notebook)
        self.notebook.add(unfollow_frame, text="Batch Unfollow")
        
        # Status display
        status_frame = ttk.LabelFrame(unfollow_frame, text="Status", padding=15)
        status_frame.pack(fill="x", padx=20, pady=(20,10))
        
        self.unfollow_status_var = tk.StringVar(value="Ready to unfollow users from your following list")
        ttk.Label(status_frame, textvariable=self.unfollow_status_var, font=("SF Pro Display", 12)).pack()
        
        # Current page info
        current_page_frame = ttk.LabelFrame(unfollow_frame, text="Current Page", padding=15)
        current_page_frame.pack(fill="x", padx=20, pady=10)
        
        self.current_page_var = tk.StringVar(value="Not on Instagram following page")
        ttk.Label(current_page_frame, textvariable=self.current_page_var, font=("SF Pro Display", 10)).pack()
        
        # Batches display
        batches_frame = ttk.LabelFrame(unfollow_frame, text="Follow Batches", padding=15)
        batches_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create canvas for scrollable batches
        self.batches_canvas = tk.Canvas(batches_frame, height=300)
        scrollbar = ttk.Scrollbar(batches_frame, orient="vertical", command=self.batches_canvas.yview)
        self.scrollable_batches_frame = ttk.Frame(self.batches_canvas)
        
        self.scrollable_batches_frame.bind(
            "<Configure>",
            lambda e: self.batches_canvas.configure(scrollregion=self.batches_canvas.bbox("all"))
        )
        
        self.batches_canvas.create_window((0, 0), window=self.scrollable_batches_frame, anchor="nw")
        self.batches_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.batches_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_frame = ttk.Frame(unfollow_frame)
        refresh_frame.pack(fill="x", padx=20, pady=10)
        ttk.Button(refresh_frame, text="🔄 Refresh Batches", command=self.refresh_batches_display).pack(side="left", padx=5)
        
        # Initial load of batches
        self.refresh_batches_display()
    
    def create_stats_tab(self):
        """Create statistics tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Stats display
        stats_display = ttk.LabelFrame(stats_frame, text="Statistics", padding=15)
        stats_display.pack(fill="both", expand=True, padx=20, pady=(20,10))
        
        self.stats_text = tk.Text(stats_display, wrap=tk.WORD, height=20)
        self.stats_text.pack(fill="both", expand=True)
        
        # Update button
        ttk.Button(stats_frame, text="🔄 Refresh Stats", command=self.update_stats).pack(pady=10)
    
    def load_batches(self):
        """Load batches from file"""
        if self.batches_file.exists():
            try:
                with open(self.batches_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading batches: {e}")
                return []
        return []
    
    def refresh_batches_display(self):
        """Refresh the batches display"""
        # Clear existing frames
        for widget in self.scrollable_batches_frame.winfo_children():
            widget.destroy()
        
        # Reload batches
        self.batches = self.load_batches()
        
        if not self.batches:
            no_batches_label = ttk.Label(self.scrollable_batches_frame, text="No follow batches found", font=("SF Pro Display", 12))
            no_batches_label.pack(pady=20)
            return
        
        # Sort batches by timestamp (newest first)
        sorted_batches = sorted(
            self.batches,
            key=lambda x: datetime.fromisoformat(x['timestamp']),
            reverse=True
        )
        
        # Create frames for each batch
        for batch in sorted_batches:
            self.create_batch_unfollow_frame(batch)
    
    def create_batch_unfollow_frame(self, batch):
        """Create a frame for a batch in the unfollow tab"""
        batch_frame = ttk.Frame(self.scrollable_batches_frame, relief="solid", borderwidth=1)
        batch_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Inner frame for padding
        inner_frame = ttk.Frame(batch_frame, padding=10)
        inner_frame.pack(fill="x")
        
        # Batch header with timestamp
        header_frame = ttk.Frame(inner_frame)
        header_frame.pack(fill="x")
        
        # Format timestamp
        try:
            timestamp = datetime.fromisoformat(batch['timestamp'])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = "Unknown time"
        
        # Header label
        ttk.Label(
            header_frame,
            text=f"Batch from {date_str}",
            font=("SF Pro Display", 11, "bold")
        ).pack(side="left")
        
        # Status indicators
        total_users = len(batch['users'])
        unfollowed = sum(1 for user in batch['users'] if user.get('unfollowed', False))
        
        status_label = ttk.Label(
            header_frame,
            text=f"Users: {total_users} • Unfollowed: {unfollowed}",
            font=("SF Pro Display", 10)
        )
        status_label.pack(side="right")
        
        # Source accounts
        sources = batch.get('source_accounts', [])
        if sources:
            ttk.Label(
                inner_frame,
                text=f"Sources: {', '.join(sources)}",
                font=("SF Pro Display", 10)
            ).pack(fill="x", pady=(5, 0))
        
        # Action buttons - only show if there are users to unfollow
        if total_users > 0 and unfollowed < total_users:
            actions_frame = ttk.Frame(inner_frame)
            actions_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(
                actions_frame,
                text="Unfollow This Batch",
                command=lambda b=batch: self.unfollow_batch(b)
            ).pack(side="left")
            
            # Show count of users to unfollow
            users_to_unfollow = total_users - unfollowed
            ttk.Label(
                actions_frame,
                text=f"({users_to_unfollow} users will be unfollowed)",
                font=("SF Pro Display", 9)
            ).pack(side="left", padx=(10, 0))
        elif total_users == 0:
            ttk.Label(
                inner_frame,
                text="No users in this batch",
                font=("SF Pro Display", 9),
                foreground="gray"
            ).pack(pady=(10, 0))
        else:
            ttk.Label(
                inner_frame,
                text="All users in this batch have been unfollowed",
                font=("SF Pro Display", 9),
                foreground="green"
            ).pack(pady=(10, 0))
    
    def unfollow_batch(self, batch):
        """Unfollow all users in a specific batch"""
        if not self.username_var.get() or not self.password_var.get():
            messagebox.showerror("Error", "Please enter username and password in the Login & Settings tab")
            return
        
        # Count users to unfollow
        users_to_unfollow = [u for u in batch['users'] if not u.get('unfollowed', False)]
        
        if not users_to_unfollow:
            messagebox.showinfo("Info", "All users in this batch have already been unfollowed")
            return
        
        # Confirm unfollow
        if not messagebox.askyesno(
            "Confirm Unfollow",
            f"Are you sure you want to unfollow {len(users_to_unfollow)} users from the batch created on {datetime.fromisoformat(batch['timestamp']).strftime('%Y-%m-%d %H:%M')}?"
        ):
            return
        
        self.unfollow_status_var.set(f"Starting unfollow process for {len(users_to_unfollow)} users...")
        
        # Start unfollow process in background thread
        def unfollow_thread():
            try:
                # Import the actual Instagram bot
                import sys
                sys.path.append('deployment_package')
                from instagram_gui import InstagramBotGUI
                
                # Create bot instance
                bot = InstagramBotGUI(
                    self.username_var.get().strip(),
                    self.password_var.get().strip(),
                    [],  # No target accounts needed for unfollowing
                    0
                )
                
                # Initialize and login
                if not bot.init_driver(show_browser=False):  # Hide browser for unfollowing
                    raise Exception("Failed to initialize browser")
                    
                if not bot.login():
                    raise Exception("Failed to login to Instagram")
                
                # Unfollow each user in batch
                total_users = len(users_to_unfollow)
                unfollowed_count = 0
                
                for i, user in enumerate(users_to_unfollow):
                    try:
                        self.unfollow_status_var.set(f"Unfollowing {i + 1}/{total_users}: @{user['username']}")
                        
                        # Use the bot's unfollow method
                        if hasattr(bot, 'unfollow_user') and bot.unfollow_user(user['username']):
                            user['unfollowed'] = True
                            user['unfollowed_at'] = datetime.now().isoformat()
                            unfollowed_count += 1
                            
                            # Save progress
                            try:
                                with open(self.batches_file, 'w') as f:
                                    json.dump(self.batches, f, indent=2)
                            except Exception as e:
                                print(f"Warning: Could not save batch progress: {e}")
                        
                        # Add delay between unfollows to avoid rate limiting
                        import time
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        print(f"Error unfollowing @{user['username']}: {e}")
                        continue
                
                # Cleanup
                if bot.driver:
                    bot.driver.quit()
                
                # Update status and refresh display
                self.unfollow_status_var.set(f"Unfollow completed: {unfollowed_count}/{total_users} users unfollowed")
                self.root.after(0, self.refresh_batches_display)
                
            except Exception as e:
                error_msg = f"Failed to unfollow batch: {str(e)}"
                self.unfollow_status_var.set(f"Error: {error_msg}")
                messagebox.showerror("Error", error_msg)
        
        # Start the unfollow thread
        threading.Thread(target=unfollow_thread, daemon=True).start()
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")
    
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "target_accounts": self.target_accounts_var.get()
        }
        
        try:
            settings_dir = Path.home() / '.instagram_bot'
            settings_dir.mkdir(exist_ok=True)
            settings_file = settings_dir / 'settings.json'
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            settings_file = Path.home() / '.instagram_bot' / 'settings.json'
            
            if not settings_file.exists():
                return
                
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            self.username_var.set(settings.get("username", ""))
            self.password_var.set(settings.get("password", ""))
            self.target_accounts_var.set(settings.get("target_accounts", ""))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
        
    def start_automation(self):
        """Start the automation"""
        if not self.username_var.get() or not self.password_var.get():
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        self.status_var.set("Running...")
        # Add automation code here
    
    def stop_automation(self):
        """Stop the automation"""
        self.status_var.set("Stopped")
        # Add stop code here
    
    def test_connection(self):
        """Test Instagram connection"""
        if not self.username_var.get() or not self.password_var.get():
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        self.status_var.set("Testing connection...")
        # Add connection test code here
        
    def update_stats(self):
        """Update statistics display"""
        # Add stats update code here
        pass

def main():
    root = tk.Tk()
    app = InstagramBotGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - 800) // 2
    y = (root.winfo_screenheight() - 600) // 2
    root.geometry(f"800x600+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 