import json, os

def write_report(path: str, content: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(content, f, indent=2)
