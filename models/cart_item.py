from sqlalchemy import *
from  extensions import db


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    quantity = Column(Integer)

    product = db.relationship("Product", backref='cart_items')
    cart = db.relationship("Cart", backref='cart_items')


    # name = Column(String, unique=True, nullable=False, index=True)
    # description = Column(String, nullable=False, index=True)
    # price = Column(Integer, nullable=False, index=True)
    # active = Column(Integer, nullable=False, index=True)
