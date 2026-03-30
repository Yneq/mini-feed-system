from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.post import Post
from app.models.user import Follow
from app.core.redis import redis_client  # 🔥 新增

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}/feed")
def get_feed(user_id: int, db: Session = Depends(get_db)):
    from app.models.user import User

    # 1️⃣ user 存在檢查
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ 🔥 先從 Redis 拿（快）
    post_ids = redis_client.lrange(f"feed:{user_id}", 0, 20)

    if post_ids:
        posts = db.query(Post).filter(Post.id.in_(post_ids)).all()
        return [
            {"post_id": p.id, "user_id": p.user_id, "content": p.content}
            for p in posts
        ]

    # 3️⃣ 🔁 fallback
    following = db.query(Follow.follow_id).filter(Follow.user_id == user_id)
    user_ids = [user_id] + [f.follow_id for f in following]

    posts = db.query(Post).filter(
        Post.user_id.in_(user_ids)
    ).order_by(Post.created_at.desc()).all()

    return [
        {"post_id": p.id, "user_id": p.user_id, "content": p.content, "created_at": p.created_at}
        for p in posts
    ]