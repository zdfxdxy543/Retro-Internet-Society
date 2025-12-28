import os
import sys
import json
import requests
from flask import current_app, jsonify, send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dotenv import load_dotenv
from .models import Product, db

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# 加载环境变量
load_dotenv()

# 注册中文字体
try:
    # 注册黑体字体
    simhei_path = 'C:\\Windows\\Fonts\\simhei.ttf'
    if os.path.exists(simhei_path):
        pdfmetrics.registerFont(TTFont('SimHei', simhei_path))
    else:
        # 如果系统字体不存在，尝试使用ReportLab内置字体
        current_app.logger.warning("SimHei font not found, using default font")
except Exception as e:
    current_app.logger.error(f"Font registration failed: {str(e)}")

class DataSheetGenerator:
    def __init__(self):
        self.api_key = config.SILICON_FLOW_API_KEY
        self.model_name = config.AI_MODEL_NAME
        self.api_url = config.SILICON_FLOW_API_URL

    def call_ai_api(self, prompt):
        """
        调用硅基流动AI API生成内容
        :param prompt: 提示词
        :return: AI生成的内容
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一名专业的产品文案撰写专家，擅长撰写技术产品的DataSheet内容。请保持专业、准确、简洁的风格。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            current_app.logger.error(f"AI API调用失败: {str(e)}")
            # 如果AI调用失败，返回空字符串，后续使用默认内容
            return ""

    def generate_datasheet_content(self, product):
        """
        使用AI生成DataSheet的详细内容
        :param product: Product对象
        :return: 包含AI生成内容的字典
        """
        # 直接处理product对象，不依赖to_dict方法的所有字段
        
        # 使用AI生成产品概述
        overview_prompt = f"""请为以下产品生成一个专业的产品概述（150-200字）：
产品名称：{product.name}
产品型号：{product.model}
现有描述：{product.description}"""
        ai_overview = self.call_ai_api(overview_prompt)
        
        # 使用AI生成产品特性说明
        features = []
        if product.features:
            try:
                features = json.loads(product.features)
            except json.JSONDecodeError:
                current_app.logger.error(f"产品特性JSON解析失败: {product.features}")
                # 如果JSON解析失败，尝试使用默认空列表
        
        features_prompt = f"""请为以下产品的特性生成详细说明（每条特性2-3句话）：
产品名称：{product.name}
产品型号：{product.model}
现有特性：{json.dumps(features, ensure_ascii=False)}"""
        ai_features = self.call_ai_api(features_prompt)
        
        # 使用AI生成应用场景
        application_prompt = f"""请为以下产品生成5个典型的应用场景（每条场景1句话）：
