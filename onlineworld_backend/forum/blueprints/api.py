from flask import Blueprint, request, jsonify, make_response, send_file
import os
from .base import BasePageView, register_page_route, require_api_key
from ..models import Post, Reply, db, SearchIndex, Board, ShopProduct, DynamicPage
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 搜索接口视图类
class SearchView(BasePageView):
    def get_data(self):
        # 获取前端传递的搜索参数
        keyword = request.args.get('keyword', '').strip()
        search_type = request.args.get('type', 'post')  # 默认搜索帖子

        if not keyword:
            return {
                "results": [],
                "keyword": keyword,
                "type": search_type
            }

        # 1. 搜索帖子：模糊匹配标题或内容，关联板块信息
        if search_type == 'post':
            # 使用 LIKE 模糊查询（不区分大小写，适配不同数据库）
            posts = Post.query.filter(
                db.or_(
                    Post.title.ilike(f'%{keyword}%'),
                    Post.content.ilike(f'%{keyword}%')
                )
            ).order_by(Post.create_time.desc()).all()

            results = [{
                "id": post.id,
                "title": post.title,
                "content": post.content[:150] + "..." if len(post.content) > 150 else post.content,  # 截取前150字预览
                "author": post.author,
                "board_id": post.board.id,
                "board_name": post.board.name,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": len(post.replies)
            } for post in posts]

        # 2. 搜索用户：模糊匹配作者名，去重并统计发帖/回帖数
        elif search_type == 'user':
            # 从帖子表和回帖表中查询匹配的作者名（去重）
            post_authors = Post.query.filter(Post.author.ilike(f'%{keyword}%')).with_entities(Post.author).distinct()
            reply_authors = Reply.query.filter(Reply.author.ilike(f'%{keyword}%')).with_entities(Reply.author).distinct()
            
            # 合并去重所有匹配的用户名
            all_authors = set()
            for author in post_authors:
                all_authors.add(author[0])
            for author in reply_authors:
                all_authors.add(author[0])
            all_authors = list(all_authors)

            # 统计每个用户的发帖数和回帖数
            results = []
            for author in all_authors:
                post_count = Post.query.filter_by(author=author).count()
                reply_count = Reply.query.filter_by(author=author).count()
                results.append({
                    "author": author,
                    "post_count": post_count,
                    "reply_count": reply_count
                })

        # 其他类型默认返回空结果
        else:
            results = []

        return {
            "results": results,
            "keyword": keyword,
            "type": search_type
        }

# 注册搜索接口路由
register_page_route(api_bp, "/search", SearchView)

# ===================== 新搜索引擎API =====================

