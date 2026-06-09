from config_manager import ConfigManager

cfg = ConfigManager("config.yaml")
print(cfg.get_nested("database", "name"))
print(cfg.get_nested("paths", "downloads"))
print(cfg.get_nested("missing_key", "fake", "not found"))