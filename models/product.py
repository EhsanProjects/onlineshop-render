import datetime
from sqlalchemy import *
from  extensions import db
from sqlalchemy.orm import backref
class Product(db.Model):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    price = Column(Integer, nullable=False, index=True)
    active = Column(Integer, nullable=False, index=True)
    # Added
    category = Column(Integer,  nullable=False)
    # product_setID = Column(Integer,  nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC), nullable=False)
    owner = Column(String, nullable=False, default="admin")
def __repr__(self):
        return f"<Product id={self.id}>"