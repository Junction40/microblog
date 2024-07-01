from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa # General purpose database functions and classes such as types and query building helpers
import sqlalchemy.orm as so # Support for using models
from app import db

# This class inherits from db.Model, a base class for all models from Flask-SQLAlchemy
# Represent users stored in the database
class User(db.Model):
    # Type declaration also makes values required/non-nullable
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256)) # 'Optional' allows for empty or nullable
    
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author') # This is not an actual database field, but a high-level view of the relationship between users and posts, and for that reason it isn't in the database diagram
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts') # These two attributes (This and User.posts) allow the application to access the connected user and post entries

    # The __repr__ method tells Python how to print objects of this class, which is going to be useful for debugging
    def __repr__(self):
        return '<User {}>'.format(self.username)