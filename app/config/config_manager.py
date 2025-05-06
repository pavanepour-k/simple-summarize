from app.config.settings import settings
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    
    def __init__(self):
        self.model_paths = {}
        self.plan_limits = {}
        self.time_limits = {}
        self._load_configurations()
    
    @classmethod
    def instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_configurations(self):
        """Load all configuration files"""
        self._load_model_paths()
        self._load_plan_limits()
        self._load_time_limits()
    
    def _load_model_paths(self):
        """Load model paths from configuration file"""
        try:
            config_file = os.path.join("app", "config", "models.json")
            with open(config_file, 'r') as file:
                self.model_paths = json.load(file)
        except Exception as e:
            logger.error(f"Failed to load model paths: {str(e)}")
            # Default model paths as fallback
            self.model_paths = {
                "en": "facebook/bart-large-cnn",
                "ko": "Helsinki-NLP/opus-mt-ko-en",
                "ja": "sonoisa/t5-base-japanese-summarization",
                "fr": "facebook/bart-large-cnn",
                "de": "facebook/bart-large-cnn"
            }
    
    def _load_plan_limits(self):
        """Load API usage limits by plan"""
        try:
            config_file = os.path.join("app", "config", "plan_limits.json")
            with open(config_file, 'r') as file:
                self.plan_limits = json.load(file)
        except Exception as e:
            logger.error(f"Failed to load plan limits: {str(e)}")
            # Default plan limits as fallback
            self.plan_limits = {
                "user": {"free": 1000, "pro": 5000, "enterprise": 10000},
                "pro": {"free": 1000, "pro": 10000, "enterprise": 20000},
                "admin": {"free": 1000, "pro": 10000, "enterprise": 50000}
            }
    
    def _load_time_limits(self):
        """Load time-based API limits"""
        # These could be loaded from a file as well
        self.time_limits = {
            "user": {0: 50, 6: 200, 12: 300, 18: 150},
            "pro": {0: 100, 6: 500, 12: 1000, 18: 800}
        }
    
    def get_model_for_language(self, lang: str) -> str:
        """Get the appropriate model path for a language"""
        return self.model_paths.get(lang, self.model_paths.get("en"))
    
    def get_plan_limit(self, role: str, plan: str) -> int:
        """Get the API call limit for a role and plan combination"""
        role = role.lower()
        plan = plan.lower()
        role_limits = self.plan_limits.get(role, self.plan_limits.get("user", {}))
        return role_limits.get(plan, role_limits.get("free", 1000))
    
    def get_time_based_limit(self, role: str, plan: str, hour: int) -> int:
        """Get time-based API call limit"""
        role = role.lower()
        time_limits = self.time_limits.get(role, self.time_limits.get("user", {}))
        
        # Find the closest time bracket
        keys = sorted(time_limits.keys())
        closest_key = keys[0]
        
        for key in keys:
            if key <= hour:
                closest_key = key
            else:
                break
                
        return time_limits.get(closest_key, 100)  # Default: 100 calls
