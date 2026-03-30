from fastapi import FastAPI
from app.api import user, post, feed
from app.core.database import Base, engine
from app.models.user import User  # import 所有 model
from app.models.post import Post  # 如果有 post model
from app.models.user import User, Follow

# 🔑 建立資料表
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/users")
app.include_router(post.router, prefix="/posts")
app.include_router(feed.router, prefix="/feed")


@app.get("/")
def root():
    return {"message": "Feed system running"}