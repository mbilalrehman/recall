import os

CONFIG_DIR = os.path.expanduser("~/.recall")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config")

def get_token() -> str | None:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            for line in f:
                if line.startswith("TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None

def get_email() -> str | None:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            for line in f:
                if line.startswith("EMAIL="):
                    return line.strip().split("=", 1)[1]
    return None

def save_token(token: str, email: str):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        f.write(f"TOKEN={token}\n")
        f.write(f"EMAIL={email}\n")

def clear_token():
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)