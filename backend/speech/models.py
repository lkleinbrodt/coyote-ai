import json
from enum import Enum

from backend.extensions import db


class SpeechProfile(db.Model):
    """User profile specific to the Speech Coach application"""

    __tablename__ = "speech_profile"
    __table_args__ = {"schema": "speech"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    last_seen = db.Column(db.DateTime, nullable=True, default=db.func.now())
    role = db.Column(db.String(50), default="user")

    speaking_level = db.Column(db.String(50), nullable=True)
    total_recordings = db.Column(db.Integer, default=0)
    total_practice_time = db.Column(db.Integer, default=0)  # in seconds
    last_practice = db.Column(db.DateTime, nullable=True)

    # Relationships
    recordings = db.relationship("Recording", backref="speech_profile", lazy=True)

    def __repr__(self):
        return f"<SpeechProfile {self.id}>"


class Recording(db.Model):
    """Speech recording data"""

    __tablename__ = "recording"
    __table_args__ = {"schema": "speech"}

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(
        db.Integer, db.ForeignKey("speech.speech_profile.id"), nullable=False
    )
    title = db.Column(db.String(255))
    duration = db.Column(db.Integer)  # in seconds
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Relationship
    analysis = db.relationship(
        "Analysis", backref="recording", lazy=True, uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "duration": self.duration,
            "created_at": self.created_at,
            "analysis": self.analysis.to_dict() if self.analysis else None,
        }


class Analysis(db.Model):
    """Speech analysis results"""

    __tablename__ = "analysis"
    __table_args__ = {"schema": "speech"}

    id = db.Column(db.Integer, primary_key=True)
    recording_id = db.Column(
        db.Integer, db.ForeignKey("speech.recording.id"), nullable=False
    )
    transcript = db.Column(db.Text)
    clarity_score = db.Column(db.Float)
    pace_score = db.Column(db.Float)
    filler_word_count = db.Column(db.Integer)
    tone_analysis = db.Column(db.JSON)
    content_structure = db.Column(db.JSON)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "transcript": self.transcript,
            "clarity_score": self.clarity_score,
            "pace_score": self.pace_score,
            "filler_word_count": self.filler_word_count,
            "tone_analysis": self.tone_analysis,
            "content_structure": self.content_structure,
            "feedback": self.feedback,
            "created_at": self.created_at,
        }


# Operation types specific to the speech app
class SpeechOperation(str, Enum):
    """Types of operations that cost money in the speech app"""

    TRANSCRIPTION = "transcription"
    ANALYSIS = "analysis"
    TITLE = "title"
    MODERATION = "moderation"
