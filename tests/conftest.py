import os
import sys
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")

# Ensure root and openyantra package are in sys.path for test imports
root_dir = Path(__file__).resolve().parent.parent
openyantra_dir = root_dir / "openyantra"

for path_str in (str(openyantra_dir), str(root_dir)):
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
