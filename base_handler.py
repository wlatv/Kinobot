import os
import json
from config import ADMIN_IDS

def is_admin(user_id):
    return user_id in ADMIN_IDS

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)