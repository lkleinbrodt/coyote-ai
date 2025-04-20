from datetime import date, datetime

import pytz

from backend.extensions import db

# Create Pacific timezone object
pacific = pytz.timezone("America/Los_Angeles")


class DailyFeeding(db.Model):
    """Tracks daily feeding amounts and targets for the dog"""

    __table_args__ = {"schema": "poppytracker"}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.Date,
        nullable=False,
        unique=True,
        default=lambda: datetime.now(pacific).date(),
    )
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    daily_target = db.Column(
        db.Float, nullable=False, default=3.0
    )  # Default target of 3.0 cups
    last_updated_by = db.Column(db.String(36), nullable=True)  # Store user ID
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(pacific),
        onupdate=lambda: datetime.now(pacific),
    )

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "total": self.total_amount,
            "target": self.daily_target,
            "last_updated_by": self.last_updated_by,
            "updated_at": self.updated_at.astimezone(pacific).isoformat(),
        }
