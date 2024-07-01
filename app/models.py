from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa # General purpose database functions and classes such as types and query building helpers
import sqlalchemy.orm as so # Support for using models
from app import db
from flask_login import UserMixin

# This class inherits from db.Model, a base class for all models from Flask-SQLAlchemy
# Represent users stored in the database
class User(UserMixin, db.Model):
    # Type declaration also makes values required/non-nullable
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256)) # 'Optional' allows for empty or nullable
    
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author') # This is not an actual database field, but a high-level view of the relationship between users and posts, and for that reason it isn't in the database diagram
    
    # Generates a password hash for the current/'self' user's input password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Compares the current/'self' user's stored password hash with the input password hashed
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts') # These two attributes (This and User.posts) allow the application to access the connected user and post entries

    # The __repr__ method tells Python how to print objects of this class, which is going to be useful for debugging
    def __repr__(self):
        return '<User {}>'.format(self.username)

# This decorator registers the function as the callback that Flask-Login will use to retrieve the user object based on the user ID stored in the session
# Automatically loads the user object from the database based on the user ID stored in the session
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))