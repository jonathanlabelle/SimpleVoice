from flask_login import LoginManager
from model import Users


login_manager = LoginManager()
login_manager.init_app(app)