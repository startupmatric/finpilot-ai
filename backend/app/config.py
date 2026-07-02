import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# App
APP_NAME = os.getenv("APP_NAME", "FinPilot")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CORS - Add allowed origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# CSV Upload
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_CSV_MIME_TYPES = ["text/csv", "application/vnd.ms-excel"]

# Validation
MIN_AMOUNT = 0.01
MAX_AMOUNT = 1_000_000_000

# Validate required config
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY is not set. Chat features will not work.")
else:
    print(f"✅ GROQ_API_KEY configured. Using model: {GROQ_MODEL}")