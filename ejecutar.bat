@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Primero sigue la instalacion del README.md.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py
