from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.post import Post
from app.models.user import Follow
from app.core.redis import redis_client

router = APIRouter()

@router.post("/")
def create_post(user_id: int, content: str, db: Session = Depends(get_db)):
    # 1️⃣ 寫 DB
    post = Post(user_id=user_id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)

    # 2️⃣ 找 followers
    followers = db.query(Follow).filter(Follow.follow_id == user_id).all()

    # 3️⃣ fan-out → 寫進 Redis feed
    for f in followers:
        redis_client.lpush(f"feed:{f.user_id}", post.id)

    # 自己也要看到自己的貼文
    redis_client.lpush(f"feed:{user_id}", post.id)

    return post