import os

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return dict(line.strip().split('=') for line in f if '=' in line and not line.strip().startswith('#'))
        return {}

    def get(self):
        return self.config

    def save(self):
        with open(self.config_path, 'w') as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")