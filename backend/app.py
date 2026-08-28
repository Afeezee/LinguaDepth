from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import get_config
from models import db


FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def _run_light_migrations():
    """Idempotent schema top-ups for columns SQLAlchemy's create_all can't add.

    create_all() creates missing tables but never alters existing ones, so any
    column added to a model after its table already exists in the deployed
    database has to be introduced manually here. Kept intentionally narrow:
    only column additions, no data migrations.
    """
    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    dialect = db.engine.dialect.name

    def _has_column(table: str, column: str) -> bool:
        return column in {c["name"] for c in inspector.get_columns(table)}

    if "lessons" in inspector.get_table_names():
        with db.engine.begin() as conn:
            if not _has_column("lessons", "content_markdown"):
                conn.execute(
                    text(
                        "ALTER TABLE lessons ADD COLUMN content_markdown TEXT "
                        "NOT NULL DEFAULT ''"
                    )
                )
            if not _has_column("lessons", "estimated_minutes"):
                # SQLite disallows non-constant defaults; a literal integer is fine.
                conn.execute(
                    text(
                        "ALTER TABLE lessons ADD COLUMN estimated_minutes "
                        "INTEGER DEFAULT 5"
                    )
                )
        # Refresh inspector metadata for any callers later in this process.
        inspector = inspect(db.engine)


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    JWTManager(app)
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
    )

    from admin.routes import admin_bp
    from auth.routes import auth_bp
    from lessons.routes import lessons_bp
    from quiz.routes import quiz_bp
    from dashboard.routes import dashboard_bp
    from ml.routes import ml_bp
    from llm.routes import llm_bp

    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(lessons_bp, url_prefix="/api/lessons")
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(ml_bp, url_prefix="/api/ml")
    app.register_blueprint(llm_bp, url_prefix="/api/llm")

    with app.app_context():
        db.create_all()
        _run_light_migrations()

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"error": "Resource not found"}), 404

        if not FRONTEND_DIST_DIR.exists():
            return jsonify({"error": "Frontend build not found"}), 404

        requested_file = FRONTEND_DIST_DIR / path
        if path and requested_file.is_file():
            return send_from_directory(FRONTEND_DIST_DIR, path)

        return send_from_directory(FRONTEND_DIST_DIR, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
