from datetime import datetime, timedelta
from sqlalchemy import Column, Date, Integer, DateTime, String, func
from extensions import db

def default_expiration_date():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day).date()

class ProductDiscount(db.Model):
    __tablename__ = "product_discount"
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False,default="Default")
    discountpercent = Column(Integer, nullable=False,unique=True, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    active = Column(Integer, nullable=False, index=True)
    expiration_date = Column(Date, default=default_expiration_date, nullable=False)

    def __repr__(self):
        return f"<ProductDiscount id={self.id}, discountpercent={self.discountpercent}, created_at={self.created_at}>"