# 搜索引擎搜索视图类
class SearchEngineView(BasePageView):
    def get_data(self):
        # 获取前端传递的搜索参数
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return {
                "results": [],
                "keyword": keyword
            }
        
        # 改进的搜索算法：支持多关键词搜索
        # 1. 分割关键词，去除空字符串
        keywords = [k.strip() for k in keyword.split() if k.strip()]
        
        # 调试：输出原始关键词和分割后的关键词
        print(f"[调试] API - 原始搜索关键词: '{keyword}'")
        print(f"[调试] API - 分割后的关键词列表: {keywords}")
        
        if not keywords:
            return {
                "results": [],
                "keyword": keyword
            }
        
        # 2. 基本搜索（包含所有关键词）
        query = SearchIndex.query
        
        # 调试：输出查询构建过程
        print(f"[调试] API - 开始构建查询")
        for k in keywords:
            # 转义特殊字符，避免SQL注入
            safe_k = k.replace('%', '\\%').replace('_', '\\_')
            print(f"[调试] API - 添加关键词过滤: '{k}' (转义后: '{safe_k}')")
            print(f"[调试] API - 过滤条件: SearchIndex.title.ilike('%{safe_k}%')")
            query = query.filter(SearchIndex.title.ilike(f'%{safe_k}%', escape='\\'))
        
        # 3. 获取结果
        results = query.all()
        print(f"[调试] API - 查询结果数量: {len(results)}")
        print(f"[调试] API - 查询结果详情: {[(r.id, r.title, r.entity_type) for r in results]}")
        
        # 4. 三级排序：完全相符 > 开头匹配 > 包含匹配
        def get_sort_level(title, keyword_string):
            """获取排序级别：1级=完全匹配，2级=开头匹配，3级=包含匹配"""
            title_lower = title.lower()
            keyword_lower = keyword_string.lower()
            
            # 调试：排序级别计算
            print(f"[调试] API - 标题: '{title_lower}', 关键词: '{keyword_lower}'")
            
            # 1级：完全匹配
            if title_lower == keyword_lower:
                print(f"[调试] API -  完全匹配，返回级别1")
                return 1
            
            # 2级：开头匹配（标题以搜索词开头）
            if title_lower.startswith(keyword_lower):
                print(f"[调试] API -  开头匹配，返回级别2")
                return 2
            
            # 3级：包含匹配（标题包含搜索词）
            print(f"[调试] API -  包含匹配，返回级别3")
            return 3
        
        # 按级别排序，同一级别内按更新时间降序
        print(f"[调试] API - 开始三级排序，结果数量: {len(results)}")
        sorted_results = sorted(
            results, 
            key=lambda r: (get_sort_level(r.title, keyword), r.update_time), 
            reverse=True
        )
        print(f"[调试] API - 排序完成，排序后结果数量: {len(sorted_results)}")
        print(f"[调试] API - 排序后结果详情: {[(r.id, r.title, r.entity_type) for r in sorted_results]}")
        
        # 5. 格式化搜索结果
        formatted_results = []
        for result in sorted_results:
            formatted_results.append({
                "id": result.id,
                "title": result.title,
                "type": result.entity_type,
                "url": result.url,
                "update_time": result.update_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {
            "results": formatted_results,
            "keyword": keyword
        }

# 注册搜索引擎路由
register_page_route(api_bp, "/search-engine", SearchEngineView)

# 构建搜索索引的API（仅内部使用或管理员调用）
@api_bp.route("/search-engine/build-index", methods=["POST"])
def build_search_index():
    """
    构建搜索索引，从所有可搜索的模型中提取标题并存储到SearchIndex表
    """
    try:
        # 首先清空现有的索引
        SearchIndex.query.delete()
        db.session.commit()
        
        # 从各个模型中提取标题并创建索引
        search_indexes = []
        
        # 1. 论坛板块 (Board)
        boards = Board.query.all()
        for board in boards:
            index = SearchIndex(
                title=board.name,
                entity_type="forum_board",
                entity_id=board.id,
                url=f"/forum/board/{board.id}"
            )
            search_indexes.append(index)
        
        # 2. 论坛帖子 (Post)
        posts = Post.query.all()
        for post in posts:
            index = SearchIndex(
                title=post.title,
                entity_type="forum_post",
                entity_id=post.id,
                url=f"/forum/post/{post.id}"
            )
            search_indexes.append(index)
        
        # 3. 商城商品 (ShopProduct)
        products = ShopProduct.query.filter_by(is_active=True).all()
        for product in products:
            index = SearchIndex(
                title=product.name,
                entity_type="shop_product",
                entity_id=product.id,
                url=f"/shop/product/{product.id}"
            )
            search_indexes.append(index)
        
        # 4. 动态页面 (DynamicPage)
        pages = DynamicPage.query.filter_by(is_active=True, is_public=True).all()
        for page in pages:
            index = SearchIndex(
                title=page.title,
                entity_type="dynamic_page",
                entity_id=page.id,
                url=f"/dynamic/{page.slug}"
            )
            search_indexes.append(index)
        
        # 批量添加索引
        db.session.add_all(search_indexes)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"搜索索引构建完成，共添加 {len(search_indexes)} 条记录"
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"数据库错误：{str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"构建索引失败：{str(e)}"
        }), 500

