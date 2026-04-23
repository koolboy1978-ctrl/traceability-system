"""
数据库迁移脚本：添加 base64 图片字段
用法: python migrate.py
"""
import os
import sys

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models import Product, FarmInfo, ProductionRecord, QualityRecord

def migrate():
    print("🔧 开始数据库迁移...")
    
    # 删除旧表，重新创建（数据会丢失，请先备份！）
    print("⚠️  删除旧表...")
    Base.metadata.drop_all(bind=engine)
    
    print("📦 创建新表...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ 迁移完成！")

if __name__ == "__main__":
    migrate()
