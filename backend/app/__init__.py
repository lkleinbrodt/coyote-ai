from flask import Flask
from server.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_bootstrap import Bootstrap5


from flask_cors import CORS


app = Flask(__name__, static_folder="frontend/dist")

app.config.from_object(Config)
# jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

CORS(
    app,
)

from .routes import main
from lyrica.routes import lyrica
from lifter.routes import lifter

from flask_admin.contrib.sqla import ModelView

app.register_blueprint(lyrica)
app.register_blueprint(lifter)
app.register_blueprint(main)
bootstrap = Bootstrap5(app)

admin = Admin(
    app,
    name="Lyrica Admin",
    template_mode="bootstrap3",
    index_view=AdminIndexView(),
)
from lyrica.models import Artist, Song, Lyric

admin.add_view(ModelView(Artist, db.session))
admin.add_view(ModelView(Song, db.session))
admin.add_view(ModelView(Lyric, db.session))

# with app.app_context():
#     # get all lyrics for which the embedding length is not 1536
#     lyrics = Lyric.query.filter(Lyric.embeddings != None).all()
#     bad_lyrics = [lyric for lyric in lyrics if len(lyric.get_embedding()) != 1536]
#     for lyric in bad_lyrics:
#         db.session.delete(lyric)
#     db.session.commit()
#     print(f"Found {len(bad_lyrics)} bad lyrics")
#     print(len(bad_lyrics[0].get_embedding()))
