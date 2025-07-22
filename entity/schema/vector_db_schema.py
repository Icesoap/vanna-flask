from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from entity.models import VectorDB


class VectorDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VectorDB
