@echo off
chcp 65001 >nul
title 融鑫CRM - 后端服务

cd /d "%~dp0backend"

echo [1/2] 检查依赖...
"C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m pip install -r requirements.txt --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] pip install 遇到问题，尝试继续启动...
)

echo [2/2] 启动后端服务 (端口 8080)...
"C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

pause
