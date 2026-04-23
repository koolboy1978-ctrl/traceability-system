"""
农产品溯源系统 - 初始化示例数据
"""
from database import SessionLocal, init_db
from models import Product, FarmInfo, ProductionRecord, QualityRecord
from datetime import datetime, timedelta


def init_sample_data():
    """初始化示例数据"""
    init_db()
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing = db.query(Product).filter(Product.code == "DEMO001").first()
        if existing:
            print("示例数据已存在，跳过初始化")
            return
        
        # 创建示例产品
        product = Product(
            code="DEMO001",
            name="有机红富士苹果",
            category="水果",
            brand="阳光果园",
            origin="山东省烟台市栖霞镇",
            description="来自山东烟台的有机红富士苹果，阳光充足，土壤肥沃，采用有机种植方式，口感脆甜多汁。"
        )
        db.add(product)
        db.flush()
        
        # 创建农场信息
        farm_info = FarmInfo(
            product_id=product.id,
            farm_name="阳光有机果园",
            location="山东省烟台市栖霞镇",
            area=50.0,
            certification="有机食品认证 CNCA-2024-0088",
            story="阳光果园始创于1995年，三代果农传承，坚持有机种植20年。我们相信，只有健康的土壤才能种出健康的水果。每一颗苹果都承载着我们对土地的敬畏和对品质的坚持。"
        )
        db.add(farm_info)
        
        # 创建生产记录
        records = [
            ("春季修剪", "老张", "对果树进行春季修剪，促进新枝生长"),
            ("开花授粉", "小李", "人工辅助授粉，提高坐果率"),
            ("套袋保护", "老王", "使用环保纸袋保护果实，减少农药残留"),
            ("有机施肥", "小李", "施用有机堆肥，提供营养"),
            ("定期灌溉", "老张", "采用滴灌技术，节约用水"),
            ("果实采摘", "老王", "人工采摘，确保果实完整"),
            ("分拣包装", "小李", "按照大小、颜色分拣，精品包装"),
        ]
        
        base_date = datetime.now() - timedelta(days=120)
        for i, (stage, operator, desc) in enumerate(records):
            record = ProductionRecord(
                product_id=product.id,
                stage=stage,
                date=base_date + timedelta(days=i * 15),
                operator=operator,
                description=desc
            )
            db.add(record)
        
        # 创建质检记录
        quality_records = [
            ("农药残留检测", "合格", "检测员李明", "未检出农药残留"),
            ("糖度检测", "合格", "检测员王芳", "糖度 14.5%，口感极佳"),
            ("外观检测", "合格", "检测员张伟", "果形端正，色泽鲜艳"),
        ]
        
        check_date = datetime.now() - timedelta(days=10)
        for i, (stage, result, inspector, notes) in enumerate(quality_records):
            record = QualityRecord(
                product_id=product.id,
                stage=stage,
                check_date=check_date - timedelta(days=i * 3),
                inspector=inspector,
                result=result,
                notes=notes
            )
            db.add(record)
        
        db.commit()
        print("示例数据初始化成功！")
        print("测试编码：DEMO001")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败：{e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()