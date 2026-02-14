from __future__ import annotations
import secrets
import string
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import db, login_manager, limiter
from .models import User
from .routes_public import public_bp
from .routes_auth import auth_bp
from .routes_admin import admin_bp

def _ticket_code(n: int = 7) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    limiter.default_limits = [app.config.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")]

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))  # type: ignore[arg-type]

    with app.app_context():
        db.create_all()
        _ensure_bootstrap_admin(app)

    return app

def _ensure_bootstrap_admin(app: Flask) -> None:
    from .models import User
    from werkzeug.security import generate_password_hash

    username = app.config["ADMIN_USERNAME"]
    password = app.config["ADMIN_PASSWORD"]

    u = User.query.filter_by(username=username).first()
    if u:
        return
    u = User(
        username=username,
        password_hash=generate_password_hash(password),
        role="ADMIN",
        is_active=True,
        is_approved=True,
    )
    db.session.add(u)
    db.session.commit()
