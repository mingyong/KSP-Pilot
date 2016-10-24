@echo off
start pydoc.bat
del *.log
cd dist
del *.log
del *.mp3
cls
call pilot.py
cd ..
move /Y dist\*.log .\
pause
