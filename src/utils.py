import os
import json


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist.")
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config
