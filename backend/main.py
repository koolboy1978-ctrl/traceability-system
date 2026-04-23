"""
农产品溯源系统 - FastAPI 主程序
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import shutil
import uuid
import io

from database import get_db, init_db, engine, Base

# 上传文件存储路径
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 创建 FastAPI 应用
app = FastAPI(
    title="农产品溯源系统 API",
    description="为农产品提供全流程溯源追踪服务",
    version="1.0.0"
)

# 跨域设置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class FarmInfoBase(BaseModel):
    farm_name: str
    location: Optional[str] = None
    area: Optional[float] = None
    certification: Optional[str] = None
    story: Optional[str] = None
    video_url: Optional[str] = None


class ProductionRecordBase(BaseModel):
    stage: str
    date: Optional[str] = None
    operator: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class QualityRecordBase(BaseModel):
    check_date: Optional[str] = None
    inspector: Optional[str] = None
    result: Optional[str] = "合格"
    report_url: Optional[str] = None
    notes: Optional[str] = None


class ProductBase(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    origin: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    farm_info: Optional[FarmInfoBase] = None
    production_records: Optional[List[ProductionRecordBase]] = []
    quality_records: Optional[List[QualityRecordBase]] = []


# ==================== API 接口 ====================

@app.on_event("startup")
def startup_event():
    """启动时初始化数据库"""
    init_db()


@app.get("/")
def root():
    """健康检查"""
    return {"status": "ok", "message": "农产品溯源系统 API 运行中"}


@app.get("/api/v1/product/{code}")
def get_product_by_code(code: str, db: Session = Depends(get_db)):
    """根据产品编码查询产品信息（扫码后调用的接口）"""
    from models import Product
    
    product = db.query(Product).filter(Product.code == code).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    return {
        "code": product.code,
        "name": product.name,
        "category": product.category,
        "brand": product.brand,
        "origin": product.origin,
        "description": product.description,
        "image_url": product.image_url,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "farm_info": {
            "farm_name": product.farm_info.farm_name if product.farm_info else None,
            "location": product.farm_info.location if product.farm_info else None,
            "area": product.farm_info.area if product.farm_info else None,
            "certification": product.farm_info.certification if product.farm_info else None,
            "story": product.farm_info.story if product.farm_info else None,
            "video_url": product.farm_info.video_url if product.farm_info else None,
        } if product.farm_info else None,
        "production_records": [
            {
                "stage": r.stage,
                "date": r.date.isoformat() if r.date else None,
                "operator": r.operator,
                "description": r.description,
                "image_url": r.image_url,
            }
            for r in product.production_records
        ] if product.production_records else [],
        "quality_records": [
            {
                "check_date": r.check_date.isoformat() if r.check_date else None,
                "inspector": r.inspector,
                "result": r.result,
                "report_url": r.report_url,
                "notes": r.notes,
            }
            for r in product.quality_records
        ] if product.quality_records else [],
    }


@app.post("/api/v1/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """创建新产品"""
    from models import Product, FarmInfo, ProductionRecord, QualityRecord
    
    # 检查编码是否已存在
    existing = db.query(Product).filter(Product.code == product.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="产品编码已存在")
    
    # 创建产品
    product_data = product.model_dump()
    # 移除嵌套对象
    farm_info_data = product_data.pop('farm_info', None)
    production_records_data = product_data.pop('production_records', None)
    quality_records_data = product_data.pop('quality_records', None)
    
    db_product = Product(**product_data)
    db.add(db_product)
    db.flush()
    
    # 创建农场信息
    if farm_info_data:
        farm_info = FarmInfo(product_id=db_product.id, **farm_info_data)
        db.add(farm_info)
    
    # 创建生产记录
    for record in production_records_data or []:
        if 'date' in record and record['date']:
            record['date'] = datetime.fromisoformat(record['date'].replace('Z', '+00:00'))
        prod_record = ProductionRecord(product_id=db_product.id, **record)
        db.add(prod_record)
    
    # 创建质检记录
    for record in quality_records_data or []:
        if 'check_date' in record and record['check_date']:
            record['check_date'] = datetime.fromisoformat(record['check_date'].replace('Z', '+00:00'))
        quality_record = QualityRecord(product_id=db_product.id, **record)
        db.add(quality_record)
    
    db.commit()
    db.refresh(db_product)
    
    return {"message": "产品创建成功", "id": db_product.id}


@app.get("/api/v1/products")
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取产品列表"""
    from models import Product
    products = db.query(Product).offset(skip).limit(limit).all()
    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "origin": p.origin,
        }
        for p in products
    ]


@app.delete("/api/v1/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除产品"""
    from models import Product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    db.delete(product)
    db.commit()
    return {"message": "删除成功"}


@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件（质检报告等）"""
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回文件URL
    file_url = f"/uploads/{unique_name}"
    return {"url": file_url, "filename": file.filename}


@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """获取上传的文件"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path)


@app.post("/api/v1/batch-qr")
async def generate_batch_qr_api(
    prefix: str = "",
    start: int = 1,
    count: int = 100,
    size: int = 300,
    with_label: bool = True,
    base_url: str = "https://koolboy1978-ctrl.github.io/traceability-system/"
):
    """
    批量生成二维码并打包下载
    
    - prefix: 编码前缀，如 "APPLE"
    - start: 起始编号
    - count: 生成数量（建议单次不超过5000）
    - size: 二维码尺寸
    - with_label: 是否添加文字标签
    """
    if count > 10000:
        raise HTTPException(status_code=400, detail="单次生成数量不能超过10000")
    
    # 生成编码列表
    codes = [f"{prefix}{str(i).zfill(6)}" for i in range(start, start + count)]
    
    # 导入批量生成模块
    from batch_qr import generate_batch_qr
    
    # 生成ZIP
    zip_data = generate_batch_qr(codes, base_url, size, with_label)
    
    # 返回文件
    filename = f"qrcodes_{prefix}_{start}_{start+count-1}.zip"
    return StreamingResponse(
        io.BytesIO(zip_data),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/v1/batch-qr/pdf")
async def generate_batch_qr_pdf(
    prefix: str = "",
    start: int = 1,
    count: int = 100,
    cols: int = 5,
    rows: int = 8,
    base_url: str = "https://koolboy1978-ctrl.github.io/traceability-system/"
):
    """
    批量生成二维码并排版为PDF打印版
    
    - prefix: 编码前缀
    - start: 起始编号
    - count: 生成数量（建议单次不超过5000）
    - cols: 每行数量
    - rows: 每页行数
    """
    if count > 10000:
        raise HTTPException(status_code=400, detail="单次生成数量不能超过10000")
    
    codes = [f"{prefix}{str(i).zfill(6)}" for i in range(start, start + count)]
    
    from batch_qr import generate_print_layout
    
    pdf_data = generate_print_layout(codes, base_url, cols=cols, rows=rows)
    
    filename = f"qrcodes_{prefix}_{start}_{start+count-1}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)