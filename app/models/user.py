from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    follow_id = Column(Integer, ForeignKey("users.id"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)