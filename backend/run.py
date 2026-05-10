"""
TeleTrack Enterprise — Application Entry Point
Run this file to start the development server.
"""

from app import create_app
from extensions import socketio

app = create_app()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TeleTrack Enterprise v5.0 — Backend Server")
    print("  Running on: http://127.0.0.1:5000")
    print("  API Docs:   http://127.0.0.1:5000/api/health")
    print("=" * 60 + "\n")

    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
