# 检查数据库表结构的脚本
import sqlite3
import os

# 获取数据库文件路径
app_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(app_root, 'instance', 'forum.db')

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询online_disk_share表的结构
print("online_disk_share表结构:")
cursor.execute("PRAGMA table_info(online_disk_share);")
columns = cursor.fetchall()
for column in columns:
    print(f"  {column[1]} ({column[2]}) - 主键: {column[5]}, 非空: {column[3]}")

# 查询所有表
print("\n所有表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  {table[0]}")

# 关闭连接
conn.close()