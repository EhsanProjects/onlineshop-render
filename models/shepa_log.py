# models/shepa_log.py
from datetime import datetime, UTC
from sqlalchemy import *
from  extensions import db
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
# from datetime import datetime
class ShepaStatusLog(db.Model):
    __tablename__ = 'shepa_status_logs'
    id = Column(Integer, primary_key=True)
    status = Column(String(10))  # 'UP' or 'DOWN'
    message = Column(String(255))
    # checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", backref=backref('shepa_status_logs', lazy='dynamic')) # Optional: if you want to access log.user.username
# ----------------------------------------------------


def __repr__(self):
        return f"<ShepaStatusLog id={self.id}> user_id={self.user_id}>"