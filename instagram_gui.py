#!/usr/bin/env python3
"""
Instagram Bot GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path

class InstagramBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Bot")
        self.root.geometry("800x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_login_tab()
        self.create_control_tab()
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