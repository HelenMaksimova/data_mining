from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Table,
    ForeignKey,
)

Base = declarative_base()

tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("post.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    url = Column(String, unique=True, nullable=False)
    img_url = Column(String, unique=False, nullable=True)
    public_date = Column(DateTime, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="posts")


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String(350), nullable=False, unique=False)


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String(350), nullable=False, unique=False)
    posts = relationship(Post, secondary=tag_post, backref="tags")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String(350), nullable=False, unique=False)
    parent_id = Column(Integer, unique=False, nullable=True)
    parent = relationship("Comment",
                          primaryjoin=id == parent_id,
                          foreign_keys=parent_id,
                          remote_side=id)
    children = relationship("Comment",
                            primaryjoin=parent_id == id,
                            foreign_keys=id,
                            remote_side=parent_id,
                            uselist=True)
    post_id = Column(Integer, ForeignKey("post.id"), unique=False, nullable=True)
    posts = relationship("Post", backref="comments")
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    author = relationship("Author", backref="comments")
