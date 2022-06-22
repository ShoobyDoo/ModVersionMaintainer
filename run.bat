@ECHO OFF

echo Mod Version Maintainer - Auto mode
echo:
echo Checking for Python virtual environment...

if exist .venv\ (.venv\Scripts\activate.bat && cls && python -m main)

echo Virtual environment doesnt exist. Looking for requirements.txt...
echo:
if exist requirements.txt goto :REQUIREMENTS_EXISTS
echo The requirements.txt file is needed to proceed. Please obtain it via the GitHub page!
pause
goto :EOF

:REQUIREMENTS_EXISTS
echo Found. Creating virtual environment...
python -m venv .venv
echo Done. Installing required external libraries...
echo:
.venv\Scripts\activate.bat && python -m pip install -r requirements.txt && echo: && echo All done! :) Starting in 5 seconds... && sleep 5 && cls && python -m main