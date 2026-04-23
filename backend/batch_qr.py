"""
批量二维码生成工具
支持生成10000+个二维码并打包下载
"""
import qrcode
import zipfile
import io
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


def generate_single_qr(code, base_url, size=300, with_label=True):
    """生成单个二维码，可选添加文字标签"""
    # 创建二维码
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    url = f"{base_url}?code={code}"
    qr.add_data(url)
    qr.make(fit=True)
    
    # 生成图像
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert('RGB')
    
    if with_label:
        # 添加文字标签
        label_height = 60
        new_img = Image.new('RGB', (size, size + label_height), 'white')
        
        # 调整二维码大小
        qr_size = size - 20
        img = img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # 粘贴二维码
        new_img.paste(img, (10, 10))
        
        # 添加文字
        draw = ImageDraw.Draw(new_img)
        
        # 尝试加载字体
        try:
            # 尝试不同平台的中文字体
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/System/Library/Fonts/STHeiti Light.ttc",  # macOS备选
                "C:/Windows/Fonts/simhei.ttf",  # Windows
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
            ]
            font = None
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, 20)
                    break
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 绘制编码文字
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        draw.text((text_x, size + 15), code, fill='black', font=font)
        
        img = new_img.resize((size, size + label_height))
    else:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    return img


def generate_batch_qr(codes, base_url, size=300, with_label=True, format='png'):
    """
    批量生成二维码
    
    Args:
        codes: 产品编码列表
        base_url: 溯源页面基础URL
        size: 二维码尺寸
        with_label: 是否添加文字标签
        format: 图片格式 (png, jpg)
    
    Returns:
        bytes: ZIP文件的二进制数据
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, code in enumerate(codes):
            # 生成二维码
            img = generate_single_qr(code, base_url, size, with_label)
            
            # 保存到内存
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=format.upper())
            img_buffer.seek(0)
            
            # 添加到zip
            filename = f"{code}.{format}"
            zip_file.writestr(filename, img_buffer.getvalue())
            
            # 每100个打印进度
            if (i + 1) % 100 == 0:
                print(f"已生成 {i + 1}/{len(codes)} 个二维码...")
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def generate_print_layout(codes, base_url, layout='a4', cols=5, rows=8):
    """
    生成打印排版（A4纸布局）
    
    Args:
        codes: 产品编码列表
        base_url: 溯源页面基础URL
        layout: 纸张类型 (a4, letter)
        cols: 每行二维码数量
        rows: 每页二维码行数
    
    Returns:
        bytes: PDF文件的二进制数据
    """
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    import io
    
    # 选择纸张尺寸
    page_size = A4 if layout == 'a4' else letter
    page_width, page_height = page_size
    
    # 计算每个二维码的尺寸和间距
    margin = 10 * mm
    qr_size = min(
        (page_width - 2 * margin) / cols,
        (page_height - 2 * margin) / rows
    ) * 0.9  # 留一些间距
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    qr_per_page = cols * rows
    
    for i, code in enumerate(codes):
        page_index = i % qr_per_page
        col = page_index % cols
        row = page_index // cols
        
        # 计算位置
        x = margin + col * (qr_size + 5 * mm)
        y = page_height - margin - (row + 1) * (qr_size + 5 * mm)
        
        # 生成二维码图像
        img = generate_single_qr(code, base_url, int(qr_size * 2.83), with_label=True)
        
        # 保存临时图像
        temp_buffer = io.BytesIO()
        img.save(temp_buffer, format='PNG')
        temp_buffer.seek(0)
        
        # 绘制到PDF
        c.drawImage(temp_buffer, x, y, width=qr_size, height=qr_size * 1.2)
        
        # 翻页
        if (i + 1) % qr_per_page == 0 and i < len(codes) - 1:
            c.showPage()
        
        if (i + 1) % 100 == 0:
            print(f"已排版 {i + 1}/{len(codes)} 个二维码...")
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def main():
    """命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量生成溯源二维码')
    parser.add_argument('--codes', '-c', required=True, help='产品编码文件（每行一个）')
    parser.add_argument('--url', '-u', required=True, help='溯源页面基础URL')
    parser.add_argument('--output', '-o', default='qrcodes.zip', help='输出文件名')
    parser.add_argument('--size', '-s', type=int, default=300, help='二维码尺寸（像素）')
    parser.add_argument('--format', '-f', default='png', choices=['png', 'jpg'], help='图片格式')
    parser.add_argument('--pdf', action='store_true', help='生成PDF打印版')
    parser.add_argument('--cols', type=int, default=5, help='PDF每行数量')
    parser.add_argument('--rows', type=int, default=8, help='PDF每页行数')
    
    args = parser.parse_args()
    
    # 读取编码列表
    with open(args.codes, 'r', encoding='utf-8') as f:
        codes = [line.strip() for line in f if line.strip()]
    
    print(f"开始生成 {len(codes)} 个二维码...")
    
    if args.pdf:
        # 生成PDF
        output_file = args.output.replace('.zip', '.pdf')
        pdf_data = generate_print_layout(codes, args.url, cols=args.cols, rows=args.rows)
        with open(output_file, 'wb') as f:
            f.write(pdf_data)
        print(f"✅ PDF打印版已生成: {output_file}")
    else:
        # 生成ZIP
        zip_data = generate_batch_qr(codes, args.url, args.size, format=args.format)
        with open(args.output, 'wb') as f:
            f.write(zip_data)
        print(f"✅ 二维码包已生成: {args.output}")
        print(f"   包含 {len(codes)} 个二维码文件")


if __name__ == '__main__':
    main()
