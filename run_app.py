#!/usr/bin/env python3
import os, sys
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.getcwd())
    from app import app
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, port=port, host='127.0.0.1')
