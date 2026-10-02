import os

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MONGODB CONFIGURATION
# ============================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "voiceshield"
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    "uploads"
)