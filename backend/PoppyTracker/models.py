from datetime import date, datetime

from backend.extensions import db


class DailyFeeding(db.Model):
    """Tracks daily feeding amounts for the dog"""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, default=date.today)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    last_updated_by = db.Column(db.String(36), nullable=True)  # Store user ID
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "total": self.total_amount,
            "last_updated_by": self.last_updated_by,
            "updated_at": self.updated_at.isoformat(),
        }


class Settings(db.Model):
    """Stores application settings"""

    id = db.Column(db.Integer, primary_key=True)
    daily_target = db.Column(
        db.Float, nullable=False, default=3.0
    )  # Default target of 3.0 cups
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {"target": self.daily_target, "updated_at": self.updated_at.isoformat()}
