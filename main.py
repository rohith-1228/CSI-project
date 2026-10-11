"""
Root entry point proxy for CyberSaathi FastAPI application.
Ensures that regardless of whether uvicorn is invoked as:
  uvicorn main:app
  uvicorn backend.app.main:app
  uvicorn app.main:app
it always loads the exact same production FastAPI application instance.
"""

import sys
import os
from pathlib import Path

# Add project root and backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
for p in [str(ROOT_DIR), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port)
