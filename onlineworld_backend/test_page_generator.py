import sys
import os
import tempfile

# 添加项目根目录到sys.path，确保模块导入正确
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask
from onlineworld_backend.config import Config
from onlineworld_backend.forum.models import db, DynamicPage
from onlineworld_backend.ai_page_generator import AIPageGenerator

def test_ai_page_generator():
    """
    测试AI页面生成器的功能
    """
    try:
        # 创建Flask应用实例
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # 配置应用
        app.config["ALLOWED_HTML_TAGS"] = ["div", "p", "h2", "h3", "h4", "ul", "li", "a", "strong", "em", "code", "pre", "img"]
        app.config["ALLOWED_HTML_ATTRS"] = {"a": ["href", "target", "rel"], "code": ["class"], "img": ["src", "alt", "title", "width", "height"]}
        
        # 初始化数据库
        db.init_app(app)
        
        # 创建应用上下文
        with app.app_context():
            # 确保数据库表存在并更新结构
            db.create_all()
            
            # 检查并添加缺失的列（兼容旧表结构）
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('dynamic_page')]
            
            # 使用原始SQL添加缺失的列
            with db.engine.connect() as conn:
                if 'category' not in columns:
                    conn.execute(db.text('ALTER TABLE dynamic_page ADD COLUMN category VARCHAR(50) DEFAULT "general"'))
                if 'is_public' not in columns:
                    conn.execute(db.text('ALTER TABLE dynamic_page ADD COLUMN is_public BOOLEAN DEFAULT TRUE'))
            db.session.commit()
            
            # 初始化AI页面生成器
            ai_page_generator = AIPageGenerator(db, app.config)
            
            # 生成一个测试页面
            print("开始生成测试页面...")
            page_info = ai_page_generator.create_dynamic_page(
                title="人工智能的未来发展",
                category="tech",
                is_public=True,
                include_image=True
            )
            
            print("\n页面生成成功！")
            print(f"页面标题: {page_info['title']}")
            print(f"页面URL: {page_info['page_url']}")
            print(f"页面分类: {page_info['category']}")
            print(f"创建时间: {page_info['create_time']}")
            
            # 从数据库中获取页面内容
            page = DynamicPage.query.filter_by(slug=page_info['slug']).first()
            if page:
                print("\n页面内容预览:")
                print(page.content[:200] + "...")  # 只显示前200个字符
                
                # 生成完整的HTML页面
                full_html = ai_page_generator.generate_full_html_page(page.title, page.content)
                
                # 检查是否包含图片标签
                if "<img" in full_html:
                    print("\n✅ 生成的HTML包含图片标签")
                else:
                    print("\n❌ 生成的HTML不包含图片标签")
                
                # 检查是否引用了CSS文件
                if '<link rel="stylesheet" href="/static/css/main.css">' in full_html:
                    print("✅ 生成的HTML引用了通用CSS文件")
                else:
                    print("❌ 生成的HTML未引用通用CSS文件")
                

            
            print("\n测试完成！")
            return True
            
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ai_page_generator()
