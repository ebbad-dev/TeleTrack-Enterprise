"""
TeleTrack Enterprise — Pagination Helper
Generic pagination for SQLAlchemy queries.
"""

from flask import request


def paginate_query(query, default_per_page=20, max_per_page=100):
    """
    Apply pagination to a SQLAlchemy query.
    Returns (items, total, page, per_page).
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", default_per_page, type=int)

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = default_per_page
    if per_page > max_per_page:
        per_page = max_per_page

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return pagination.items, pagination.total, page, per_page
