import sys
import os
from pathlib import Path

# Add project root and backend to sys.path
_backend_dir = Path(__file__).resolve().parent / "backend"
_project_root = _backend_dir.parent
sys.path.insert(0, str(_backend_dir))
sys.path.insert(0, str(_project_root))

print(f"PYTHONPATH: {sys.path}")

try:
    from app.main import app
    print("App imported successfully")
    app.run(port=8080, debug=True)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
