from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.user import User, Follow
from app.models.post import Post
from datetime import datetime

router = APIRouter()
redis_client = Redis(host="redis", port=6379, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Get feed from Redis
# -----------------------------
@router.get("/{user_id}/feed")
def get_feed(user_id: int, db: Session = Depends(get_db)):
    # 確認 user 存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 取 Redis feed list
    post_ids = redis_client.lrange(f"feed:user:{user_id}", 0, 49)
    feed = []
    for pid in post_ids:
        post_data = redis_client.hgetall(f"post:{pid}")
        if post_data:
            feed.append(post_data)

    return feed

