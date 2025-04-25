from datetime import date, datetime

from backend.extensions import db


class Feeding(db.Model):
    """Tracks individual feeding events"""

    __table_args__ = {"schema": "poppytracker"}

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    amount = db.Column(db.Float, nullable=False)
    last_updated_by = db.Column(db.String(36), nullable=True)  # Store user ID

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "date": self.timestamp.date().isoformat(),
            "amount": self.amount,
            "last_updated_by": self.last_updated_by,
        }


class DailyTarget(db.Model):
    """Tracks daily feeding targets"""

    __table_args__ = {"schema": "poppytracker"}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.Date,
        nullable=False,
        unique=True,
        default=lambda: datetime.utcnow().date(),
    )
    target = db.Column(
        db.Float, nullable=False, default=3.0
    )  # Default target of 3.0 cups
    last_updated_by = db.Column(db.String(36), nullable=True)  # Store user ID
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "target": self.target,
            "last_updated_by": self.last_updated_by,
            "updated_at": self.updated_at.isoformat(),
        }
