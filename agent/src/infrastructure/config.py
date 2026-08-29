import os


def load_config():
    return {"API_URL": os.getenv("API_URL", "http://localhost")}
