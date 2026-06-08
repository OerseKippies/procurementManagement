import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PROCM_DATA_DIR", BASE_DIR / "data"))
DATABASE_PATH = Path(os.environ.get("PROCM_DATABASE", DATA_DIR / "procm.sqlite3"))
SECRET_KEY = os.environ.get("PROCM_SECRET_KEY", "dev-procm-change-in-production")
FETCH_TIMEOUT = int(os.environ.get("PROCM_FETCH_TIMEOUT", "15"))
USER_AGENT = "OerseKippies-procM/1.0 (+local-intake)"
