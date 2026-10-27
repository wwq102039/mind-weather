"""清空所有打卡记录，用于正式投入使用前重置。"""
from app import create_app, db
from app.models import MoodRecord

app = create_app()

with app.app_context():
    n = MoodRecord.query.count()
    MoodRecord.query.delete()
    db.session.commit()

print(f"已清空 {n} 条打卡记录。")
