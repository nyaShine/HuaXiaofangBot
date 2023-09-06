@echo off

REM Check for required Python libraries and install them if necessary
echo Checking and installing required Python libraries...
pip install -r requirements.txt

REM Run the application
py main.py
pause