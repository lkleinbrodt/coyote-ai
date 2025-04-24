from datetime import date, datetime

import pytz

from backend.extensions import db

# Create Pacific timezone object for display conversions
pacific = pytz.timezone("America/Los_Angeles")


class Feeding(db.Model):
    """Tracks individual feeding events"""

    __table_args__ = {"schema": "poppytracker"}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.Date,
        nullable=False,
        default=lambda: datetime.now(pacific).date(),
    )
    amount = db.Column(db.Float, nullable=False)
    last_updated_by = db.Column(db.String(36), nullable=True)  # Store user ID
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(pacific),
        onupdate=lambda: datetime.now(pacific),
    )

    def to_dict(self):
        # Convert to Pacific time for display
        pacific_date = pytz.utc.localize(self.date).astimezone(pacific)
        pacific_updated_at = pytz.utc.localize(self.updated_at).astimezone(pacific)

        return {
            "id": self.id,
            "date": pacific_date.isoformat(),
            "amount": self.amount,
            "last_updated_by": self.last_updated_by,
            "updated_at": pacific_updated_at.isoformat(),
        }


class DailyTarget(db.Model):
    """Tracks daily feeding targets"""

    __table_args__ = {"schema": "poppytracker"}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.Date,
        nullable=False,
        unique=True,
        # Get current date in Pacific time but store as date without timezone
        default=lambda: datetime.now(pacific).date(),
    )
    target = db.Column(
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
        # Convert to Pacific time for display
        pacific_updated_at = pytz.utc.localize(self.updated_at).astimezone(pacific)

        return {
            "date": self.date.isoformat(),
            "target": self.target,
            "last_updated_by": self.last_updated_by,
            "updated_at": pacific_updated_at.isoformat(),
        }
