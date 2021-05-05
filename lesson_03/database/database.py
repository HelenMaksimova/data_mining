from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models


class Database:

    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)
        self.session = None

    def add_post(self, data):
        self.session = self.maker()
        print(1)
        post = self.session.query(models.Post).filter(models.Post.id == data['id']).first()
        if post is None:
            post = models.Post(
                id=data['id'],
                title=data['title'],
                url=data['url'],
                img_url=data['first_img_link'],
                public_date=data['post_time'],
                author_id=data['author_id']
            )
            self.session.add(post)
        self._add_author((data['author_id'], data['author_link'], data['author_name']))
        self._add_comments(data['comments'], data['id'])
        self._add_tags(data['tags'], data['id'])
        self.session.commit()
        self.session.close()

    def _add_author(self, data):
        author = self.session.query(models.Author).filter(models.Author.id == data[0]).first()
        if author is None:
            author = models.Author(
                id=data[0],
                url=data[1],
                name=data[2])
            self.session.add(author)

    def _add_comments(self, comments, post_id):
        for comment in comments:
            self._add_author((comment['author_id'], comment['author_link'], comment['author_name']))
            exist_comment = self.session.query(models.Comment).filter(models.Comment.id == comment['id']).first()
            if exist_comment is None:
                exist_comment = models.Comment(
                    id=comment['id'],
                    parent_id=comment['parent_id'],
                    post_id=post_id,
                    text=comment['message'],
                    author_id=comment['author_id']
                )
                self.session.add(exist_comment)

    def _add_tags(self, tags, post_id):
        for tag in tags:
            exist_tag = self.session.query(models.Tag).filter(models.Tag.url == tag['url']).first()
            if exist_tag is None:
                exist_tag = models.Tag(
                    name=tag['name'],
                    url=tag['url']
                )
                self.session.add(exist_tag)
            exist_relay = self.session.query(models.tag_post).filter_by(post_id=post_id, tag_id=exist_tag.id).first()
            if exist_relay is None:
                exist_relay = models.tag_post.insert().values(post_id=post_id, tag_id=exist_tag.id)
                self.session.execute(exist_relay)
