# backend/__init__.py  (create this file if missing)
import sys
from pathlib import Path

# Add project root (one level above backend) to sys.path
root_path = Path(__file__).resolve().parent.parent
root_str = str(root_path)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
