"""
Configuration Helper for Instagram-to-Social Media Agent System
Validates and manages environment variables
"""
import os
from typing import Dict, List, Optional
from loguru import logger
from dotenv import load_dotenv

class ConfigValidator:
    """Validate and manage system configuration"""
    
    def __init__(self):
        load_dotenv()
        self.config = {}
        self.errors = []
        self.warnings = []
    
    def validate_twitter_config(self) -> bool:
        """Validate Twitter API configuration"""
        required_keys = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET', 
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET'
        ]
        
        missing = []
        for key in required_keys:
            value = os.getenv(key)
            if not value:
                missing.append(key)
            else:
                self.config[key] = value
        
        if missing:
            self.errors.append(f"Missing Twitter API keys: {', '.join(missing)}")
            return False
        
        logger.success("✅ Twitter API configuration valid")
        return True
    
    def validate_openai_config(self) -> bool:
        """Validate OpenAI API configuration"""
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            self.warnings.append("OpenAI API key not found - will use rule-based transformation")
            return False
        
        self.config['OPENAI_API_KEY'] = openai_key
        logger.success("✅ OpenAI API configuration valid")
        return True
    
    def validate_instagram_config(self) -> bool:
        """Validate Instagram configuration"""
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            self.warnings.append("Instagram credentials not found - will use public scraping only")
            return False
        
        self.config['INSTAGRAM_USERNAME'] = username
        self.config['INSTAGRAM_PASSWORD'] = password
        logger.success("✅ Instagram credentials configured")
        return True
    
    def get_target_users(self) -> List[str]:
        """Get target Instagram users"""
        users_env = os.getenv('TARGET_INSTAGRAM_USERS', 'edhonour')
        users = [user.strip() for user in users_env.split(',')]
        
        logger.info(f"📸 Target users: {', '.join(users)}")
        return users
    
    def get_system_config(self) -> Dict:
        """Get system configuration"""
        return {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_videos_per_user': int(os.getenv('MAX_VIDEOS_PER_USER', '3')),
            'rate_limit_delay': int(os.getenv('RATE_LIMIT_DELAY', '5')),
            'target_users': self.get_target_users()
        }
    
    def validate_all(self) -> bool:
        """Validate all configuration"""
        logger.info("🔍 Validating system configuration...")
        
        # Required validations
        twitter_valid = self.validate_twitter_config()
        
        # Optional validations
        self.validate_openai_config()
        self.validate_instagram_config()
        
        # Print warnings
        for warning in self.warnings:
            logger.warning(f"⚠️ {warning}")
        
        # Print errors
        for error in self.errors:
            logger.error(f"❌ {error}")
        
        if not twitter_valid:
            logger.error("❌ Twitter API configuration is required for posting")
            return False
        
        logger.success("✅ Configuration validation complete")
        return True
    
    def print_config_status(self):
        """Print configuration status"""
        print("\n" + "="*60)
        print("🔧 SYSTEM CONFIGURATION STATUS")
        print("="*60)
        
        # Twitter
        if 'TWITTER_API_KEY' in self.config:
            print("✅ Twitter API: Configured")
        else:
            print("❌ Twitter API: Missing (Required)")
        
        # OpenAI
        if 'OPENAI_API_KEY' in self.config:
            print("✅ OpenAI API: Configured")
        else:
            print("⚠️ OpenAI API: Not configured (Optional)")
        
        # Instagram
        if 'INSTAGRAM_USERNAME' in self.config:
            print("✅ Instagram: Credentials configured")
        else:
            print("⚠️ Instagram: No credentials (Public scraping only)")
        
        # System settings
        sys_config = self.get_system_config()
        print(f"📊 Max videos per user: {sys_config['max_videos_per_user']}")
        print(f"⏱️ Rate limit delay: {sys_config['rate_limit_delay']}s")
        print(f"👥 Target users: {', '.join(sys_config['target_users'])}")
        
        print("="*60)

def check_system_ready() -> bool:
    """Check if system is ready to run"""
    validator = ConfigValidator()
    
    if validator.validate_all():
        validator.print_config_status()
        return True
    else:
        validator.print_config_status()
        print("\n❌ System not ready. Please fix configuration errors.")
        return False

if __name__ == "__main__":
    check_system_ready()
