from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import StoreModel, ItemModel
from models.tag import TagModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags", 'tags', description="Operations on tags")

@blp.route('/store/<int:store_id>/tag')
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag


@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag

    @blp.response(201, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {'message': 'Tag removed from item', 'item': item, 'tag':  tag}

@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(200, TagSchema)
    @blp.alt_response( 404, description="Tag not found.", example={"message": "Tag not found."})
    @blp.alt_response(400, description="Tag cannot be deleted. Make sure tag is not associated with any items first.", example={"message": "Tag cannot be deleted. Make sure tag is not associated with any items first."})
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items:
            abort(400, message="Tag cannot be deleted. Make sure tag is not associated with any items first.")
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted."}