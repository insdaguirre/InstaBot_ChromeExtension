import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from pathlib import Path
import threading
import random
import uuid
from deployment_package.instagram_gui import InstagramBotGUI

class BatchFollowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Batch Follow Manager")
        
        # Set window size and make it resizable
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Batch.TFrame', relief='solid', borderwidth=1)
        self.style.configure('BatchHeader.TLabel', font=('Helvetica', 11, 'bold'))
        self.style.configure('Status.TLabel', font=('Helvetica', 10))
        self.style.configure('Unfollowed.TFrame', background='#f0f0f0')
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.target_accounts_var = tk.StringVar()
        self.min_follows_var = tk.StringVar(value="3")
        self.max_follows_var = tk.StringVar(value="10")
        self.show_browser_var = tk.BooleanVar(value=True)
        self.show_password_var = tk.BooleanVar(value=False)
        
        # Add status message variable
        self.status_message = tk.StringVar(value="Ready to start")
        
        # Add counters
        self.total_followed = tk.StringVar(value="0")
        self.total_unfollowed = tk.StringVar(value="0")
        
        # Data storage
        self.data_dir = Path('instagram_data')
        self.data_dir.mkdir(exist_ok=True)
        self.batches_file = self.data_dir / 'follow_batches.json'
        self.batches = self.load_batches()
        
        # Create main layout
        self.create_main_layout()
        
        # Start periodic updates
        self.update_batches_display()
        self.update_totals()
        
    def create_main_layout(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Configuration
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Login section
        login_frame = ttk.LabelFrame(left_panel, text="Instagram Login", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Username:").pack(fill=tk.X)
        ttk.Entry(login_frame, textvariable=self.username_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(login_frame, text="Password:").pack(fill=tk.X)
        
        # Password entry and show password checkbox in same frame
        password_frame = ttk.Frame(login_frame)
        password_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Checkbutton(
            password_frame, 
            text="Show", 
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Target accounts section
        target_frame = ttk.LabelFrame(left_panel, text="Target Configuration", padding="10")
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(target_frame, text="Target Accounts (comma-separated):").pack(fill=tk.X)
        ttk.Entry(target_frame, textvariable=self.target_accounts_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(target_frame, text="Follow Range:").pack(fill=tk.X)
        range_frame = ttk.Frame(target_frame)
        range_frame.pack(fill=tk.X)
        
        ttk.Entry(range_frame, textvariable=self.min_follows_var, width=5).pack(side=tk.LEFT)
        ttk.Label(range_frame, text=" to ").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.max_follows_var, width=5).pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.Frame(target_frame)
        options_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Checkbutton(options_frame, text="Show Browser", variable=self.show_browser_var).pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = ttk.Frame(left_panel)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(actions_frame, text="Start New Batch", command=self.start_new_batch).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(actions_frame, text="Delete Unfollowed Batches", command=self.delete_unfollowed_batches).pack(fill=tk.X, pady=(0, 5))
        
        # Status log
        status_frame = ttk.LabelFrame(left_panel, text="Status Log", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, textvariable=self.status_message, wraplength=250).pack(fill=tk.X)
        
        # Totals frame
        totals_frame = ttk.LabelFrame(left_panel, text="Total Statistics", padding="10")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Total followed
        followed_frame = ttk.Frame(totals_frame)
        followed_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(followed_frame, text="Total Followed:").pack(side=tk.LEFT)
        ttk.Label(followed_frame, textvariable=self.total_followed, font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Total unfollowed
        unfollowed_frame = ttk.Frame(totals_frame)
        unfollowed_frame.pack(fill=tk.X)
        ttk.Label(unfollowed_frame, text="Total Unfollowed:").pack(side=tk.LEFT)
        ttk.Label(unfollowed_frame, textvariable=self.total_unfollowed, font=('Helvetica', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Right panel - Batches
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Batches header with custom style
        header_label = ttk.Label(right_panel, text="Follow Batches", style='Header.TLabel')
        header_label.pack(fill=tk.X, pady=(0, 10))
        
        # Create scrollable frame for batches
        self.canvas = tk.Canvas(right_panel, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        
        # Create a frame to hold all batches
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=right_panel.winfo_width()
        )
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind events
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_canvas_configure(self, event):
        # Update the width of the canvas window when the canvas is resized
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_batch_frame(self, batch, frame):
        # Create a frame with border
        batch_frame = tk.Frame(frame, relief="solid", borderwidth=1)
        batch_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        # Add gray background if batch is unfollowed
        is_unfollowed = all(user.get('unfollowed', False) for user in batch['users'])
        if is_unfollowed:
            batch_frame.configure(bg='#f0f0f0')
        
        # Inner frame for padding
        inner_frame = tk.Frame(batch_frame, padx=10, pady=10)
        inner_frame.pack(fill=tk.X)
        if is_unfollowed:
            inner_frame.configure(bg='#f0f0f0')
        
        # Batch header
        header_frame = tk.Frame(inner_frame)
        header_frame.pack(fill=tk.X)
        if is_unfollowed:
            header_frame.configure(bg='#f0f0f0')
        
        # Format timestamp
        timestamp = datetime.fromisoformat(batch['timestamp'])
        date_str = timestamp.strftime("%Y-%m-%d %H:%M")
        
        # Header label with custom font
        tk.Label(
            header_frame,
            text=f"Batch from {date_str}",
            font=('Helvetica', 11, 'bold'),
            bg='#f0f0f0' if is_unfollowed else 'white'
        ).pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        if is_unfollowed:
            status_frame.configure(bg='#f0f0f0')
        
        total_users = len(batch['users'])
        unfollowed = sum(1 for user in batch['users'] if user.get('unfollowed'))
        
        tk.Label(
            status_frame,
            text=f"Users: {total_users}  •  Unfollowed: {unfollowed}",
            font=('Helvetica', 10),
            bg='#f0f0f0' if is_unfollowed else 'white'
        ).pack(side=tk.RIGHT)
        
        # Source accounts
        sources = batch.get('source_accounts', [])
        if sources:
            tk.Label(
                inner_frame,
                text=f"Sources: {', '.join(sources)}",
                font=('Helvetica', 10),
                bg='#f0f0f0' if is_unfollowed else 'white'
            ).pack(fill=tk.X, pady=(5, 0))
        
        # Action buttons
        if not is_unfollowed:
            actions_frame = tk.Frame(inner_frame)
            actions_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(
                actions_frame,
                text="Unfollow All",
                command=lambda b=batch: self.unfollow_batch(b)
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
            
        # Get follow count
        min_follows = int(self.min_follows_var.get())
        max_follows = int(self.max_follows_var.get())
        follow_count = random.randint(min_follows, max_follows)
        
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
            args=(batch, follow_count),
            daemon=True
        ).start()
        
    def execute_batch(self, batch, follow_count):
        try:
            self.update_status(f"Initializing bot for new batch...")
            
            # Create bot instance
            bot = InstagramBotGUI(
                self.username_var.get().strip(),
                self.password_var.get().strip(),
                batch['source_accounts'],
                follow_count
            )
            
            # Initialize and login
            if not bot.init_driver(show_browser=self.show_browser_var.get()):
                raise Exception("Failed to initialize browser")
                
            if not bot.login():
                raise Exception("Failed to login to Instagram")
                
            # Follow users from each source account
            for account in batch['source_accounts']:
                if len(batch['users']) >= follow_count:
                    break
                    
                self.update_status(f"Following users from @{account}...")
                
                # Follow users and track them in the batch
                followed = bot.follow_users_from_account(account)
                
                # Update batch with new follows
                for username, data in bot.follows_data.items():
                    if data.get('source_account') == account:
                        batch['users'].append({
                            'username': username,
                            'followed_at': data['followed_at'],
                            'unfollowed': False
                        })
                        
            batch['completed'] = True
            self.save_batches()
            
            self.update_status(f"Batch completed: {len(batch['users'])} users followed")
            
            # Cleanup
            if bot.driver:
                bot.driver.quit()
                
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
            min_follows = int(self.min_follows_var.get())
            max_follows = int(self.max_follows_var.get())
            
            if min_follows < 1 or max_follows < min_follows:
                raise ValueError()
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid follow range numbers")
            return False
            
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchFollowGUI(root)
    root.mainloop() 