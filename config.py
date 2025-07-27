"""
Configuration management for the Instagram-to-Social Media Agent System
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Twitter API
    twitter_api_key: str = Field(..., env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(..., env="TWITTER_API_SECRET")
    twitter_access_token: str = Field(..., env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: str = Field(..., env="TWITTER_ACCESS_TOKEN_SECRET")
    twitter_bearer_token: str = Field(..., env="TWITTER_BEARER_TOKEN")
    
    # LinkedIn API
    linkedin_client_id: str = Field(..., env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: str = Field(..., env="LINKEDIN_CLIENT_SECRET")
    linkedin_access_token: str = Field(..., env="LINKEDIN_ACCESS_TOKEN")
    
    # Instagram Settings
    instagram_username: Optional[str] = Field(None, env="INSTAGRAM_USERNAME")
    instagram_password: Optional[str] = Field(None, env="INSTAGRAM_PASSWORD")
    target_instagram_users: List[str] = Field(
        default_factory=lambda: ["user1", "user2"], 
        env="TARGET_INSTAGRAM_USERS"
    )
    
    # Database
    database_url: str = Field("sqlite:///./agent_system.db", env="DATABASE_URL")
    
    # Redis (for Celery)
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Application Settings
    max_videos_per_user: int = Field(5, env="MAX_VIDEOS_PER_USER")
    content_check_interval: int = Field(3600, env="CONTENT_CHECK_INTERVAL")  # seconds
    
    # Content Generation Settings
    max_twitter_length: int = 280
    max_linkedin_length: int = 3000
    
    # File Storage
    storage_path: str = Field("./storage", env="STORAGE_PATH")
    temp_path: str = Field("./temp", env="TEMP_PATH")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("agent_system.log", env="LOG_FILE")
    
    # Web Interface
    web_host: str = Field("0.0.0.0", env="WEB_HOST")
    web_port: int = Field(8000, env="WEB_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Platform-specific configurations
PLATFORM_CONFIGS = {
    "twitter": {
        "max_length": settings.max_twitter_length,
        "hashtag_limit": 10,
        "media_types": ["image", "video"],
        "video_max_duration": 140,  # seconds
        "video_max_size": 512 * 1024 * 1024,  # 512MB
    },
    "linkedin": {
        "max_length": settings.max_linkedin_length,
        "hashtag_limit": 30,
        "media_types": ["image", "video"],
        "video_max_duration": 600,  # seconds
        "video_max_size": 5 * 1024 * 1024 * 1024,  # 5GB
    }
}

# Content transformation prompts
CONTENT_PROMPTS = {
    "twitter": """
    Transform this Instagram video content into an engaging Twitter post.
    
    Requirements:
    - Maximum 280 characters
    - Include relevant hashtags (max 10)
    - Make it engaging and shareable
    - Maintain the core message
    - Use Twitter-appropriate tone
    
    Original content: {content}
    Video description: {description}
    """,
    
    "linkedin": """
    Transform this Instagram video content into a professional LinkedIn post.
    
    Requirements:
    - Professional tone
    - Include relevant industry hashtags
    - Add value for professional audience
    - Encourage engagement
    - Maximum 3000 characters
    
    Original content: {content}
    Video description: {description}
    """
}
