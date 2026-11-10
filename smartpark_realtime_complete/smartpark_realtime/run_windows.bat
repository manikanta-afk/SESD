@echo off
cd /d "%~dp0"
if not exist .venv py -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
python app.py
