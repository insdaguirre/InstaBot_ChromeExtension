"""
Secure configuration management for Instagram Automation System
"""
import os
import json
from typing import Dict, List, Optional

class Config:
    """Secure configuration loader that prioritizes environment variables over config files"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self._config = {}
        else:
            self._config = {}
    
    def get_instagram_username(self) -> str:
        """Get Instagram username from environment variable or config file"""
        username = os.getenv('INSTAGRAM_USERNAME')
        if username:
            return username
        
        if 'instagram' in self._config:
            return self._config['instagram'].get('username', '')
        
        raise ValueError("Instagram username not found. Please set INSTAGRAM_USERNAME environment variable or config file.")
    
    def get_instagram_password(self) -> str:
        """Get Instagram password from environment variable or config file"""
        password = os.getenv('INSTAGRAM_PASSWORD')
        if password:
            return password
        
        if 'instagram' in self._config:
            return self._config['instagram'].get('password', '')
        
        raise ValueError("Instagram password not found. Please set INSTAGRAM_PASSWORD environment variable or config file.")
    
    def get_target_accounts(self) -> List[str]:
        """Get target accounts list"""
        # Try environment variable first (comma-separated)
        env_accounts = os.getenv('TARGET_ACCOUNTS')
        if env_accounts:
            return [account.strip() for account in env_accounts.split(',')]
        
        # Fall back to config file
        if 'automation' in self._config:
            return self._config['automation'].get('target_accounts', [
                '1001tracklists', 'housemusic.us', 'housemusicnerds', 'edm'
            ])
        
        # Default accounts
        return ['1001tracklists', 'housemusic.us', 'housemusicnerds', 'edm']
    
    def get_users_per_account(self) -> int:
        """Get number of users to follow per account"""
        env_value = os.getenv('USERS_PER_ACCOUNT')
        if env_value:
            return int(env_value)
        
        if 'automation' in self._config:
            return self._config['automation'].get('users_per_account', 25)
        
        return 25
    
    def get_unfollow_delay_hours(self) -> int:
        """Get unfollow delay in hours"""
        env_value = os.getenv('UNFOLLOW_DELAY_HOURS')
        if env_value:
            return int(env_value)
        
        if 'automation' in self._config:
            return self._config['automation'].get('unfollow_delay_hours', 48)
        
        return 48
    
    def get_aws_instance_type(self) -> str:
        """Get preferred AWS instance type"""
        instance_type = os.getenv('AWS_INSTANCE_TYPE')
        if instance_type:
            return instance_type
        
        if 'aws' in self._config:
            return self._config['aws'].get('instance_type', 't3.small')
        
        return 't3.small'
    
    def get_aws_region(self) -> str:
        """Get AWS region"""
        region = os.getenv('AWS_REGION')
        if region:
            return region
        
        if 'aws' in self._config:
            return self._config['aws'].get('region', 'us-east-2')
        
        return 'us-east-2'


# Global config instance
config = Config()

def get_credentials() -> tuple[str, str]:
    """Get Instagram credentials as (username, password) tuple"""
    return config.get_instagram_username(), config.get_instagram_password()

def get_automation_settings() -> dict:
    """Get automation settings as dictionary"""
    return {
        'target_accounts': config.get_target_accounts(),
        'users_per_account': config.get_users_per_account(),
        'unfollow_delay_hours': config.get_unfollow_delay_hours()
    } 