# 大模型生成页面接口（带鉴权）
@api_bp.route("/ai/generate-page", methods=["POST"])
@require_api_key  # 保留原有鉴权装饰器
def ai_generate_page():
    """
    大模型生成动态页面的接口（仅内部/管理员调用）
    请求体：{"title": "页面标题", "content": "HTML/Markdown内容", "content_type": "html", "category": "tech"}
    """
    try:
        # 延迟导入，避免循环依赖
        from ai_page_generator import AIPageGenerator
        
        data = request.get_json()
        # 创建AI页面生成器实例
        ai_generator = AIPageGenerator(db=db, app_config=current_app.config)
        
        # 调用工具类的核心方法，创建动态页面
        page_info = ai_generator.create_dynamic_page(
            title=data.get("title"),
            content=data.get("content"),
            content_type=data.get("content_type", "html"),
            category=data.get("category", "general"),
            is_public=data.get("is_public", True)
        )
        return jsonify({
            "status": "success",
            "data": page_info
        }), 201
    except ValueError as e:
        # 参数校验失败
        return jsonify({"status": "error", "msg": str(e)}), 400
    except SQLAlchemyError as e:
        # 数据库存储失败
        return jsonify({"status": "error", "msg": f"页面生成失败：{str(e)}"}), 500
    except Exception as e:
        # 其他未知异常
        return jsonify({"status": "error", "msg": f"服务器错误：{str(e)}"}), 500

# 为未来API预留扩展空间
# 可以在这里添加更多API路由，或者创建专门的API模块
# 例如：
# @api_bp.route("/other/endpoint", methods=["GET", "POST"])
# def other_endpoint():
#     pass

# 首页数据接口（兼容前端请求）
@api_bp.route("/", methods=["GET"])
def api_index():
    """
    首页数据接口，返回论坛板块信息
    """
    try:
        # 从models导入Board模型
        from ..models import Board, db
        
        # 查询所有板块，按创建时间排序
        boards = Board.query.order_by(Board.create_time.desc()).all()
        
        # 格式化板块数据
        boards_data = []
        for board in boards:
            boards_data.append({
                "id": board.id,
                "name": board.name,
                "description": board.description,
                "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": "GreatGame论坛",
                "boards": boards_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取数据失败：{str(e)}"
        }), 500

# 板块详情接口
@api_bp.route("/board/<int:board_id>", methods=["GET"])
def api_board(board_id):
    """
    板块详情接口，返回板块信息和帖子列表
    """
    try:
        # 从models导入Board和Post模型
        from ..models import Board, Post, Reply, db
        
        # 查询板块信息
        board = Board.query.get_or_404(board_id)
        
        # 查询该板块下的所有帖子
        posts = Post.query.filter_by(board_id=board_id).order_by(Post.create_time.desc()).all()
        
        # 格式化帖子数据
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "author": post.author,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": Reply.query.filter_by(post_id=post.id).count()
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": f"论坛 - {board.name}",
                "board": {
                    "id": board.id,
                    "name": board.name,
                    "description": board.description,
                    "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "posts": posts_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取板块数据失败：{str(e)}"
        }), 500

# 帖子详情接口
@api_bp.route("/post/<int:post_id>", methods=["GET"])
def api_post(post_id):
    """
    帖子详情接口，返回帖子信息和回帖列表
    """
    try:
        # 从models导入Post、Reply和Board模型
        from ..models import Post, Reply, Board, db
        
        # 查询帖子信息
        post = Post.query.get_or_404(post_id)
        
        # 查询该帖子的所有回帖
        replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.create_time.asc()).all()
        
        # 格式化回帖数据
        replies_data = []
        for reply in replies:
            replies_data.append({
                "id": reply.id,
                "author": reply.author,
                "content": reply.content,
                "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "signature": reply.signature
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "title": post.title,
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "author": post.author,
                    "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "view_count": post.view_count,
                    "board_id": post.board_id,
                    "board_name": post.board.name
                },
                "replies": replies_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取帖子数据失败：{str(e)}"
        }), 500

