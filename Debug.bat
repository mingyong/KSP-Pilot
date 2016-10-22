@echo off
start pydoc.bat
del *.log
cd dist
del *.log
cls
call pilot.py
cd ..
move /Y dist\*.log .\
pause
