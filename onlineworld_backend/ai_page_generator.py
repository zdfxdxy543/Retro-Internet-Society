from slugify import slugify
import bleach
import uuid
import requests
import json
import os
from datetime import datetime
from onlineworld_backend.forum.models import DynamicPage
from sqlalchemy.exc import SQLAlchemyError
from .image_generator import generate_image

class AIPageGenerator:
    def __init__(self, db, app_config):
        self.db = db
        self.app_config = app_config

        self.allowed_html_tags = app_config.get(
            "ALLOWED_HTML_TAGS",
            ["div", "p", "h2", "h3", "h4", "ul", "li", "a", "strong", "em", "code", "pre", "img"]
        )
        self.allowed_html_attrs = app_config.get(
            "ALLOWED_HTML_ATTRS",
            {"a": ["href", "target", "rel"], "code": ["class"], "img": ["src", "alt", "title", "width", "height"]}
        )
        
        # 硅基流动API配置
        self.silicon_flow_api_key = app_config.get("SILICON_FLOW_API_KEY", "sk-vxnqqulpbrduxkhpxmsfebvhyvwdxjebofqcjtdsjrggebvv")
        self.silicon_flow_api_url = app_config.get("SILICON_FLOW_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
        self.ai_model_name = app_config.get("AI_MODEL_NAME", "Pro/deepseek-ai/DeepSeek-V3.2-Exp")
    
    def _generate_unique_slug(self, title):
        """
        生成唯一的URL友好slug（内部私有方法）
        :param title: 大模型生成的页面标题
        :return: 唯一slug字符串
        """
        # 基础slug：标题转小写、替换空格为横杠、去除特殊字符
        base_slug = slugify(title.lower(), separator="-", max_length=80)
        if not base_slug:  # 极端情况：标题无有效字符，用uuid生成slug
            base_slug = f"ai-page-{str(uuid.uuid4())[:10]}"
        
        # 检查slug是否重复，重复则添加8位uuid后缀
        slug = base_slug
        while DynamicPage.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        return slug

    def _call_siliconflow_api(self, messages, temperature=0.7, timeout=60):
        """
        调用硅基流动大模型API
        :param messages: 对话消息列表
        :param temperature: 生成温度
        :param timeout: 请求超时时间
        :return: API响应内容
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.silicon_flow_api_key}"
        }
        
        # 确保messages是列表格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        data = {
            "model": self.ai_model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.silicon_flow_api_url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and result["choices"]:
                message = result["choices"][0]["message"]
                content = message.get("content", "").strip() or message.get("reasoning_content", "").strip()
                return content
            return None
        except Exception as e:
            print(f"API调用失败：{str(e)}")
            return None

    def _generate_html_content(self, topic, include_image=True):
        """
        使用硅基流动大模型生成HTML内容
        :param topic: 页面主题
        :param include_image: 是否包含AI生成的图片
        :return: 生成的HTML内容
        """
        # 生成图片
        image_urls = []
        if include_image:
            try:
                # 生成与主题相关的图片
                image_prompt = f"一个关于{topic}的图片，高清，美观，适合网页展示"
                image_path = generate_image(image_prompt, width=1024, height=512)
                # 转换为API URL
                image_filename = os.path.basename(image_path)
                image_url = f"/api/images/{image_filename}"
                image_urls.append(image_url)
            except Exception as e:
                print(f"生成图片失败：{str(e)}")
        
        # 生成HTML内容
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的网页内容生成器，能够根据主题生成高质量的HTML内容。生成的内容应该结构清晰，使用合适的HTML标签，并且内容丰富、有价值。如果提供了图片URL，请将图片合理地嵌入到HTML内容中。"
            },
            {
                "role": "user",
                "content": f"""请根据主题'{topic}'生成一个完整的HTML页面内容，要求：
                1. 结构完整，包含标题、段落、列表等元素
                2. 内容丰富，围绕主题展开详细说明
                3. 使用合适的HTML标签（如h2, h3, p, ul, li等）
                4. 如果有图片URL，请将其嵌入到内容中，使用合适的尺寸
                5. 只返回HTML内容，不包含其他任何文字或说明
                图片URL：{image_urls[0] if image_urls else ''}"""
            }
        ]
        
        html_content = self._call_siliconflow_api(messages)
        return html_content if html_content else f"<h2>{topic}</h2><p>未能生成相关内容</p>"

    def _clean_html_content(self, content):
        """
        过滤大模型生成的HTML内容（防止恶意脚本，内部私有方法）
        :param content: 大模型生成的原始HTML
        :return: 过滤后的安全HTML
        """
        if not content:
            return ""
        
        # 1. 使用bleach过滤危险标签和属性
        cleaned_content = bleach.clean(
            content,
            tags=self.allowed_html_tags,
            attributes=self.allowed_html_attrs,
            strip=True  # 移除不允许的标签（而非转义）
        )
        
        # 2. 过滤没有标签的内容（确保所有内容都在标签内）
        import re
        
        # 检查是否有任何HTML标签
        if not re.search(r'<[a-z][\s\S]*?>', cleaned_content, re.I):
            # 如果没有任何标签，直接返回空内容
            return ""
        
        # 找出所有有标签包裹的内容
        tagged_content = []
        
        # 匹配所有HTML标签及其内容
        tag_pattern = re.compile(r'<[a-z][\s\S]*?>([\s\S]*?)<\/[a-z]+>', re.I)
        matches = tag_pattern.findall(cleaned_content)
        
        # 如果没有匹配到任何标签内容，返回空
        if not matches:
            return ""
        
        # 重新构建HTML，只保留有标签的内容
        # 注意：这个简单实现只保留了标签内容，丢失了原始的标签结构
        # 为了更精确的实现，需要更复杂的HTML解析
        result = ""
        for match in matches:
            # 只添加非空内容
            if match.strip():
                # 将内容包裹在<p>标签中
                result += f"<p>{match.strip()}</p>"
        
        return result
    
    def create_dynamic_page(self, title, content=None, content_type="html", category="general", is_public=True, auto_generate=True, include_image=True):
        """
        核心方法：创建大模型动态页面（对外提供的公共接口）
        :param title: 页面标题（必填）
        :param content: 页面内容（可选，HTML或Markdown）
        :param content_type: 内容格式（html/markdown，默认html）
        :param category: 页面分类（默认general，可扩展tech/life等）
        :param is_public: 是否公开访问（默认True）
        :param auto_generate: 是否自动生成内容（默认True）
        :param include_image: 是否包含AI生成的图片（默认True）
        :return: 字典形式的页面信息（slug、url、title等）
        :raises ValueError: 缺少必填参数或参数非法
        :raises SQLAlchemyError: 数据库存储异常
        """
        # 1. 校验必填参数
        if not title or not isinstance(title, str) or len(title) > 200:
            raise ValueError("标题必填，且长度不能超过200字符")
        if content_type not in ["html", "markdown"]:
            raise ValueError("内容格式仅支持html或markdown")

        # 2. 生成内容（如果需要自动生成）
        if auto_generate or not content:
            generated_content = self._generate_html_content(title, include_image=include_image)
            content = generated_content

        # 3. 生成唯一slug
        slug = self._generate_unique_slug(title)

        # 4. 过滤HTML内容（仅当content_type为html时过滤）
        if content_type == "html":
            cleaned_content = self._clean_html_content(content)
        else:
            cleaned_content = content  # Markdown无需过滤，前端渲染时处理

        # 5. 存储到数据库
        try:
            new_page = DynamicPage(
                slug=slug,
                title=title,
                content=cleaned_content,
                content_type=content_type,
                category=category,
                is_public=is_public,
                is_active=True  # 默认启用页面
            )
            self.db.session.add(new_page)
            self.db.session.commit()

            # 6. 返回页面信息（供前端跳转使用）
            return {
                "slug": slug,
                "title": new_page.title,
                "page_url": f"/page/{slug}",
                "content_type": new_page.content_type,
                "category": new_page.category,
                "create_time": new_page.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except SQLAlchemyError as e:
            self.db.session.rollback()  # 数据库异常回滚
            raise SQLAlchemyError(f"动态页面存储失败：{str(e)}")
    
    def generate_full_html_page(self, title, content, css_path="/static/css/main.css"):
        """
        生成完整的HTML页面，包括头部、尾部和CSS样式
        :param title: 页面标题
        :param content: 页面内容
        :param css_path: CSS文件路径
        :return: 完整的HTML页面
        """
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_path}">
    <style>
        /* 基础样式 */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .content {{
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p>{datetime.now().strftime("%Y-%m-%d")}</p>
    </header>
    <div class="content">
        {content}
    </div>
    <footer>
        <p>页面由AI自动生成</p>
    </footer>
</body>
</html>
        """
        return html_template
        
    def deactivate_page(self, slug):
        """
        辅助方法：下架动态页面（可选扩展）
        :param slug: 页面唯一标识
        :return: 是否下架成功
        """
        page = DynamicPage.query.filter_by(slug=slug).first()
        if not page:
            return False
        page.is_active = False
        self.db.session.commit()
        return True
