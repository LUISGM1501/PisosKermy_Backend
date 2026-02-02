from ..database import db
from ..models import Tag


class TagRepository:
    @staticmethod
    def get_all():
        return Tag.query.order_by(Tag.name).all()

    @staticmethod
    def get_by_id(tag_id):
        return db.session.get(Tag, tag_id)

    @staticmethod
    def get_by_name(name):
        return Tag.query.filter_by(name=name).first()

    @staticmethod
    def create(name):
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return tag

    @staticmethod
    def update(tag, name):
        tag.name = name
        db.session.commit()
        return tag

    @staticmethod
    def delete(tag):
        db.session.delete(tag)
        db.session.commit()