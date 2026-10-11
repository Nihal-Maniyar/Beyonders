"""Root entrypoint for LearnLoop AI FastAPI backend.

Guarantees seamless execution across all hosting platforms (Render, Railway, Heroku, Docker)
without requiring manual PYTHONPATH or directory flags.
"""

import os
import sys
from pathlib import Path

# Automatically insert src/ into sys.path
_src_dir = str(Path(__file__).resolve().parent / "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from learnloop.api.main import app

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port)
