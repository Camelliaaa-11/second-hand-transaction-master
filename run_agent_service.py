#!/usr/bin/env python3
"""
启动智能体Web服务
"""
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.agent_service import app

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 二手交易智能体Web服务启动")
    print("=" * 60)
    print("📡 服务地址: http://localhost:5011")
    print("📚 API文档:")
    print("   GET  /                     服务信息")
    print("   GET  /health               健康检查")
    print("   POST /api/v1/buyer/advice  买家砍价建议")
    print("   POST /api/v1/seller/response 卖家回应建议")
    print("   POST /api/v1/negotiation/auto 自动谈判演示")
    print("=" * 60)
    print("📝 按 Ctrl+C 停止服务")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5011, debug=True)