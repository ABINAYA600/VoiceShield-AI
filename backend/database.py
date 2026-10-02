from pymongo import MongoClient

from config import (
    MONGODB_URI,
    DATABASE_NAME
)


# ============================================================
# MONGODB CLIENT
# ============================================================

client = MongoClient(
    MONGODB_URI
)


# ============================================================
# DATABASE
# ============================================================

db = client[
    DATABASE_NAME
]


# ============================================================
# COLLECTIONS
# ============================================================

trusted_voices_collection = db[
    "trusted_voices"
]

analysis_collection = db[
    "analysis_history"
]

alerts_collection = db[
    "alerts"
]


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

def test_database():

    try:

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB connected successfully!"
        )

        return True

    except Exception as e:

        print(
            "MongoDB connection failed:"
        )

        print(e)

        return False