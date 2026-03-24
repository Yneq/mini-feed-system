from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.post import Post

router = APIRouter()

@router.post("/")
def create_post(user_id: int, content: str, db: Session = Depends(get_db)):
    post = Post(user_id=user_id, content=content)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post