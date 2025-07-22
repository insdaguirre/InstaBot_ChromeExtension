import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from pathlib import Path
import threading
import random
import uuid
from deployment_package.instagram_gui import InstagramBotGUI

VINTAGE_BLUE = "#0a246a"
VINTAGE_GRAY = "#c0c0c0"
VINTAGE_LIGHT = "#eaeaea"
VINTAGE_BORDER = "#808080"
VINTAGE_BTN = "#f0f0f0"
VINTAGE_FONT = ("Courier New", 10, "normal")
VINTAGE_FONT_BOLD = ("Courier New", 11, "bold")
VINTAGE_HEADER = ("Courier New", 20, "bold")
VINTAGE_BTN_FONT = ("Courier New", 10, "bold")

class BatchFollowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("insta bot")
        self.root.configure(bg=VINTAGE_GRAY)
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        self.status_message = tk.StringVar(value="Ready to start")
        self.total_followed = tk.StringVar(value="0")
        self.total_unfollowed = tk.StringVar(value="0")
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.target_accounts_var = tk.StringVar()
        self.follows_per_account_var = tk.StringVar(value="10")
        self.show_browser_var = tk.BooleanVar(value=True)
        self.show_password_var = tk.BooleanVar(value=False)
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        self.batches_file = self.data_dir / 'follow_batches.json'
        self.batches = self.load_batches()
        self.create_main_layout()
        self.update_batches_display()
        self.update_totals()

    def create_main_layout(self):
        # --- Title Bar ---
        title_bar = tk.Frame(self.root, bg=VINTAGE_BLUE, height=56)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)
        title_label = tk.Label(title_bar, text="insta bot", fg="white", bg=VINTAGE_BLUE, font=VINTAGE_HEADER, padx=16, pady=8, anchor="w")
        title_label.pack(side=tk.LEFT, fill=tk.Y)
        for color in ("#c0c0c0", "#c0c0c0", "#c0c0c0"):
            tk.Canvas(title_bar, width=16, height=24, bg=VINTAGE_BLUE, highlightthickness=0).pack(side=tk.RIGHT, padx=2)

        # --- Main Layout ---
        main = tk.Frame(self.root, bg=VINTAGE_GRAY)
        main.pack(fill=tk.BOTH, expand=True)

        # Left column (status/summary on top, controls below)
        left_col = tk.Frame(main, bg=VINTAGE_GRAY)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(18, 8), pady=18, expand=False)

        # --- Status/Summary (top of left column) ---
        status_summary = tk.Frame(left_col, bg=VINTAGE_GRAY)
        status_summary.pack(fill=tk.X, pady=(0, 10))
        # Status log
        status_frame = tk.LabelFrame(status_summary, text="STATUS LOG", font=VINTAGE_FONT_BOLD, bg=VINTAGE_LIGHT, fg="black", bd=2, relief="groove", labelanchor="nw")
        status_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(status_frame, textvariable=self.status_message, wraplength=320, bg=VINTAGE_LIGHT, font=VINTAGE_FONT, anchor="w", justify="left", fg="black").pack(fill=tk.BOTH, padx=8, pady=8)
        # Stats
        stats_frame = tk.LabelFrame(status_summary, text="SUMMARY", font=VINTAGE_FONT_BOLD, bg=VINTAGE_LIGHT, fg="black", bd=2, relief="groove", labelanchor="nw")
        stats_frame.pack(fill=tk.X)
        tk.Label(stats_frame, text="TOTAL FOLLOWED:", bg=VINTAGE_LIGHT, font=VINTAGE_FONT_BOLD, anchor="w", fg="black").pack(fill=tk.X, padx=8, pady=(8,0))
        tk.Label(stats_frame, textvariable=self.total_followed, font=VINTAGE_FONT_BOLD, bg=VINTAGE_LIGHT, anchor="w", fg="black").pack(fill=tk.X, padx=8)
        tk.Label(stats_frame, text="TOTAL UNFOLLOWED:", bg=VINTAGE_LIGHT, font=VINTAGE_FONT_BOLD, anchor="w", fg="black").pack(fill=tk.X, padx=8, pady=(8,0))
        tk.Label(stats_frame, textvariable=self.total_unfollowed, font=VINTAGE_FONT_BOLD, bg=VINTAGE_LIGHT, anchor="w", fg="black").pack(fill=tk.X, padx=8)

        # --- Controls (bottom of left column) ---
        controls = tk.Frame(left_col, bg=VINTAGE_GRAY, bd=2, relief="groove", highlightbackground=VINTAGE_BORDER, highlightthickness=2)
        controls.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        tk.Label(controls, text="CONTROLS", font=VINTAGE_FONT_BOLD, bg=VINTAGE_GRAY, anchor="w", fg="black").pack(fill=tk.X, pady=(10, 2), padx=12)
        # Login
        login_frame = tk.LabelFrame(controls, text="INSTAGRAM LOGIN", font=VINTAGE_FONT, bg=VINTAGE_LIGHT, fg="black", bd=2, relief="groove", labelanchor="nw")
        login_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        tk.Label(login_frame, text="Username:", bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(anchor="w", padx=8, pady=(6,0))
        tk.Entry(login_frame, textvariable=self.username_var, font=VINTAGE_FONT, bg="white", relief="sunken", bd=2, fg="black").pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(login_frame, text="Password:", bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(anchor="w", padx=8)
        pw_frame = tk.Frame(login_frame, bg=VINTAGE_LIGHT)
        pw_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        self.password_entry = tk.Entry(pw_frame, textvariable=self.password_var, show="*", font=VINTAGE_FONT, bg="white", relief="sunken", bd=2, fg="black")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Checkbutton(pw_frame, text="Show", variable=self.show_password_var, command=self.toggle_password_visibility, bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(side=tk.LEFT, padx=(8,0))
        # Target
        target_frame = tk.LabelFrame(controls, text="TARGET CONFIGURATION", font=VINTAGE_FONT, bg=VINTAGE_LIGHT, fg="black", bd=2, relief="groove", labelanchor="nw")
        target_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        tk.Label(target_frame, text="Target Accounts (comma-separated):", bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(anchor="w", padx=8, pady=(6,0))
        tk.Entry(target_frame, textvariable=self.target_accounts_var, font=VINTAGE_FONT, bg="white", relief="sunken", bd=2, fg="black").pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(target_frame, text="Follows per Account:", bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(anchor="w", padx=8)
        range_frame = tk.Frame(target_frame, bg=VINTAGE_LIGHT)
        range_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Entry(range_frame, textvariable=self.follows_per_account_var, width=5, font=VINTAGE_FONT, bg="white", relief="sunken", bd=2, fg="black").pack(side=tk.LEFT)
        tk.Checkbutton(target_frame, text="Show Browser", variable=self.show_browser_var, bg=VINTAGE_LIGHT, font=VINTAGE_FONT, fg="black").pack(anchor="w", padx=8, pady=(0, 6))
        # Buttons
        btn_frame = tk.Frame(controls, bg=VINTAGE_GRAY)
        btn_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        tk.Button(btn_frame, text="START NEW BATCH", command=self.start_new_batch, font=VINTAGE_BTN_FONT, bg=VINTAGE_BTN, relief="raised", bd=2, activebackground=VINTAGE_LIGHT, anchor="center", fg="black").pack(fill=tk.X, pady=(0, 6))
        tk.Button(btn_frame, text="DELETE UNFOLLOWED BATCHES", command=self.delete_unfollowed_batches, font=VINTAGE_BTN_FONT, bg=VINTAGE_BTN, relief="raised", bd=2, activebackground=VINTAGE_LIGHT, anchor="center", fg="black").pack(fill=tk.X)

        # --- Batches/Logs (right column) ---
        batches_panel = tk.Frame(main, bg=VINTAGE_GRAY, bd=2, relief="groove", highlightbackground=VINTAGE_BORDER, highlightthickness=2)
        batches_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 18), pady=18)
        tk.Label(batches_panel, text="FOLLOW BATCHES", font=VINTAGE_FONT_BOLD, bg=VINTAGE_GRAY, anchor="w", fg="black").pack(fill=tk.X, padx=12, pady=(10, 0))
        self.canvas = tk.Canvas(batches_panel, highlightthickness=0, bg=VINTAGE_LIGHT)
        scrollbar = ttk.Scrollbar(batches_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=VINTAGE_LIGHT)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=700
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12,0), pady=(0,12))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,12))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        # Update the width of the canvas window when the canvas is resized
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_batch_frame(self, batch, frame):
        # Create a frame with border
        batch_frame = tk.Frame(frame, relief="solid", borderwidth=1, bg=VINTAGE_LIGHT)
        batch_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Add light gray background if batch is unfollowed
        is_unfollowed = all(user.get('unfollowed', False) for user in batch['users'])
        if is_unfollowed:
            batch_frame.configure(bg=VINTAGE_LIGHT)
        
        # Inner frame for padding
        inner_frame = tk.Frame(batch_frame, padx=10, pady=10, bg=VINTAGE_LIGHT)
        inner_frame.pack(fill=tk.X)
        
        # Batch header
        header_frame = tk.Frame(inner_frame, bg=VINTAGE_LIGHT)
        header_frame.pack(fill=tk.X)
        
        # Format timestamp
        timestamp = datetime.fromisoformat(batch['timestamp'])
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        
        # Header label with custom font
        tk.Label(
            header_frame,
            text=f"Batch from {date_str}",
            font=('Helvetica', 11, 'bold'),
            bg=VINTAGE_LIGHT,
            fg="black"
        ).pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(header_frame, bg=VINTAGE_LIGHT)
        status_frame.pack(side=tk.RIGHT)
        
        total_users = len(batch['users'])
        unfollowed = sum(1 for user in batch['users'] if user.get('unfollowed'))
        
        tk.Label(
            status_frame,
            text=f"Users: {total_users}  •  Unfollowed: {unfollowed}",
            font=('Helvetica', 10),
            bg=VINTAGE_LIGHT,
            fg="black"
        ).pack(side=tk.RIGHT)
        
        # Source accounts
        sources = batch.get('source_accounts', [])
        if sources:
            tk.Label(
                inner_frame,
                text=f"Sources: {', '.join(sources)}",
                font=('Helvetica', 10),
                bg=VINTAGE_LIGHT,
                fg="black"
            ).pack(fill=tk.X, pady=(5, 0))
        
        # Action buttons
        if not is_unfollowed:
            actions_frame = tk.Frame(inner_frame, bg=VINTAGE_LIGHT)
            actions_frame.pack(fill=tk.X, pady=(10, 0))
            
            tk.Button(
                actions_frame,
                text="Unfollow All",
                command=lambda b=batch: self.unfollow_batch(b),
                font=VINTAGE_BTN_FONT,
                bg=VINTAGE_BTN,
                fg="black",
                relief="raised",
                bd=2,
                activebackground=VINTAGE_LIGHT
            ).pack(side=tk.LEFT)
            
    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            
    def load_batches(self):
        if self.batches_file.exists():
            try:
                with open(self.batches_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
        
    def save_batches(self):
        with open(self.batches_file, 'w') as f:
            json.dump(self.batches, f, indent=2)
            
    def update_batches_display(self):
        # Clear existing frames
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Sort batches by timestamp (newest first)
        sorted_batches = sorted(
            self.batches,
            key=lambda x: datetime.fromisoformat(x['timestamp']),
            reverse=True
        )
        
        # Create frames for each batch
        for batch in sorted_batches:
            self.create_batch_frame(batch, self.scrollable_frame)
            
        # Schedule next update
        self.root.after(5000, self.update_batches_display)
        
    def update_status(self, message):
        """Update the status message"""
        self.status_message.set(message)
        
    def update_totals(self):
        """Update the total counters"""
        total_followed = 0
        total_unfollowed = 0
        
        for batch in self.batches:
            total_followed += len(batch['users'])
            total_unfollowed += sum(1 for user in batch['users'] if user.get('unfollowed', False))
        
        self.total_followed.set(str(total_followed))
        self.total_unfollowed.set(str(total_unfollowed))
        
        # Schedule next update
        self.root.after(5000, self.update_totals)
        
    def delete_unfollowed_batches(self):
        """Delete all batches that have been completely unfollowed"""
        # Find batches where all users are unfollowed
        unfollowed_batches = [
            batch for batch in self.batches 
            if all(user.get('unfollowed', False) for user in batch['users'])
        ]
        
        if not unfollowed_batches:
            self.update_status("No unfollowed batches to delete")
            return
        
        # Confirm deletion
        if messagebox.askyesno(
            "Delete Unfollowed Batches",
            f"Delete {len(unfollowed_batches)} unfollowed batches?"
        ):
            # Remove unfollowed batches
            self.batches = [
                batch for batch in self.batches 
                if not all(user.get('unfollowed', False) for user in batch['users'])
            ]
            
            # Save changes
            self.save_batches()
            self.update_status(f"Deleted {len(unfollowed_batches)} unfollowed batches")
            
    def start_new_batch(self):
        if not self.validate_inputs():
            return
            
        self.update_status("Starting new batch...")
            
        # Create new batch
        batch = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'source_accounts': [acc.strip() for acc in self.target_accounts_var.get().split(',')],
            'users': [],
            'completed': False
        }
        
        # Add to batches and save
        self.batches.append(batch)
        self.save_batches()
        
        # Start following process in background
        threading.Thread(
            target=self.execute_batch,
            args=(batch,),
            daemon=True
        ).start()
        
    def execute_batch(self, batch):
        try:
            self.update_status(f"Initializing bot for new batch...")
            
            # Get follows per account
            follows_per_account = int(self.follows_per_account_var.get())
            
            # For each account, follow the specified number
            for i, account in enumerate(batch['source_accounts']):
                self.update_status(f"Following {follows_per_account} users from @{account}...")
                
                # Create a fresh bot instance for each account (to avoid session issues)
                bot = InstagramBotGUI(
                    self.username_var.get().strip(),
                    self.password_var.get().strip(),
                    [account],
                    follows_per_account
                )
                
                if not bot.init_driver(show_browser=self.show_browser_var.get()):
                    raise Exception("Failed to initialize browser")
                if not bot.login():
                    raise Exception("Failed to login to Instagram")
                
                # Store initial count for this account
                initial_count = len(batch['users'])
                
                followed = bot.follow_users_from_account(account)
                
                # Update batch with new follows from this account
                for username, data in bot.follows_data.items():
                    if data.get('source_account') == account and not any(u['username'] == username for u in batch['users']):
                        batch['users'].append({
                            'username': username,
                            'followed_at': data['followed_at'],
                            'unfollowed': False
                        })
                        
                # Update GUI after completing each account
                self.save_batches()
                self.root.after(0, self.update_batches_display)
                self.root.after(0, self.update_totals)
                
                account_follows = len(batch['users']) - initial_count
                self.update_status(f"Completed @{account}: {account_follows} users followed")
                        
                if bot.driver:
                    bot.driver.quit()
                
            batch['completed'] = True
            self.save_batches()
            self.root.after(0, self.update_batches_display)
            self.root.after(0, self.update_totals)
            self.update_status(f"Batch completed: {len(batch['users'])} users followed")
        except Exception as e:
            error_msg = f"Failed to execute batch: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def unfollow_batch(self, batch):
        if not self.validate_inputs():
            return
            
        def unfollow_thread():
            try:
                self.update_status(f"Starting unfollow process...")
                
                # Create bot instance
                bot = InstagramBotGUI(
                    self.username_var.get().strip(),
                    self.password_var.get().strip(),
                    [],
                    0
                )
                
                # Initialize and login
                if not bot.init_driver(show_browser=self.show_browser_var.get()):
                    raise Exception("Failed to initialize browser")
                    
                if not bot.login():
                    raise Exception("Failed to login to Instagram")
                    
                # Unfollow each user in batch
                total_users = len([u for u in batch['users'] if not u.get('unfollowed')])
                unfollowed_count = 0
                
                for user in batch['users']:
                    if not user.get('unfollowed'):
                        self.update_status(f"Unfollowing {unfollowed_count + 1}/{total_users}: @{user['username']}")
                        if bot.unfollow_user(user['username']):
                            user['unfollowed'] = True
                            user['unfollowed_at'] = datetime.now().isoformat()
                            unfollowed_count += 1
                            self.save_batches()
                        
                # Cleanup
                if bot.driver:
                    bot.driver.quit()
                    
                self.update_status(f"Unfollow completed: {unfollowed_count}/{total_users} users unfollowed")
                    
            except Exception as e:
                error_msg = f"Failed to unfollow batch: {str(e)}"
                self.update_status(error_msg)
                messagebox.showerror("Error", error_msg)
                
        threading.Thread(target=unfollow_thread, daemon=True).start()
        
    def validate_inputs(self):
        if not self.username_var.get().strip():
            messagebox.showerror("Error", "Please enter your Instagram username")
            return False
            
        if not self.password_var.get().strip():
            messagebox.showerror("Error", "Please enter your Instagram password")
            return False
            
        if not self.target_accounts_var.get().strip():
            messagebox.showerror("Error", "Please enter at least one target account")
            return False
            
        try:
            follows_per_account = int(self.follows_per_account_var.get())
            
            if follows_per_account < 1:
                raise ValueError()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for follows per account")
            return False
            
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchFollowGUI(root)
    root.mainloop() 