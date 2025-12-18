from slugify import slugify
import bleach
import uuid
from models import DynamicPage
from sqlalchemy.exc import SQLAlchemyError

class AIPageGenerator:
    def __init__(self, db, app_config):
        self.db = db
        self.app_config = app_config

        self.allowed_html_tags = app_config.get(
            "ALLOWED_HTML_TAGS",
            ["div", "p", "h2", "h3", "h4", "ul", "li", "a", "strong", "em", "code", "pre"]
        )
        self.allowed_html_attrs = app_config.get(
            "ALLOWED_HTML_ATTRS",
            {"a": ["href", "target", "rel"], "code": ["class"]}
        )
    
    def _generate_unique_slug(self, title):
        """
        生成唯一的URL友好slug（内部私有方法）
        :param title: 大模型生成的页面标题
        :return: 唯一slug字符串
        """
        # 基础slug：标题转小写、替换空格为横杠、去除特殊字符
        base_slug = slugify(title, lowercase=True, separator="-", max_length=80)
        if not base_slug:  # 极端情况：标题无有效字符，用uuid生成slug
            base_slug = f"ai-page-{str(uuid.uuid4())[:10]}"
        
        # 检查slug是否重复，重复则添加8位uuid后缀
        slug = base_slug
        while DynamicPage.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        return slug

    def _clean_html_content(self, content):
        """
        过滤大模型生成的HTML内容（防止恶意脚本，内部私有方法）
        :param content: 大模型生成的原始HTML
        :return: 过滤后的安全HTML
        """
        if not content:
            return ""
        # 使用bleach过滤危险标签和属性
        cleaned_content = bleach.clean(
            content,
            tags=self.allowed_html_tags,
            attributes=self.allowed_html_attrs,
            strip=True  # 移除不允许的标签（而非转义）
        )
        return cleaned_content
    
    def create_dynamic_page(self, title, content, content_type="html", category="general", is_public=True):
        """
        核心方法：创建大模型动态页面（对外提供的公共接口）
        :param title: 页面标题（必填）
        :param content: 页面内容（必填，HTML或Markdown）
        :param content_type: 内容格式（html/markdown，默认html）
        :param category: 页面分类（默认general，可扩展tech/life等）
        :param is_public: 是否公开访问（默认True）
        :return: 字典形式的页面信息（slug、url、title等）
        :raises ValueError: 缺少必填参数或参数非法
        :raises SQLAlchemyError: 数据库存储异常
        """
        # 1. 校验必填参数
        if not title or not isinstance(title, str) or len(title) > 200:
            raise ValueError("标题必填，且长度不能超过200字符")
        if not content or not isinstance(content, str):
            raise ValueError("内容必填")
        if content_type not in ["html", "markdown"]:
            raise ValueError("内容格式仅支持html或markdown")

        # 2. 生成唯一slug
        slug = self._generate_unique_slug(title)

        # 3. 过滤HTML内容（仅当content_type为html时过滤）
        if content_type == "html":
            cleaned_content = self._clean_html_content(content)
        else:
            cleaned_content = content  # Markdown无需过滤，前端渲染时处理

        # 4. 存储到数据库
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

            # 5. 返回页面信息（供前端跳转使用）
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