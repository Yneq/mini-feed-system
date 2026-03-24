from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import time

DATABASE_URL = "postgresql://user:password@db:5432/feed_db"

# retry 直到 DB 可以連線
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        print("✅ DB connected")
        break
    except Exception:
        print("⏳ DB not ready, retrying...")
        time.sleep(2)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()