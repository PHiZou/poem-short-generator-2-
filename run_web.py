#!/usr/bin/env python3
"""Entry point to run the Poem Short Generator web application."""

import os
import sys
from pathlib import Path

# Ensure the project root is in the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from webapp.app import app

if __name__ == '__main__':
    # Get configuration from environment or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              🎬 Daily Poem Generator Web App                 ║
╠══════════════════════════════════════════════════════════════╣
║  Starting server at: http://{host}:{port}                      ║
║  Debug mode: {debug}                                          ║
║                                                              ║
║  Press Ctrl+C to stop the server                             ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    app.run(host=host, port=port, debug=debug)
