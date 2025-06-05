from sqlalchemy import *
from extensions import db, get_current_time


class Payment(db.Model):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    status = Column(String, default='pending')
    price = Column(Integer)
    token = Column(String)
    refid = Column(String)
    transaction_id = Column(String)
    card_pan = Column(String)
    # date_created = Column(String(15), default=get_current_time)
    date_created = Column(String(15), default=func.now())
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)

    amount_to_pay=Column(Integer)
    coupon_id = Column(Integer, ForeignKey('coupons.id'), nullable=True)
    coupon = db.relationship('Coupon', backref='payments')
    cart = db.relationship("Cart", backref='payments')   
    def get_status_persian(self):
        if self.status == 'pending':
            return "در انتظار پرداخت"

        if self.status == "success":
            return "پرداخت شده"

        if self.status == "failed":
            return "عدم موفق"