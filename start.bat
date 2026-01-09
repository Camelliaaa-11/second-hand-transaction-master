@echo off
chcp 65001 > nul
title 闲置交易平台一键启动
color 0A

echo ========================================
echo       闲置交易平台 - 一键启动
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python！
    echo 请安装Python 3.8+
    pause
    exit /b 1
)

echo [2/5] 安装Python依赖...
echo 正在安装依赖，请稍候...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo 警告: 部分依赖安装失败，尝试重新安装...
    pip install flask flask-socketio flask-cors flask-sqlalchemy zhipuai sniffio --quiet
)

echo [3/5] 初始化数据库...
if exist "softapp.db" (
    echo 数据库已存在，跳过初始化
) else (
    python init_db.py
)

echo [4/5] 启动主服务器...
start "闲置交易平台-主服务器" cmd /k "echo 主服务器启动中... && echo 端口: 5011 && echo 请勿关闭此窗口 && echo. && python run_server.py && pause"

echo [5/5] 启动AI智能议价服务...
timeout /t 3 /nobreak > nul
start "闲置交易平台-智能体议价服务" cmd /k "echo AI议价服务启动中... && echo 请勿关闭此窗口 && echo. && python run_agent_service.py && pause"

echo.
echo ========================================
echo 启动成功！
echo.
echo 已启动两个服务：
echo 1. 主服务器 (Web + API) - 端口 5011
echo 2. AI智能议价服务
echo.
echo 请按以下步骤操作：
echo 1. 等待两个服务完全启动（约10-15秒）
echo 2. 打开浏览器访问：
echo    http://localhost:5011
echo    或
echo    http://127.0.0.1:5011
echo.
echo 如果无法访问：
echo 1. 检查两个黑色窗口是否都正常运行
echo 2. 确保5011端口未被占用
echo 3. 等待服务完全启动
echo ========================================
echo.
echo 按任意键退出此窗口...
pause >nul