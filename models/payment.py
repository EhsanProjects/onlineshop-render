from sqlalchemy import *
from  extensions import db


class Payment(db.Model):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    status = Column(String, default="pending")
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    cart = db.relationship("Cart", backref='payments')



    # name = Column(String, unique=True, nullable=False, index=True)
    # description = Column(String, nullable=False, index=True)
    # price = Column(Integer, nullable=False, index=True)
    # active = Column(Integer, nullable=False, index=True)
