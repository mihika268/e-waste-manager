import os
from datetime import timedelta
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

_current_dir = os.path.dirname(
    os.path.dirname(__file__)
)

_backend_env = os.path.join(
    _current_dir,
    '.env'
)

if os.path.exists(_backend_env):
    load_dotenv(
        _backend_env,
        override=False
    )