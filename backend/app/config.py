import os

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")