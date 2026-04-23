"""
农产品溯源系统 - 管理脚本
用于命令行管理产品和数据
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, init_db
from models import Product, FarmInfo, ProductionRecord, QualityRecord
from datetime import datetime


def create_product():
    """创建产品"""
    print("\n=== 创建新产品 ===")
    
    code = input("产品编码（二维码内容）: ").strip()
    name = input("产品名称: ").strip()
    category = input("分类（蔬菜/水果/畜禽/粮食）: ").strip() or "农产品"
    brand = input("品牌名称: ").strip()
    origin = input("产地: ").strip()
    description = input("产品描述: ").strip()
    
    db = SessionLocal()
    try:
        # 检查编码是否已存在
        existing = db.query(Product).filter(Product.code == code).first()
        if existing:
            print("错误：产品编码已存在！")
            return
        
        product = Product(
            code=code,
            name=name,
            category=category,
            brand=brand,
            origin=origin,
            description=description
        )
        db.add(product)
        db.flush()
        
        print("\n是否添加农场信息？(y/n)")
        if input().lower() == 'y':
            farm_name = input("农场名称: ").strip()
            location = input("农场位置: ").strip()
            area = input("面积（亩）: ").strip()
            cert = input("认证信息: ").strip()
            story = input("品牌故事: ").strip()
            
            farm = FarmInfo(
                product_id=product.id,
                farm_name=farm_name,
                location=location,
                area=float(area) if area else None,
                certification=cert,
                story=story
            )
            db.add(farm)
        
        db.commit()
        print(f"\n✅ 产品创建成功！编码：{code}")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{e}")
    finally:
        db.close()


def list_products():
    """列出所有产品"""
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        print("\n=== 产品列表 ===")
        print(f"{'编码':<15} {'名称':<20} {'分类':<10} {'品牌':<15}")
        print("-" * 60)
        for p in products:
            print(f"{p.code:<15} {p.name:<20} {p.category or '':<10} {p.brand or '':<15}")
    finally:
        db.close()


def delete_product():
    """删除产品"""
    code = input("请输入要删除的产品编码: ").strip()
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.code == code).first()
        if not product:
            print("产品不存在！")
            return
        
        print(f"确认删除：{product.name} (编码：{code})？(y/n)")
        if input().lower() == 'y':
            db.delete(product)
            db.commit()
            print("✅ 删除成功！")
    except Exception as e:
        db.rollback()
        print(f"错误：{e}")
    finally:
        db.close()


def add_production_record():
    """添加生产记录"""
    code = input("产品编码: ").strip()
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.code == code).first()
        if not product:
            print("产品不存在！")
            return
        
        print("\n=== 添加生产记录 ===")
        stage = input("阶段名称（播种/施肥/浇水/收获等）: ").strip()
        operator = input("操作人: ").strip()
        description = input("描述: ").strip()
        
        record = ProductionRecord(
            product_id=product.id,
            stage=stage,
            operator=operator,
            description=description
        )
        db.add(record)
        db.commit()
        print("✅ 生产记录添加成功！")
    except Exception as e:
        db.rollback()
        print(f"错误：{e}")
    finally:
        db.close()


def main():
    """主菜单"""
    while True:
        print("\n" + "="*50)
        print("   农产品溯源系统 - 管理工具")
        print("="*50)
        print("1. 创建新产品")
        print("2. 查看产品列表")
        print("3. 删除产品")
        print("4. 添加生产记录")
        print("5. 初始化示例数据")
        print("0. 退出")
        print("-"*50)
        
        choice = input("请选择操作: ").strip()
        
        if choice == '1':
            create_product()
        elif choice == '2':
            list_products()
        elif choice == '3':
            delete_product()
        elif choice == '4':
            add_production_record()
        elif choice == '5':
            from init_data import init_sample_data
            init_sample_data()
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效选择，请重试！")


if __name__ == "__main__":
    main()