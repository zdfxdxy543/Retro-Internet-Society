from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from config import config
from onlineworld_backend.models import db, Board, Post, Reply, PlayerStatus
from datetime import datetime

app = Flask(__name__)
app.config.from_object(config)
CORS(app, supports_credentials=True)  # 允许跨域（后续子域名部署用）
db.init_app(app)

# -------------------------- 初始化数据库（首次运行用）--------------------------
@app.cli.command("init-db")
def init_db():
    db.drop_all()
    db.create_all()
    # 插入测试数据（2个板块、3个帖子、5个回帖）
    board1 = Board(name="技术讨论区", description="聊聊编程、网络、硬件相关")
    board2 = Board(name="生活闲聊区", description="分享日常、八卦、求助")
    db.session.add_all([board1, board2])
    db.session.commit()

    # 帖子1（技术区，正文藏线索：源码注释有密码）
    post1 = Post(
        title="求助！老旧服务器登录密码忘了",
        content="公司有台2018年的服务器，登录密码找不到了，系统是CentOS7。试了admin、root123都不行，有没有大佬知道默认密码或者重置方法？\n（附：服务器机房在XX大厦B1层，门禁牌上的编号是8A3F）",
        author="IT小菜鸟",
        board_id=board1.id
    )
    # 帖子2（生活区，回帖藏线索）
    post2 = Post(
        title="XX大厦附近有什么好吃的？",
        content="刚来这边上班，想问下XX大厦周边有没有性价比高的午饭？不要太贵，人均20左右～",
        author="打工人小李",
        board_id=board2.id
    )
    # 帖子3（技术区，签名档藏线索）
    post3 = Post(
        title="分享一个简单的Python脚本",
        content="写了个自动备份SQLite数据库的脚本，贴出来给需要的人：\n```python\nimport shutil\nshutil.copy('data.db', 'data_backup.db')\n```",
        author="代码爱好者",
        board_id=board1.id
    )
    db.session.add_all([post1, post2, post3])
    db.session.commit()

    # 回帖（含线索：帖子1的回帖藏密码，帖子3的回帖签名档藏线索）
    reply1 = Reply(
        content="CentOS7默认没有root密码，可能是之前管理员设的。试试重置：重启按e，修改kernel参数加rd.break，然后mount /sysroot rw，chroot /sysroot，passwd root改密码～",
        author="运维老司机",
        post_id=post1.id,
        signature="专注运维10年 | 常用命令：ssh root@xxx.xxx.xxx.xxx -p 22"
    )
    reply2 = Reply(
        content="我知道！大厦对面的巷子里有家兰州拉面，18元一碗，分量超足～",
        author="吃货小张",
        post_id=post2.id,
        signature="唯有美食不可辜负"
    )
    reply3 = Reply(
        content="谢谢分享！我之前用shell写过类似的，Python版本更简洁～",
        author="脚本达人",
        post_id=post3.id,
        signature="密钥：L2FkbWluL2RhdGEv"  # Base64编码的线索，解码后是/ admin / data /
    )
    reply4 = Reply(
        content="楼主的服务器是戴尔的吗？戴尔服务器默认用户名可能是dell，密码Dell123！",
        author="硬件爱好者",
        post_id=post1.id,
        signature="硬件问题欢迎咨询"
    )
    reply5 = Reply(
        content="马克一下，下次备份数据库能用～",
        author="小白白",
        post_id=post3.id,
        signature=""
    )
    db.session.add_all([reply1, reply2, reply3, reply4, reply5])
    db.session.commit()
    print("数据库初始化成功！测试数据已插入")

# -------------------------- 核心路由（伪装成论坛路径）--------------------------
# 1. 论坛首页 → 返回所有板块
@app.route("/", methods=["GET"])
def forum_index():
    # 生成/获取匿名玩家ID
    player_id = session.get("player_id")
    if not player_id:
        player = PlayerStatus()
        db.session.add(player)
        db.session.commit()
        player_id = player.id
        session["player_id"] = player_id
    else:
        # 更新最后访问时间
        player = PlayerStatus.query.get(player_id)
        if player:
            player.last_visit = datetime.utcnow()
            db.session.commit()

    # 查询所有板块
    boards = Board.query.all()
    board_list = [{
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "create_time": board.create_time.strftime("%Y-%m-%d %H:%M:%S")
    } for board in boards]

    # 返回JSON（前端模板渲染用）
    return jsonify({
        "status": "success",
        "data": {
            "title": "复古论坛 - 首页",
            "boards": board_list,
            "player_id": player_id  # 前端无需显示，仅用于状态关联
        }
    })

