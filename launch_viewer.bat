@echo off
title 3D Knowledge Graph Viewer
echo ========================================================
echo  Rebuilding 3D Graph Model from graphify-out...
echo ========================================================
python "%~dp0rebuild.py"
echo.
echo Starting live viewer server...
python "%~dp0run_viewer.py"
pause
