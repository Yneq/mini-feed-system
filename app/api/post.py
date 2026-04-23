from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.post import Post
from app.models.user import Follow
from app.core.redis import redis_client

router = APIRouter()

from app.core.redis import redis_client
from app.models.user import Follow

@router.post("/")
def create_post(user_id: int, content: str, db: Session = Depends(get_db)):
    # 1️⃣ 寫 DB
    post = Post(user_id=user_id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)

    # 2️⃣ 🔥 寫 Redis（post cache）
    redis_client.hset(f"post:{post.id}", mapping={
        "id": post.id,
        "user_id": post.user_id,
        "content": post.content,
        "created_at": str(post.created_at)
    })

    # 3️⃣ 🔥 fan-out
    followers = db.query(Follow).filter(Follow.follow_id == user_id).all()

    for f in followers:
        redis_client.lpush(f"feed:user:{f.user_id}", post.id)

    # 自己也要
    redis_client.lpush(f"feed:user:{user_id}", post.id)

    return post