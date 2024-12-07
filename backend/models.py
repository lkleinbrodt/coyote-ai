# import sqlalchemy.orm as so
# import sqlalchemy as sa
# from typing import Optional
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# from server import db


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     userName = db.Column(db.String(80), unique=True, nullable=False)
#     password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

#     email = db.Column(db.String(120), unique=True, nullable=False)
#     storeName = db.Column(db.String(120), unique=False, nullable=True)
#     reverbAccess = db.Column(db.String(120), unique=True, nullable=True)

#     email_verified = db.Column(db.Boolean, default=False)

#     # TODO: I dont like this implementation, using deeplinking would be better
#     # but that is more complex and requires more setup
#     can_change_password = db.Column(db.Boolean, default=False)
#     can_change_password_expiry = db.Column(db.DateTime, default=datetime.utcnow)
#     change_password_code = db.Column(db.String(6), nullable=True)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def set_reverb_key(self, reverb_key):
#         self.reverbAccess = reverb_key

#     def __repr__(self):
#         return f"<User {self.userName}>"
