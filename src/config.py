"""
Configuration management for LinkedIn Post Automation
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

class Config:
    """Configuration manager for the LinkedIn post automation system."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
                
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_newsletter_sources(self) -> Dict[str, Any]:
        """Get newsletter sources configuration."""
        return self.get('newsletter_sources', {})
    
    def get_content_processing(self) -> Dict[str, Any]:
        """Get content processing configuration."""
        return self.get('content_processing', {})
    
    def get_post_generation(self) -> Dict[str, Any]:
        """Get post generation configuration."""
        return self.get('post_generation', {})
    
    def get_scheduling(self) -> Dict[str, Any]:
        """Get scheduling configuration."""
        return self.get('scheduling', {})
    
    def get_linkedin_config(self) -> Dict[str, Any]:
        """Get LinkedIn API configuration."""
        return self.get('linkedin', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return self.get('monitoring', {})
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self._config.copy()

# Global configuration instance
config = Config()
