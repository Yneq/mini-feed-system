from sqlalchemy import Column, Integer
from app.core.database import Base

class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, primary_key=True)
    followee_id = Column(Integer, primary_key=True)