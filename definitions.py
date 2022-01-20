import os
from pathlib import Path

ALGO_FACTORY_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = str(Path(ALGO_FACTORY_ROOT_DIR).parent)
