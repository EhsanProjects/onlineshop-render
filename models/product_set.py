import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from extensions import db

class ProductSet(db.Model):
    __tablename__ = "product_set"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    discount_id = Column(Integer, ForeignKey('product_discount.id'), nullable=True, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    deleted_at = Column(DateTime, nullable=True)

    # Define relationships
    product = db.relationship('Product', backref='product_sets')
    product_discount = db.relationship('ProductDiscount', backref='product_sets')

    def __repr__(self):
        return f"<ProductSet id={self.id}, product_id={self.product_id}, created_at={self.created_at}>"
