# write a class called ConfigManager that accepts a file path and loads the YAML file into a self.config dictionary using yaml.safe_load.
import yaml

class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = {}
        self.load_config()
    #   add a get() to your class that accepts and returns the value from self.config

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_nested(self, key, nested_key, default=None):
        section = self.get(key)
        if section is None:
            return default
        return section.get(nested_key, default)

    def load_config(self):
        try:
            with open(self.file_path, 'r') as file:
                self.config = yaml.safe_load(file)
                print(f"Configuration loaded successfully from {self.file_path}")
        except Exception as e:
            print(f"Error loading configuration: {e}")