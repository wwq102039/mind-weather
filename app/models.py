from datetime import datetime
from . import db


class MoodRecord(db.Model):
    __tablename__ = "mood_record"

    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(64), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.Integer, nullable=False)      # 情绪指数 1-5
    stress = db.Column(db.Integer, nullable=False)    # 压力指数 1-10
    sleep = db.Column(db.Float, nullable=False)       # 睡眠时长（小时）
    energy = db.Column(db.Integer, nullable=False)    # 精力 1-5
    note = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("visitor_id", "date", name="uq_visitor_date"),)


class Article(db.Model):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.String(500), default="")
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
