"""
Configuration settings for LoRA Dashboard Backend
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    debug: bool = Field(default=False, description="Debug mode")
    mock_mode: bool = Field(default=False, description="Mock mode - use fake services for local testing")
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    
    # GPU and Process Management
    max_concurrent_jobs: int = Field(default=10, description="Maximum concurrent GPU jobs")
    gpu_timeout: int = Field(default=14400, description="GPU job timeout in seconds (4 hours)")
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # S3 Storage Configuration (RunPod Storage)
    s3_endpoint_url: str = Field(
        default="https://storage.runpod.io",
        description="S3 endpoint URL"
    )
    s3_access_key: str = Field(description="S3 access key")
    s3_secret_key: str = Field(description="S3 secret key") 
    s3_bucket: str = Field(description="S3 bucket name")
    s3_region: str = Field(default="us-east-1", description="S3 region")
    
    # File Paths
    workspace_path: str = Field(
        default="/workspace",
        description="Workspace directory path"
    )
    models_path: str = Field(
        default="/workspace/models",
        description="Models directory path"
    )
    output_path: str = Field(
        default="/workspace/output",
        description="Output directory path"
    )
    
    # AI Toolkit Configuration
    ai_toolkit_path: str = Field(
        default="/workspace/ai-toolkit",
        description="AI Toolkit installation path"
    )
    python_executable: str = Field(
        default="python3",
        description="Python executable for AI toolkit"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # CORS Settings
    cors_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 