产品名称：{product.name}
产品型号：{product.model}
产品描述：{product.description}"""
        ai_applications = self.call_ai_api(application_prompt)
        
        # 处理规格信息
        specifications = {}
        if product.specifications:
            try:
                specifications = json.loads(product.specifications)
            except json.JSONDecodeError:
                current_app.logger.error(f"产品规格JSON解析失败: {product.specifications}")
                # 如果JSON解析失败，使用空字典
        
        return {
            "overview": ai_overview if ai_overview else product.description,
            "features": ai_features if ai_features else "\n".join([f"• {feature}" for feature in features]),
            "specifications": specifications,
            "applications": ai_applications if ai_applications else "",
            "product_name": product.name,
            "product_model": product.model,
            "price": product.price
        }

    def generate_pdf(self, product, output_path):
        """
        生成PDF格式的DataSheet
        :param product: Product对象
        :param output_path: 输出文件路径
        :return: 是否生成成功
        """
        try:
            # 获取AI生成的内容
            content = self.generate_datasheet_content(product)
            
            # 创建PDF文档，使用横向布局
            doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
            elements = []
            
            # 设置样式
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                fontName='SimHei'  # 添加中文字体
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=20,
                fontName='SimHei'  # 添加中文字体
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                leading=16,
                spaceAfter=12,
                fontName='SimHei'  # 添加中文字体
            )
            bullet_style = ParagraphStyle(
                'CustomBullet',
                parent=styles['Normal'],
                fontSize=12,
                leading=16,
                bulletIndent=15,
                leftIndent=25,
                spaceAfter=6,
                fontName='SimHei'  # 添加中文字体
            )
            
            # 添加标题
            elements.append(Paragraph(f"{content['product_name']} 数据手册", title_style))
            elements.append(Paragraph(f"型号: {content['product_model']}", subtitle_style))
            elements.append(Spacer(1, 20))
            
            # 添加产品概述
            elements.append(Paragraph("产品概述", subtitle_style))
            elements.append(Paragraph(content['overview'], normal_style))
            elements.append(Spacer(1, 20))
            
            # 添加产品特性
            elements.append(Paragraph("产品特性", subtitle_style))
            features_lines = content['features'].split('\n')
            for line in features_lines:
                if line.strip():
                    elements.append(Paragraph(line.strip(), bullet_style))
            elements.append(Spacer(1, 20))
            
            # 添加技术规格
            elements.append(Paragraph("技术规格", subtitle_style))
            specs_data = []
            for key, value in content['specifications'].items():
                specs_data.append([Paragraph(key, normal_style), Paragraph(value, normal_style)])
            
            specs_table = Table(specs_data, colWidths=[2*inch, 4*inch])
            specs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#edf2f7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ]))
            elements.append(specs_table)
            elements.append(Spacer(1, 20))
            
            # 添加应用场景（如果有）
            if content['applications']:
                elements.append(Paragraph("应用场景", subtitle_style))
                applications_lines = content['applications'].split('\n')
                for line in applications_lines:
                    if line.strip():
                        elements.append(Paragraph(line.strip(), bullet_style))
                elements.append(Spacer(1, 20))
            
            # 添加价格信息
            if content['price']:
                elements.append(Paragraph(f"建议零售价: ¥{content['price']}", normal_style))
                elements.append(Spacer(1, 20))
            
            # 添加页脚
            footer_style = ParagraphStyle(
                'CustomFooter',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#718096'),
                alignment=1,  # 居中对齐
                fontName='SimHei'  # 添加中文字体
            )
            elements.append(Paragraph("© 2025 未来科技有限公司. 保留所有权利.", footer_style))
            
            # 生成PDF
            doc.build(elements)
            return True
        except Exception as e:
            current_app.logger.error(f"PDF生成失败: {str(e)}")
            return False

    def generate_and_save_datasheet(self, product_id):
        """
        生成并保存DataSheet
        :param product_id: 产品ID
        :return: 包含文件路径和状态的字典
        """
        # 获取产品信息
        product = Product.query.get(product_id)
        if not product:
            return {"success": False, "message": "产品不存在"}
        
        # 创建输出目录
        output_dir = os.path.join(current_app.root_path, 'static', 'files', 'datasheets')
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        file_name = f"{product.model}_datasheet.pdf"
        output_path = os.path.join(output_dir, file_name)
        
        # 生成PDF
        if self.generate_pdf(product, output_path):
            # 更新产品的datasheet_url
            product.datasheet_url = f"/static/files/datasheets/{file_name}"
            db.session.commit()
            
            return {
                "success": True,
                "message": "DataSheet生成成功",
                "file_path": output_path,
                "datasheet_url": product.datasheet_url,
                "file_name": file_name
            }
        else:
            return {"success": False, "message": "DataSheet生成失败"}

    def generate_all_datasheets(self):
        """
        批量生成所有产品的DataSheet
        :return: 生成结果的统计信息
        """
        # 获取所有产品
        products = Product.query.all()
        total_count = len(products)
        if not products:
            return {"success": True, "message": "没有找到产品", "total": 0, "generated": 0, "skipped": 0, "failed": 0}
        
        # 创建输出目录
        output_dir = os.path.join(current_app.root_path, 'static', 'files', 'datasheets')
        os.makedirs(output_dir, exist_ok=True)
        
        # 统计信息
        generated_count = 0
        skipped_count = 0
        failed_count = 0
        
        # 遍历所有产品
        for product in products:
            # 生成文件名
            file_name = f"{product.model}_datasheet.pdf"
            output_path = os.path.join(output_dir, file_name)
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                current_app.logger.info(f"DataSheet for product {product.name} ({product.model}) already exists, skipping.")
                skipped_count += 1
                continue
            
            # 生成PDF
            current_app.logger.info(f"Generating DataSheet for product {product.name} ({product.model})...")
            if self.generate_pdf(product, output_path):
                # 更新产品的datasheet_url
                product.datasheet_url = f"/static/files/datasheets/{file_name}"
                try:
                    db.session.commit()
                    generated_count += 1
                    current_app.logger.info(f"DataSheet for product {product.name} ({product.model}) generated successfully.")
                except Exception as e:
                    current_app.logger.error(f"数据库更新失败: {str(e)}")
                    db.session.rollback()
                    failed_count += 1
            else:
                failed_count += 1
                current_app.logger.error(f"Failed to generate DataSheet for product {product.name} ({product.model}).")
        
        # 提交数据库更改
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"最终数据库提交失败: {str(e)}")
            db.session.rollback()
        
        return {
            "success": True,
            "message": f"批量生成完成",
            "total": total_count,
            "generated": generated_count,
            "skipped": skipped_count,
            "failed": failed_count
        }