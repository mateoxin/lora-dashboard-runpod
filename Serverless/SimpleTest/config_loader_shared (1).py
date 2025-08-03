"""
Shared configuration loader for Testing tools.
"""

import os
from pathlib import Path
from typing import Optional, Dict


def load_config_file(config_path: Optional[str] = None) -> Dict[str, str]:
    """
    Load configuration from config.env file.
    
    Args:
        config_path: Path to config file. If None, searches for config.env in current directory.
        
    Returns:
        Dictionary with configuration key-value pairs
    """
    if config_path is None:
        # Look for config.env in current directory
        current_dir = Path(__file__).parent
        config_path = current_dir / "config.env"
        
        if not config_path.exists():
            return {}
    
    config = {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    config[key] = value
                    
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading config file {config_path}: {e}")
    
    return config


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value with fallback priority:
    1. Environment variable
    2. Config file
    3. Default value
    """
    # First try environment variable
    value = os.getenv(key)
    if value is not None:
        return value
    
    # Then try config file
    config = load_config_file()
    value = config.get(key)
    if value is not None:
        return value
    
    # Finally return default
    return default


def get_runpod_token() -> str:
    """
    Get RunPod API token from configuration.
    
    Returns:
        RunPod API token
        
    Raises:
        ValueError: If token is not found or is a placeholder
    """
    token = get_config_value('RUNPOD_TOKEN')
    
    if not token:
        raise ValueError(
            "RUNPOD_TOKEN not found. Please copy config.env.template to config.env and set your token."
        )
    
    if token in ['YOUR_RUNPOD_TOKEN_HERE', 'your_runpod_api_token_here', 'your_runpod_token_here']:
        raise ValueError(
            "RUNPOD_TOKEN is still a placeholder. Please set your actual RunPod API token in config.env"
        )
    
    return token


def get_runpod_endpoint_id() -> Optional[str]:
    """Get RunPod Endpoint ID from configuration."""
    endpoint_id = get_config_value('RUNPOD_ENDPOINT_ID')
    
    if endpoint_id and endpoint_id not in ['your_endpoint_id_here', 'YOUR_ENDPOINT_ID']:
        return endpoint_id
    
    return None 