@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo 首次运行：正在创建虚拟环境并安装依赖...
    py -3 -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo 启动网站：http://127.0.0.1:5000
venv\Scripts\python.exe run.py
pause
