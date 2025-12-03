from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
import app.models

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    #初始化
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp)  # 注册蓝图
    return app