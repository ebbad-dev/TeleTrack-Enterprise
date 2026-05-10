"""
TeleTrack Enterprise — Global Error Handlers
Consistent error handling for all Flask exceptions.
"""

import traceback
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": "Bad request", "details": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"success": False, "error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({"success": False, "error": "Resource conflict"}), 409

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({"success": False, "error": "Unprocessable entity"}), 422

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({"success": False, "error": "Rate limit exceeded. Please slow down."}), 429

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return jsonify({"success": False, "error": error.description}), error.code

        logger.error(f"Unhandled exception: {error}\n{traceback.format_exc()}")

        if app.debug:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(error),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )

        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500
