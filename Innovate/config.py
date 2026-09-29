import os
class Config:
    SECRET_KEY = os.getenv("PULSEOPS_SECRET", "local-dev-only-change-me")
    DATABASE = os.getenv("PULSEOPS_DB", os.path.join(os.path.dirname(__file__), "pulseops.db"))
    DEBUG = os.getenv("PULSEOPS_DEBUG", "1") == "1"
    CORS_ORIGINS = os.getenv("PULSEOPS_CORS", "http://127.0.0.1:5000,http://localhost:5000").split(",")
