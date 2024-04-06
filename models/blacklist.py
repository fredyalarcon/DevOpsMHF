from marshmallow import fields
from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sqlalchemy import Column, DateTime, func, UniqueConstraint, Integer

class BlackList(db.Model):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    idApp = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    ip = db.Column(db.String(120), nullable=False)
    createdAt = db.Column(DateTime(timezone=True), server_default=func.now(), default=func.now(), nullable=False)
    UniqueConstraint(email, name='uq_blacklist_email')
    
    __mapper_args__ = {
        "polymorphic_identity": "blacklist",
    }

class BlackListSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BlackList
        include_relationships = True
        load_instance = True

    id = fields.Integer(required=True)
    idApp = fields.String(required=True)
    email = fields.String(required=True)
    description = fields.String(required=False)
    ip = fields.String(required=True)
    createdAt = fields.DateTime(required=True)