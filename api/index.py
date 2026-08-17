import os
import sys


# ============================================================
# ADD BACKEND DIRECTORY TO PYTHON PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    'backend'
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(
        0,
        BACKEND_DIR
    )


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

from app import create_app

app = create_app()