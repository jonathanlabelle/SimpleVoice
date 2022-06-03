import sqlalchemy
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import routes
        from . import auth
        from .assets import compile_assets

        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)

        db.create_all()

        # Compile static assets
        if app.config['FLASK_ENV'] == 'development':
            compile_assets(app)

        return app