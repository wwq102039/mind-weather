from flask import Blueprint, render_template, request, abort
from .models import Article

knowledge_bp = Blueprint("knowledge", __name__)

CATEGORIES = ["情绪管理", "压力应对", "睡眠健康", "时间管理", "人际关系"]


@knowledge_bp.route("/knowledge")
def knowledge_list():
    category = request.args.get("category", "")
    keyword = request.args.get("q", "").strip()

    query = Article.query
    if category and category in CATEGORIES:
        query = query.filter_by(category=category)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (Article.title.ilike(like)) | (Article.content.ilike(like)) | (Article.tags.ilike(like))
        )
    articles = query.order_by(Article.created_at.desc()).all()

    # 各分类文章数量，用于顶部标签
    from sqlalchemy import func
    counts = dict(
        Article.query.with_entities(Article.category, func.count(Article.id))
        .group_by(Article.category).all()
    )

    return render_template(
        "knowledge_list.html", active="knowledge", articles=articles,
        categories=CATEGORIES, current_category=category, keyword=keyword, counts=counts,
    )


@knowledge_bp.route("/knowledge/<int:article_id>")
def knowledge_detail(article_id):
    article = Article.query.get_or_404(article_id)
    related = (
        Article.query.filter(Article.category == article.category, Article.id != article_id)
        .order_by(Article.created_at.desc()).limit(3).all()
    )
    return render_template("knowledge_detail.html", active="knowledge", article=article, related=related)
