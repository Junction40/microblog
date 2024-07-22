from app import login, db, app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa # General purpose database functions and classes such as types and query building helpers
import sqlalchemy.orm as so # Support for using models
from app import db
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)

# This class inherits from db.Model, a base class for all models from Flask-SQLAlchemy
# Represent users stored in the database
class User(UserMixin, db.Model):
    # Type declaration also makes values required/non-nullable
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256)) # 'Optional' allows for empty or nullable
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers',
        passive_deletes=True)
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following',
        passive_deletes=True)
    
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author', passive_deletes=True) # This is not an actual database field, but a high-level view of the relationship between users and posts, and for that reason it isn't in the database diagram
    
    # Generates a password hash for the current/'self' user's input password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Compares the current/'self' user's stored password hash with the input password hashed
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Generates avatars for unique emails
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    # Follower/Following functionality
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    # Return all the posts of user the users they are following
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            # Join the relevant Authors to the Post table
            .join(Post.author.of_type(Author))
            # Join the relevant followers to each post (will be duplicates if there are multiple followers of one user)
            # Inner joins, and only preserve entries from the left side that have a matching entry on the right
            # The isouter=True option tells SQLAlchemy to use a left outer join instead, which preserves items from the left side that have no match on the right
            .join(Author.followers.of_type(Follower), isouter=True)
            # Since the join prior has at least one occurrence of every post a filter is required for both the followed users and author themself
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            # Eliminate duplicates in final results
            .group_by(Post)
            # Ordering posts by most recent
            .order_by(Post.timestamp.desc())
        )
    
    # Returns a JSON Web Token (JWT) as a string
    # jwt.encode params: payload, secret_key, algorithm
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    # Decodes JSON Web Token (JWT) 
    # If the token is valid, then the value of the reset_password key from the token's payload is the ID of the user, so user can be loaded and returned 
    # Static method allows it to be invoked directly from the class
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
        
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    author: so.Mapped[User] = so.relationship(back_populates='posts') # These two attributes (This and User.posts) allow the application to access the connected user and post entries

    # The __repr__ method tells Python how to print objects of this class, which is going to be useful for debugging
    def __repr__(self):
        return '<User {}>'.format(self.username)

# This decorator registers the function as the callback that Flask-Login will use to retrieve the user object based on the user ID stored in the session
# Automatically loads the user object from the database based on the user ID stored in the session
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))