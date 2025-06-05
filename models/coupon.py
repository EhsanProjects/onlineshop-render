from datetime import datetime, timedelta
from sqlalchemy import Column, Date, ForeignKey, Integer, String, DateTime, Boolean
from extensions import db
from sqlalchemy.orm import backref
def default_expiration_date():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day)

class Coupon(db.Model):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, unique=True)
    discount_percent = Column(Integer, nullable=False)
    start_date = Column(Date, default=default_expiration_date, nullable=False)
    end_date = Column(Date, default=default_expiration_date, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    usage_limit = Column(Integer, default=0)
    used_count = Column(Integer, default=0)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    min_order = Column(Integer)

     # Define relationships
    product = db.relationship('Product', backref='coupons')
    user = db.relationship("User", backref=backref('coupons', lazy='dynamic'))

    def __repr__(self):
        return f"<Coupon code={self.code}, discount_percent={self.discount_percent}, expiration_date={self.expiration_date}>"
