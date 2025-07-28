import json
from pathlib import Path

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def write_json(obj, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def read_persona_job(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)