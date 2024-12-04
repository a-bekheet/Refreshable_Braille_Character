"""
Configuration Management Module
Handles loading, saving, and accessing application configuration settings
"""

import json
import logging
from typing import Any, Dict
from pathlib import Path

class Configuration:
    """Manages application configuration settings with file persistence."""
    
    DEFAULT_CONFIG = {
        "char_delay": 3000,
        "servo_delay": 750,
        "dual_servo_mode": True,
        "debug_mode": False,
        "theme": "default"
    }

    def __init__(self, config_file: str = "braille_config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
        logging.debug("Configuration initialized")

    def load_config(self) -> None:
        """Load configuration from file, creating default if none exists."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    logging.debug("Configuration loaded from file")
            else:
                self.save_config()
                logging.info("Created new configuration file with defaults")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            logging.info("Using default configuration")

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
                logging.debug("Configuration saved to file")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key (str): Configuration key
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        return self.config.get(key, default if default is not None else self.DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value and save to file.
        
        Args:
            key (str): Configuration key
            value (Any): Value to set
        """
        if key in self.DEFAULT_CONFIG or key in self.config:
            self.config[key] = value
            self.save_config()
            logging.debug(f"Configuration updated: {key} = {value}")
        else:
            logging.warning(f"Attempted to set unknown configuration key: {key}")

    def get_all(self) -> Dict[str, Any]:
        """
        Get complete configuration dictionary.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        return self.config.copy()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        logging.info("Configuration reset to defaults")

    def validate_config(self) -> bool:
        """
        Validate current configuration against defaults.
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            for key, default_value in self.DEFAULT_CONFIG.items():
                if key not in self.config:
                    logging.warning(f"Missing configuration key: {key}")
                    return False
                if not isinstance(self.config[key], type(default_value)):
                    logging.warning(f"Invalid type for configuration key: {key}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Configuration validation error: {e}")
            return False