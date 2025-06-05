import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from extensions import db

class Rate(db.Model):
    __tablename__ = "rate"
    id = Column(Integer, primary_key=True)
    therate= Column(Integer,nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = db.relationship("Product", backref='rate')
    comment = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref='rate')

   
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    modified_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))
    deleted_at = Column(DateTime,nullable=True)

    
    
    def __repr__(self):
        return f"<Rate id={self.id}, product_id={self.product_id},user_id={self.user_id} created_at={self.created_at}>"


