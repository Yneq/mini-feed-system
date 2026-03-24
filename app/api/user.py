from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, Follow

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Create user
# -----------------------------
@router.post("/")
def create_user(name: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# -----------------------------
# Follow user
# -----------------------------
@router.post("/follow")
def follow_user(user_id: int, follow_id: int, db: Session = Depends(get_db)):
    if user_id == follow_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    user = db.query(User).filter(User.id == user_id).first()
    target = db.query(User).filter(User.id == follow_id).first()
    if not user or not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(Follow).filter(Follow.user_id==user_id, Follow.follow_id==follow_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already following")

    follow = Follow(user_id=user_id, follow_id=follow_id)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return {"message": f"{user.name} is now following {target.name}"}


# -----------------------------
# Unfollow user
# -----------------------------
@router.post("/unfollow")
def unfollow_user(user_id: int, follow_id: int, db: Session = Depends(get_db)):
    follow = db.query(Follow).filter(Follow.user_id==user_id, Follow.follow_id==follow_id).first()
    if not follow:
        raise HTTPException(status_code=404, detail="Follow relationship not found")
    db.delete(follow)
    db.commit()
    return {"message": "Unfollowed successfully"}


# -----------------------------
# List followers of a user
# -----------------------------
@router.get("/{user_id}/followers")
def get_followers(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    followers = db.query(Follow).filter(Follow.follow_id == user_id).all()
    return [{"user_id": f.user_id} for f in followers]


# -----------------------------
# List users the user is following
# -----------------------------
@router.get("/{user_id}/following")
def get_following(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    following = db.query(Follow).filter(Follow.user_id == user_id).all()
    return [{"follow_id": f.follow_id} for f in following]