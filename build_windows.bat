@echo off
echo 正在构建Windows版本...
python -m pip install pyinstaller
python build_simple.py
pause