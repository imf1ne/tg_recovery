import yaml

with open("settings.yml", "r") as ymlfile:
    SETTINGS = yaml.safe_load(ymlfile)
