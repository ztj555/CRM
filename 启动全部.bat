@echo off
chcp 65001 >nul
title 融鑫CRM - 启动全部服务

echo ========================================
echo   融鑫CRM 全部服务启动中...
echo   后端: http://localhost:8080
echo   前端: http://localhost:5173
echo ========================================
echo.

:: 检查并安装后端依赖
cd /d "%~dp0backend"
echo [后端] 检查依赖...
"C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m pip install -r requirements.txt --quiet 2>nul

:: 启动后端
start "CRM后端" cmd /k "chcp 65001 >nul && "C:\Users\10517\.workbuddy\binaries\python\versions\3.13.12\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload"

:: 启动前端
cd /d "%~dp0crm-frontend"
start "CRM前端" cmd /k "chcp 65001 >nul && "C:\node-v20.18.0-win-x64\node.exe" "C:\node-v20.18.0-win-x64\node_modules\npm\bin\npm-cli.js" run dev"

echo.
echo 已启动！3秒后打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================
echo  启动完成！
echo  使用 "停止全部.bat" 关闭所有服务
echo ========================================
pause