# 2. 板块页面 → 返回板块下的所有帖子（路径：/board/[板块ID]）
@app.route("/board/<int:board_id>", methods=["GET"])
def board_detail(board_id):
    # 验证玩家状态
    player_id = session.get("player_id")
    if not player_id or not PlayerStatus.query.get(player_id):
        return make_response(jsonify({"status": "error", "msg": "页面不存在"}), 404)

    # 更新玩家已访问板块
    player = PlayerStatus.query.get(player_id)
    if board_id not in player.visited_boards:
        player.visited_boards.append(board_id)
        db.session.commit()

    # 查询板块（不存在返回404）
    board = Board.query.get(board_id)
    if not board:
        return make_response(jsonify({"status": "error", "msg": "板块不存在"}), 404)

    # 查询板块下的所有帖子（按时间倒序）
    posts = Post.query.filter_by(board_id=board_id).order_by(Post.create_time.desc()).all()
    post_list = [{
        "id": post.id,
        "title": post.title,
        "author": post.author,
        "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        "view_count": post.view_count,
        "reply_count": len(post.replies),
        "board_id": post.board.id,
        "board_name": post.board.name
    } for post in posts]

    # 更新板块下帖子的浏览量（模拟真实论坛）
    for post in posts:
        post.view_count += 1
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": {
            "title": f"复古论坛 - {board.name}",
            "board": {
                "id": board.id,
                "name": board.name,
                "description": board.description
            },
            "posts": post_list
        }
    })

# 3. 帖子详情页 → 返回帖子正文+所有回帖（路径：/post/[帖子ID]）
@app.route("/post/<int:post_id>", methods=["GET"])
def post_detail(post_id):
    # 验证玩家状态
    player_id = session.get("player_id")
    if not player_id or not PlayerStatus.query.get(player_id):
        return make_response(jsonify({"status": "error", "msg": "页面不存在"}), 404)

    # 更新玩家已访问帖子
    player = PlayerStatus.query.get(player_id)
    if post_id not in player.visited_posts:
        player.visited_posts.append(post_id)
        db.session.commit()

    # 查询帖子（不存在返回404）
    post = Post.query.get(post_id)
    if not post:
        return make_response(jsonify({"status": "error", "msg": "帖子不存在"}), 404)

    # 查询所有回帖（按时间正序）
    replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.create_time.asc()).all()
    reply_list = [{
        "id": reply.id,
        "content": reply.content,
        "author": reply.author,
        "signature": reply.signature,
        "create_time": reply.create_time.strftime("%Y-%m-%d %H:%M:%S")
    } for reply in replies]

    # 更新帖子浏览量
    post.view_count += 1
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": {
            "title": f"复古论坛 - {post.title}",
            "post": {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "author": post.author,
                "create_time": post.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "view_count": post.view_count,
                "board_name": post.board.name,
                "board_id": post.board.id
            },
            "replies": reply_list
        }
    })

# 5. 新人指南页面（路径：/newbie）
@app.route("/newbie", methods=["GET"])
def newbie_guide():
    # 验证玩家匿名状态（保持和其他页面一致）
    player_id = session.get("player_id")
    if not player_id:
        player = PlayerStatus()
        db.session.add(player)
        db.session.commit()
        player_id = player.id
        session["player_id"] = player_id

    # 返回静态内容（前端直接渲染，无需动态数据）
    return jsonify({
        "status": "success",
        "data": {
            "title": "复古论坛 - 新人指南",
            "player_id": player_id
        }
    })

# 6. 版规说明页面（路径：/rules）
@app.route("/rules", methods=["GET"])
def rules():
    player_id = session.get("player_id")
    if not player_id:
        player = PlayerStatus()
        db.session.add(player)
        db.session.commit()
        player_id = player.id
        session["player_id"] = player_id

    return jsonify({
        "status": "success",
        "data": {
            "title": "复古论坛 - 版规说明",
            "player_id": player_id
        }
    })

# 7. 联系我们页面（路径：/contact）
@app.route("/contact", methods=["GET"])
def contact():
    player_id = session.get("player_id")
    if not player_id:
        player = PlayerStatus()
        db.session.add(player)
        db.session.commit()
        player_id = player.id
        session["player_id"] = player_id

    return jsonify({
        "status": "success",
        "data": {
            "title": "复古论坛 - 联系我们",
            "player_id": player_id
        }
    })

# 4. 404页面（拟真）
@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({
        "status": "error",
        "msg": "404 Not Found - 页面不存在或已被删除",
        "html": "<h1>404 页面不存在</h1><p>你访问的页面可能已经被删除，或者URL输入错误，请返回首页重试。</p>"
    }), 404)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)