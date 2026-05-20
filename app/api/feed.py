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
def get_feed(
    user_id: int,
    cursor: float = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # check user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # first page
    max_score = "+inf" if cursor is None else f"({cursor}"

    # Redis ZSET query
    post_ids = redis_client.zrevrangebyscore(
        f"feed:user:{user_id}",
        max_score,
        "-inf",
        start=0,
        num=limit
    )

    feed = []

    for pid in post_ids:
        post_data = redis_client.hgetall(f"post:{pid}")

        if post_data:
            feed.append(post_data)

    # next cursor
    next_cursor = None

    if post_ids:
        next_cursor = redis_client.zscore(
            f"feed:user:{user_id}",
            post_ids[-1]
        )

    return {
        "items": feed,
        "next_cursor": next_cursor
    }

