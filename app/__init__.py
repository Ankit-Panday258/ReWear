from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.models import Listing, User, SwapRequest

    from .routes.home import home
    from .routes.listing import listing
    from .routes.auth import auth
    from .routes.user import user
    from .routes.admin import admin

    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(listing, url_prefix='/listings')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(admin, url_prefix='/admin')


    migrate = Migrate(app, db)

    return app