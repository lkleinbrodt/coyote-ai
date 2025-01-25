from typing import List
from sqlalchemy.orm import relationship
from backend.extensions import db

# Association table for the many-to-many relationship between User and Project
user_project_association = db.Table(
    "user_project",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column(
        "project_id",
        db.Integer,
        db.ForeignKey("autodraft.project.id", ondelete="CASCADE"),
        primary_key=True,
    ),
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

    project_id = db.Column(
        db.Integer, db.ForeignKey("autodraft.project.id"), nullable=False
    )
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
    page_label = db.Column(db.String(200), nullable=True)
    llama_metadata = db.Column(db.JSON, nullable=False)

    content = db.Column(db.Text, nullable=False)

    file_id = db.Column(db.Integer, db.ForeignKey("autodraft.file.id"), nullable=False)
    file = relationship("File", back_populates="documents")

    responses = relationship(
        "Response",
        secondary="autodraft.source_doc",
        back_populates="source_docs",
    )

    def __repr__(self):
        return f"<Document {self.id}>"

    def __str__(self) -> str:
        return f"<Document {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "llama_id": self.llama_id,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "uploaded_at": self.uploaded_at,
            "llama_metadata": self.llama_metadata,
            "content": self.content,
            "file": self.file.to_dict(),
        }


class Report(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    # Foreign key for the One-to-Many relationship with Project
    project_id = db.Column(
        db.Integer, db.ForeignKey("autodraft.project.id"), nullable=False
    )
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
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Prompt(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2048), nullable=False)
    position = db.Column(db.Integer, nullable=False)

    # Foreign key for the One-to-Many relationship with Report
    report_id = db.Column(
        db.Integer,
        db.ForeignKey("autodraft.report.id"),
        nullable=False,
    )
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
    # each response has a relation to a list of the source documents (of type Document)
    source_docs = relationship(
        "Document", secondary="autodraft.source_doc", back_populates="responses"
    )

    # Foreign key for the One-to-Many relationship with Prompt
    prompt_id = db.Column(
        db.Integer, db.ForeignKey("autodraft.prompt.id"), nullable=False
    )
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
            # do i want to include all this data every time?
            "source_docs": [doc.to_dict() for doc in self.source_docs],
        }


class SourceDoc(db.Model):
    __table_args__ = {"schema": "autodraft"}
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(
        db.Integer, db.ForeignKey("autodraft.response.id"), nullable=False
    )
    document_id = db.Column(
        db.Integer, db.ForeignKey("autodraft.document.id"), nullable=False
    )
    score = db.Column(db.Float, nullable=False)

    # TODO: we may want to revisit how we do this

    # Store the character positions of the relevant segment
    start_char = db.Column(db.Integer, nullable=True)
    end_char = db.Column(db.Integer, nullable=True)

    # Store the actual relevant text segment
    relevant_text = db.Column(db.Text, nullable=True)

    # we will also store
