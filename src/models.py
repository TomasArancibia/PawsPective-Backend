from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20))
    age = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "name": self.name,
            "lastname": self.lastname,
            "age": self.age
        }


class Follower(db.Model):
    __tablename__ = "follower"
    id = db.Column(db.Integer, primary_key=True)
    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def serialize(self):
        return {
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id
        }


class Feed(db.Model):
    __tablename__ = "feed"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type
        }


class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "country": self.country
        }


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(400), nullable=False)
    likecount = db.Column(db.Integer)
    source_url = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.Integer, db.ForeignKey("location.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feed_id  = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "like_count": self.likecount,
            "location": self.location,
            "date": self.date,
            "source_url": self.source_url
        }


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400), nullable=True)
    author_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id  = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "post_id": self.post_id
        }


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "post_id": self.post_id
        }


class Like(db.Model):
    __tablename__ = "like"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id
        }

