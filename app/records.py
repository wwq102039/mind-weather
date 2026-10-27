from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from . import db
from .models import MoodRecord

records_bp = Blueprint("records", __name__)


def _parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@records_bp.route("/record", methods=["GET", "POST"])
def record():
    vid = g.visitor_id
    if request.method == "POST":
        mood = _parse_int(request.form.get("mood"), 0)
        stress = _parse_int(request.form.get("stress"), 0)
        sleep = _parse_float(request.form.get("sleep"), 0)
        energy = _parse_int(request.form.get("energy"), 0)
        note = request.form.get("note", "").strip()
        try:
            record_date = datetime.strptime(request.form.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            record_date = date.today()

        if mood not in range(1, 6) or stress not in range(1, 11) or energy not in range(1, 6):
            flash("请完整填写情绪、压力与精力（均为必填）", "error")
        elif sleep <= 0 or sleep > 24:
            flash("请填写合理的睡眠时长", "error")
        else:
            existing = MoodRecord.query.filter_by(visitor_id=vid, date=record_date).first()
            if existing:
                existing.mood = mood
                existing.stress = stress
                existing.sleep = sleep
                existing.energy = energy
                existing.note = note
                flash(f"已更新 {record_date} 的记录", "success")
            else:
                rec = MoodRecord(
                    visitor_id=vid, date=record_date,
                    mood=mood, stress=stress, sleep=sleep, energy=energy, note=note,
                )
                db.session.add(rec)
                flash("记录成功，谢谢你的坚持", "success")
            db.session.commit()
            return redirect(url_for("records.history"))

    today = date.today()
    today_record = MoodRecord.query.filter_by(visitor_id=vid, date=today).first()
    return render_template("record.html", active="record", today=today, today_record=today_record)


@records_bp.route("/history")
def history():
    vid = g.visitor_id
    records = MoodRecord.query.filter_by(visitor_id=vid).order_by(MoodRecord.date.desc()).all()
    recent = sorted(records, key=lambda r: r.date)[-30:]
    labels = [r.date.strftime("%m-%d") for r in recent]
    mood_series = [r.mood for r in recent]
    stress_series = [r.stress for r in recent]

    stats = {}
    if records:
        stats = {
            "total": len(records),
            "avg_mood": round(sum(r.mood for r in records) / len(records), 2),
            "avg_stress": round(sum(r.stress for r in records) / len(records), 2),
            "avg_sleep": round(sum(r.sleep for r in records) / len(records), 2),
        }

    return render_template(
        "history.html", active="history", records=records,
        labels=labels, mood_series=mood_series, stress_series=stress_series, stats=stats,
    )
