@echo off
cd dist
cls
pydoc -w pilot
cd ..
move .\dist\*.html .\
exit
