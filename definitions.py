import os
from pathlib import Path

ALGO_COMPONENTS_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = str(Path(ALGO_COMPONENTS_ROOT_DIR).parent)
GLOBAL_CONFIG = os.path.join(ROOT_DIR, "config", "config.ini")


