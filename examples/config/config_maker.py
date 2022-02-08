import json
from dataclasses import dataclass


@dataclass
class Config:
    url: str
    user_name: str
    password: str
    school: str


def make_config():
    try:
        return Config(**json.load(open("config/config.json", encoding="utf-8")))
    except FileNotFoundError:
        raise FileNotFoundError(
            "Please create a config/config.json file (use "
            "config/config_template.json as a template)"
        )
