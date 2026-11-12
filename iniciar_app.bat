@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -c "
import webbrowser
from app import create_app
app = create_app()
webbrowser.open('http://127.0.0.1:5000/')
app.run(host='127.0.0.1', port=5000, debug=False)
"
