@echo off
chcp 65001 >nul
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
set PYTHONPATH=%CD%
"%CD%\.venv\Scripts\python.exe" ask_python.py %*
