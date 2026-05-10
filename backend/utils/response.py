"""
TeleTrack Enterprise — Standardized API Responses
Consistent JSON response format across all endpoints.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200, meta=None):
    """Return a standardized success response."""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    if meta is not None:
        response["meta"] = meta
    return jsonify(response), status_code


def error_response(message="An error occurred", status_code=500, errors=None):
    """Return a standardized error response."""
    response = {"success": False, "error": message}
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code


def paginated_response(items, total, page, per_page, message="Success"):
    """Return a standardized paginated response."""
    return jsonify(
        {
            "success": True,
            "message": message,
            "data": items,
            "meta": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
            },
        }
    ), 200
