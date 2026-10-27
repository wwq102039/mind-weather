import os
import secrets
from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from html import escape

db = SQLAlchemy()


def md_lite(text):
    """极简 Markdown 渲染：支持 ## / ### 标题、- 列表、空行分段，其余全部转义。"""
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    para = []

    def flush_para():
        if para:
            out.append("<p>" + "<br>".join(para) + "</p>")
            para.clear()

    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()
        if stripped.startswith("### "):
            flush_para()
            out.append("<h3>" + escape(stripped[4:]) + "</h3>")
        elif stripped.startswith("## "):
            flush_para()
            out.append("<h2>" + escape(stripped[3:]) + "</h2>")
        elif stripped.startswith("- "):
            flush_para()
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append("<li>" + escape(lines[i].strip()[2:]) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif stripped == "":
            flush_para()
        else:
            para.append(escape(line))
        i += 1
    flush_para()
    return Markup("\n".join(out))


def create_app():
    app = Flask(__name__)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "xinli-qingyu-2026-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.jinja_env.filters["md"] = md_lite

    from . import models  # noqa: F401  确保模型注册

    from .main import main_bp
    from .records import records_bp
    from .knowledge import knowledge_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(knowledge_bp)

    @app.before_request
    def load_visitor():
        vid = request.cookies.get("visitor_id")
        if not vid:
            vid = secrets.token_hex(16)
            g.new_visitor_id = vid
        g.visitor_id = vid

    @app.after_request
    def set_visitor_cookie(resp):
        vid = getattr(g, "new_visitor_id", None)
        if vid:
            resp.set_cookie("visitor_id", vid, max_age=60 * 60 * 24 * 365, httponly=True, samesite="Lax")
        return resp

    @app.context_processor
    def inject_globals():
        return {"mood_labels": ["很低落", "有点差", "一般", "不错", "很好"]}

    with app.app_context():
        db.create_all()
        from .seed import seed
        seed()

    return app
