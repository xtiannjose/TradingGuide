@echo off
rem Opens the TradingGuide terminal in your browser. Keep MetaTrader 5 open and logged in.
rem Close this window (or press Ctrl+C) to stop it.
cd /d "%~dp0"
python app\server.py
if errorlevel 1 pause
