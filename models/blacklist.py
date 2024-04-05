from marshmallow import fields
from ..models import db
from sqlalchemy import Enum, Column, DateTime, func, CheckConstraint

class BlackList(db.Model):
    __tablename__ = "blacklist"
    idApp = db.Column(db.String(120), primary_key=True)
    email = db.Column(db.String(120))
    description = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(120))
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

    idApp = fields.String(required=True)
    email = fields.String(required=True)
    description = fields.String(required=False)
    ip = fields.String(required=True)
    createdAt = fields.DateTime(required=True)