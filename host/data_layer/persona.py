import yaml
from pathlib import Path
 
_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "persona.yaml"
 
 
def load_persona() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)
 