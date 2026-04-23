"""
农产品溯源系统 - 数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Product(Base):
    """产品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 产品编码（二维码内容）
    name = Column(String(100), nullable=False)  # 产品名称
    category = Column(String(50))  # 分类（蔬菜、水果、畜禽等）
    brand = Column(String(100))  # 品牌名称
    origin = Column(String(200))  # 产地
    description = Column(Text)  # 产品描述
    image_url = Column(Text)  # 产品图片（可存base64 Data-URL）
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联记录
    production_records = relationship("ProductionRecord", back_populates="product")
    quality_records = relationship("QualityRecord", back_populates="product")
    farm_info = relationship("FarmInfo", back_populates="product", uselist=False)


class FarmInfo(Base):
    """农场信息表"""
    __tablename__ = "farm_info"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    farm_name = Column(String(100))  # 农场名称
    location = Column(String(200))  # 农场位置
    area = Column(Float)  # 种植面积/养殖面积
    certification = Column(String(200))  # 认证信息
    story = Column(Text)  # 品牌故事
    video_url = Column(String(500))  # 视频链接

    cert_image = Column(Text)  # 认证证书图片（base64 Data-URL）

    product = relationship("Product", back_populates="farm_info")


class ProductionRecord(Base):
    """生产记录表"""
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    stage = Column(String(50))  # 生产阶段（播种、施肥、浇水、收获等）
    date = Column(DateTime, default=datetime.utcnow)  # 操作日期
    operator = Column(String(50))  # 操作人
    description = Column(Text)  # 操作描述
    image_url = Column(Text)  # 操作图片（可存base64 Data-URL）

    product = relationship("Product", back_populates="production_records")


class QualityRecord(Base):
    """质检记录表"""
    __tablename__ = "quality_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    check_date = Column(DateTime, default=datetime.utcnow)  # 质检日期
    inspector = Column(String(50))  # 质检员
    result = Column(String(20))  # 结果（合格/不合格）
    report_url = Column(Text)  # 质检报告链接（可存base64 Data-URL）
    notes = Column(Text)  # 备注

    product = relationship("Product", back_populates="quality_records")