# 个人页面接口
@api_bp.route("/user/<string:author>", methods=["GET"])
def api_user(author):
    """
    个人页面接口，返回用户信息、发布的帖子和回复的帖子
    """
    try:
        # 从models导入Post、Reply和Board模型
        from ..models import Post, Reply, Board, db
        
        # 查询用户发布的帖子
        posts = Post.query.filter_by(author=author).order_by(Post.create_time.desc()).all()
        
        # 格式化发布的帖子数据
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "author": post.author,
                "board_id": post.board_id,
                "board_name": post.board.name,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "reply_count": Reply.query.filter_by(post_id=post.id).count()
            })
        
        # 查询用户回复的帖子
        replies = Reply.query.filter_by(author=author).order_by(Reply.create_time.desc()).all()
        
        # 格式化回复的帖子数据
        replies_data = []
        for reply in replies:
            # 获取回复对应的帖子信息
            post = Post.query.get(reply.post_id)
            if post:
                replies_data.append({
                    "id": reply.id,
                    "post_id": reply.post_id,
                    "post_title": post.title,
                    "author": reply.author,
                    "content": reply.content,
                    "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "signature": reply.signature
                })
        
        # 计算用户的发帖数和回帖数
        post_count = len(posts_data)
        reply_count = len(replies_data)
        
        return jsonify({
            "status": "success",
            "data": {
                "title": f"个人主页 - {author}",
                "user_info": {
                    "author": author,
                    "post_count": post_count,
                    "reply_count": reply_count
                },
                "posts": posts_data,
                "replies": replies_data
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": f"获取个人页面数据失败：{str(e)}"
        }), 500



# 导入必要的模块
import os
from flask import send_file

# 添加DataSheet生成和下载的API端点
@api_bp.route("/datasheet/generate/<int:product_id>", methods=["POST"])
def generate_datasheet(product_id):
    """
    生成产品DataSheet的API端点
    :param product_id: 产品ID
    :return: JSON响应，包含生成结果和文件信息
    """
    try:
        from ..datasheet_generator import DataSheetGenerator
        
        generator = DataSheetGenerator()
        result = generator.generate_and_save_datasheet(product_id)
        
        if result["success"]:
            return jsonify({
                "status": "success",
                "data": result,
                "message": "DataSheet生成成功"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": result["message"]
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"生成DataSheet失败：{str(e)}"
        }), 500

@api_bp.route("/datasheet/download/<int:product_id>", methods=["GET"])
def download_datasheet(product_id):
    """
    下载产品DataSheet的API端点
    :param product_id: 产品ID
    :return: PDF文件下载响应
    """
    try:
        from ..models import Product
        
        # 获取产品信息
        product = Product.query.get_or_404(product_id)
        
        if not product.datasheet_url:
            return jsonify({
                "status": "error",
                "message": "该产品尚未生成DataSheet"
            }), 404
        
        # 构建文件路径
        file_path = os.path.join(current_app.root_path, product.datasheet_url.lstrip("/"))
        
        if not os.path.exists(file_path):
            return jsonify({
                "status": "error",
                "message": "DataSheet文件不存在"
            }), 404
        
        # 发送文件下载
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"下载DataSheet失败：{str(e)}"
        }), 500


@api_bp.route("/images/<path:image_filename>", methods=["GET"])
def get_image(image_filename):
    """
    通用图片访问API端点
    根据文件名从static/images目录中提供图片文件
    可以被网站的任何部分调用，而不仅限于商城功能
    """
    try:
        # 获取图片存储的基础路径
        static_dir = os.path.join(current_app.root_path, 'static')
        image_path = os.path.join(static_dir, 'images', image_filename)
        
        # 验证图片文件是否存在
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            return jsonify({"error": "图片文件不存在"}), 404
        
        # 发送图片文件
        return send_file(image_path, as_attachment=False)
        
    except Exception as e:
        current_app.logger.error(f"图片访问API错误: {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500