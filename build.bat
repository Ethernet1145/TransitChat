@echo off
chcp 65001 >nul
echo ========================================
echo    TransitChat v0.1.0 构建脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo错误: 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

REM 检查PyInstaller是否安装
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo安装PyInstaller...
    pip install pyinstaller
)

REM 清理旧构建
echo 清理旧构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist *.spec del /q *.spec

REM 检查图标文件
set ICON_OPTION=
if exist icon.ico (
    set ICON_OPTION=--icon=icon.ico
    echo 使用图标: icon.ico
) else (
    echo 警告: 未找到icon.ico，使用默认图标
)

REM 执行构建
echo.
echo 开始构建TransitChat...
echo.

pyinstaller ^
  --name=TransitChat ^
  %ICON_OPTION% ^
  --add-data="src;src" ^
  --add-data="version.py;." ^
  --add-data="icon.ico;." ^
  --hidden-import=p2pu.core_utils ^
  --hidden-import=p2pu.ipv4_utils ^
  --hidden-import=p2pu.ipv6_utils ^
  --hidden-import=ui.display_utils ^
  --hidden-import=ui.input_utils ^
  --hidden-import=config.settings ^
  --hidden-import=direct.direct_chat ^
  --hidden-import=room.room_host ^
  --hidden-import=room.room_join ^
  --hidden-import=version ^
  --console ^
  --clean ^
  --onedir ^
  --noconfirm ^
  src/main.py

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo   构建成功！
    echo ========================================
    echo 程序名称: TransitChat
    echo 版本号: v0.1.0 Beta
    echo 输出位置: dist\TransitChat\
    echo 主程序: dist\TransitChat\TransitChat.exe
    echo.
    echo 运行程序: dist\TransitChat\TransitChat.exe
    echo ========================================
) else (
    echo ========================================
    echo   构建失败！
    echo ========================================
    pause
    exit /b 1
)

pause