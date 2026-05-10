import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the server without the watchdog reloader to ensure stability during DB access
    app.run(port=5000, debug=True, use_reloader=False)
