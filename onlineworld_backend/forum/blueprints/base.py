from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from flask.views import MethodView  # 导入Flask类视图基类
from onlineworld_backend.config import config
from ..models import db, Board, Post, Reply, PlayerStatus, DynamicPage
from datetime import datetime
from ..ai_page_generator import AIPageGenerator
from sqlalchemy.exc import SQLAlchemyError
import functools

# 核心基类（所有网页路由继承此类）
class BasePageView(MethodView):
    """网页路由基类：封装公共逻辑，子类只需实现 get_data()"""
    
    def dispatch_request(self, *args, **kwargs):
        """所有请求都会经过此方法（MethodView核心），封装公共逻辑"""
        try:
            # 第一步：生成/验证匿名玩家ID（公共逻辑）
            player_id = session.get("player_id")
            if not player_id or not PlayerStatus.query.get(player_id):
                # 新建匿名玩家
                player = PlayerStatus()
                db.session.add(player)
                db.session.commit()
                player_id = player.id
                session["player_id"] = player_id
            else:
                # 更新最后访问时间
                player = PlayerStatus.query.get(player_id)
                player.last_visit = datetime.utcnow()
                db.session.commit()

            # 第二步：调用子类实现的 get_data()，获取页面专属数据
            page_data = self.get_data(*args, **kwargs)  # 子类必须实现此方法

            # 第三步：返回统一格式的响应（公共响应格式）
            return jsonify({
                "status": "success",
                "data": {
                    "player_id": player_id,  # 所有页面都返回匿名ID（前端无需显示）
                    **page_data  # 合并子类返回的页面数据（如title、boards、posts等）
                }
            })
        except Exception as e:
            # 异常处理：返回404（拟真）
            return make_response(jsonify({
                "status": "error",
                "msg": "404 Not Found - 页面不存在或已被删除",
                "html": "<h1>404 页面不存在</h1><p>你访问的页面可能已经被删除，或者URL输入错误，请返回首页重试。</p>"
            }), 404)

    def get_data(self, *args, **kwargs):
        """子类必须实现的方法：返回页面专属数据（如 {"title": "首页", "boards": [...]}）"""
        raise NotImplementedError("子类必须实现 get_data() 方法")

# 辅助函数：简化路由注册（可选，进一步简化开发）
def register_page_route(blueprint, url_rule, view_class, endpoint=None):
    """
    注册页面路由的辅助函数，避免重复写 add_url_rule
    :param blueprint: 蓝图对象
    :param url_rule: 路由路径（如 "/"、"/board/<int:board_id>"）
    :param view_class: 视图类（继承自 BasePageView）
    :param endpoint: 路由别名（默认用视图类名小写）
    """
    if not endpoint:
        endpoint = view_class.__name__.lower()
    blueprint.add_url_rule(url_rule, view_func=view_class.as_view(endpoint))

# 接口鉴权装饰器
def require_api_key(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        from flask import current_app
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != current_app.config.get("API_KEY"):
            return jsonify({"status": "error", "msg": "无权限访问（无效API密钥）"}), 403
        return f(*args, **kwargs)
    return wrapper