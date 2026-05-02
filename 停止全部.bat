@echo off
chcp 65001 >nul
title 融鑫CRM - 停止全部服务

echo ========================================
echo   正在关闭融鑫CRM所有服务...
echo ========================================

:: 关闭后端 (uvicorn / 端口 8080)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: 关闭前端 (node / 端口 5173)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: 关闭标题含"CRM"的命令行窗口
tasklist /FI "WINDOWTITLE eq CRM*" /FO CSV /NH | findstr /i "CRM" >nul
if %errorlevel%==0 (
    for /f "tokens=1 delims=," %%a in ('tasklist /FI "WINDOWTITLE eq CRM*" /FO CSV /NH') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo.
echo ========================================
echo   所有服务已停止！
echo ========================================
pause
