"""Flask app factory."""
import os
from flask import Flask

from app.services import Store
from app.controllers import member_bp, request_bp


def create_app(seed_path: str = None) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "mvc-exam-2569"

    # Attach in-memory store to app
    store = Store()
    if seed_path is None:
        seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed_data.json")
    store.load_seed(seed_path)
    app.store = store

    app.register_blueprint(member_bp)
    app.register_blueprint(request_bp)

    return app
