import os
import json

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return json.load(file)
        return {}
        
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self._save_config()

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)