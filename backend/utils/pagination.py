"""
TeleTrack Enterprise — Pagination Helper
Generic pagination for SQLAlchemy queries.
"""

from flask import request


def paginate_query(query, default_per_page=20, max_per_page=100):
    """
    Apply pagination to a SQLAlchemy query or a list.
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

    # Handle SQLAlchemy Query
    if hasattr(query, "paginate"):
        try:
            # Try Flask-SQLAlchemy 3.0+ style if query is not a query object
            from extensions import db
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return pagination.items, pagination.total, page, per_page
        except Exception:
            # Fallback for other objects
            pass

    # Handle List or fallback
    if isinstance(query, list):
        total = len(query)
    else:
        # Try to get total using a safe count method
        try:
            total = query.count()
        except TypeError:
            # This is the fix for "list.count() takes exactly one argument"
            if isinstance(query, list) or hasattr(query, "__len__"):
                total = len(query)
            else:
                raise

    start = (page - 1) * per_page
    end = start + per_page
    
    if isinstance(query, list):
        items = query[start:end]
    else:
        items = query.offset(start).limit(per_page).all()

    return items, total, page, per_page
