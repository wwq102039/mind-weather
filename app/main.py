from datetime import date, timedelta
from collections import Counter
from flask import Blueprint, render_template, g
from .models import MoodRecord, Article

main_bp = Blueprint("main", __name__)


def _day_range(n_days):
    today = date.today()
    return [today - timedelta(days=i) for i in range(n_days - 1, -1, -1)]


@main_bp.route("/")
def index():
    featured = Article.query.order_by(Article.created_at.desc()).limit(6).all()
    return render_template("index.html", featured=featured, active="home")


@main_bp.route("/dashboard")
def dashboard():
    today = date.today()
    records = MoodRecord.query.all()

    by_date = {}
    for r in records:
        by_date.setdefault(r.date, []).append(r)

    # 全班情绪分布（1-5）
    mood_counter = Counter(r.mood for r in records)
    mood_dist = [mood_counter.get(i, 0) for i in range(1, 6)]

    # 近 30 天趋势
    days = _day_range(30)
    day_labels = [d.strftime("%m-%d") for d in days]
    mood_trend, stress_trend, sleep_trend = [], [], []
    for d in days:
        rs = by_date.get(d, [])
        if rs:
            mood_trend.append(round(sum(r.mood for r in rs) / len(rs), 2))
            stress_trend.append(round(sum(r.stress for r in rs) / len(rs), 2))
            sleep_trend.append(round(sum(r.sleep for r in rs) / len(rs), 2))
        else:
            mood_trend.append(None)
            stress_trend.append(None)
            sleep_trend.append(None)

    # 概览卡片
    week_start = today - timedelta(days=today.weekday())
    week_records = [r for r in records if r.date >= week_start]
    stats = {
        "visitor_count": len({r.visitor_id for r in records}),
        "today_count": len(by_date.get(today, [])),
        "week_count": len(week_records),
        "total_count": len(records),
    }

    # 个人概览（匿名：按当前浏览器标识）
    vid = g.visitor_id
    my_records = sorted(
        MoodRecord.query.filter_by(visitor_id=vid).all(), key=lambda r: r.date
    )
    latest = my_records[-1] if my_records else None
    my_14 = _day_range(14)
    my_mood = []
    for d in my_14:
        rs = [r for r in my_records if r.date == d]
        my_mood.append(round(sum(r.mood for r in rs) / len(rs), 2) if rs else None)

    return render_template(
        "dashboard.html",
        active="dashboard",
        stats=stats,
        mood_dist=mood_dist,
        day_labels=day_labels,
        mood_trend=mood_trend,
        stress_trend=stress_trend,
        sleep_trend=sleep_trend,
        my_mood=my_mood,
        my_labels=[d.strftime("%m-%d") for d in my_14],
        latest=latest,
    )


@main_bp.route("/monthly")
def monthly():
    today = date.today()
    month_start = date(today.year, today.month, 1)
    records = MoodRecord.query.all()
    month_records = [r for r in records if month_start <= r.date <= today]

    by_date = Counter(r.date for r in month_records)
    month_days = _day_range(today.day)
    day_labels = [d.strftime("%m-%d") for d in month_days]
    daily_count = [by_date.get(d, 0) for d in month_days]

    mood_counter = Counter(r.mood for r in month_records)
    mood_dist = [mood_counter.get(i, 0) for i in range(1, 6)]

    participants = len({r.visitor_id for r in month_records})
    summary = {
        "month_label": today.strftime("%Y 年 %m 月"),
        "total": len(month_records),
        "participants": participants,
        "avg_mood": round(sum(r.mood for r in month_records) / len(month_records), 2) if month_records else 0,
        "avg_stress": round(sum(r.stress for r in month_records) / len(month_records), 2) if month_records else 0,
        "avg_sleep": round(sum(r.sleep for r in month_records) / len(month_records), 2) if month_records else 0,
    }

    # 高压力提醒（匿名）：本月平均压力 >= 7 的匿名访客数
    stress_by_visitor = {}
    for r in month_records:
        stress_by_visitor.setdefault(r.visitor_id, []).append(r.stress)
    high_stress_count = sum(
        1 for vals in stress_by_visitor.values()
        if sum(vals) / len(vals) >= 7
    )

    return render_template(
        "monthly.html",
        active="monthly",
        summary=summary,
        day_labels=day_labels,
        daily_count=daily_count,
        mood_dist=mood_dist,
        high_stress_count=high_stress_count,
    )
