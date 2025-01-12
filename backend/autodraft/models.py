from sqlalchemy.orm import relationship
from backend.extensions import db

# Association table for the many-to-many relationship between User and Project
user_project_association = db.Table(
    "user_project",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
)


class Project(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    index_id = db.Column(db.String(200), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Many-to-Many relationship with User

    users = relationship(
        "User", secondary=user_project_association, back_populates="projects"
    )

    # One-to-Many relationship with Report
    reports = relationship(
        "Report", back_populates="project", cascade="all, delete-orphan"
    )

    # one to many with files
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.id}>"

    def __str__(self) -> str:
        return f"<Project {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "index_id": self.index_id,
        }


class File(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_modified = db.Column(db.DateTime, nullable=False, default=db.func.now())

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = relationship("Project", back_populates="files")

    # one to many with documents

    documents = relationship(
        "Document", back_populates="file", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<File {self.id}>"

    def __str__(self) -> str:
        return f"<File {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }


class Document(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    llama_id = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    last_modified = db.Column(db.DateTime, nullable=False, default=db.func.now())
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    llama_metadata = db.Column(db.JSON, nullable=False)

    content = db.Column(db.Text, nullable=False)

    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=False)
    file = relationship("File", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.id}>"

    def __str__(self) -> str:
        return f"<Document {self.id}>"


class Report(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    # Foreign key for the One-to-Many relationship with Project
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = relationship("Project", back_populates="reports")

    # One-to-Many relationship with Prompt
    prompts = relationship(
        "Prompt", back_populates="report", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Report {self.id}>"

    def __str__(self) -> str:
        return f"<Report {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,
        }


class Prompt(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2048), nullable=False)
    position = db.Column(db.Integer, nullable=False)

    # Foreign key for the One-to-Many relationship with Report
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"), nullable=False)
    report = relationship("Report", back_populates="prompts")

    # One-to-Many relationship with Response
    responses = relationship(
        "Response", back_populates="prompt", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Prompt {self.id}>"

    def __str__(self) -> str:
        return f"<Prompt {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "position": self.position,
            "report_id": self.report_id,
            "responses": [response.to_dict() for response in self.responses],
        }


class Response(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    selected = db.Column(db.Boolean, nullable=False)

    # Foreign key for the One-to-Many relationship with Prompt
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompt.id"), nullable=False)
    prompt = relationship("Prompt", back_populates="responses")

    def __repr__(self):
        return f"<Response {self.id}>"

    def __str__(self) -> str:
        return f"<Response {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "position": self.position,
            "selected": self.selected,
        }


### DEPRECATED: Tables necessary for auth.js

# class Account(db.Model):

#     id = db.Column(db.String, primary_key=True)
#     user_id = db.Column("userId", db.String, db.ForeignKey("user.id"), nullable=False)
#     type = db.Column(db.String(255), nullable=False)
#     provider = db.Column(db.String(255), nullable=False)
#     provider_account_id = db.Column("providerAccountId", db.String(255), nullable=False)
#     refresh_token = db.Column(db.String(256), nullable=True)
#     access_token = db.Column(db.String(256), nullable=True)
#     expires_at = db.Column(db.BigInteger, nullable=True)
#     id_token = db.Column(db.String(256), nullable=True)
#     scope = db.Column(db.String(256), nullable=True)
#     session_state = db.Column(db.String(256), nullable=True)
#     token_type = db.Column(db.String(256), nullable=True)

#     created_at = db.Column(
#         "createdAt", db.BigInteger, nullable=False, default=db.func.now()
#     )
#     updated_at = db.Column(
#         "updatedAt", db.BigInteger, nullable=False, default=db.func.now()
#     )

#     # Define relationship to the User model
#     user = relationship("User", back_populates="accounts")

#     def __repr__(self):
#         return f"<Account {self.id}>"

#     def __str__(self) -> str:
#         return f"<Account {self.id}>"

# class Session(db.Model):

#     id = db.Column(db.String, primary_key=True)
#     user_id = db.Column("userId", db.String, db.ForeignKey("user.id"), nullable=False)
#     expires = db.Column(db.BigInteger, nullable=False)
#     session_token = db.Column("sessionToken", db.String(255), nullable=False)

#     created_at = db.Column(
#         "createdAt", db.BigInteger, nullable=False, default=db.func.now()
#     )
#     updated_at = db.Column(
#         "updatedAt", db.BigInteger, nullable=False, default=db.func.now()
#     )

#     # Define relationship to the User model
#     user = relationship("User", back_populates="sessions")

#     def __repr__(self):
#         return f"<Session {self.id}>"

#     def __str__(self) -> str:
#         return f"<Session {self.id}>"


# class VerificationToken(db.Model):

#     identifier = db.Column(db.String(256), primary_key=True, nullable=False)
#     token = db.Column(db.String(256), nullable=False)
#     expires = db.Column(db.BigInteger, nullable=False)

#     def __repr__(self):
#         return f"<VerificationToken {self.identifier}>"
