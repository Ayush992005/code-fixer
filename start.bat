@echo off
cd /d C:\Users\sahaa\Documents\code-fixer
start "" "frontend\index.html"
call env\Scripts\activate.bat
uvicorn main:app --port 8000