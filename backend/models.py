from .extensions import db, jwt
from sqlalchemy.orm import relationship
from .autodraft.models import user_project_association


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    email_verified = db.Column("emailVerified", db.DateTime, nullable=True)

    created_at = db.Column(
        "createdAt", db.DateTime, nullable=False, default=db.func.now()
    )
    updated_at = db.Column(
        "updatedAt", db.DateTime, nullable=False, default=db.func.now()
    )

    group = db.Column(db.String(50), nullable=True)

    projects = relationship(
        "Project", secondary=user_project_association, back_populates="users"
    )

    def __repr__(self):
        return f"<User {self.id}>"

    def __str__(self) -> str:
        return f"<User {self.id}>"


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    # decode the jwt_data
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()
