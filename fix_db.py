import os
import sys

# 1. 强力路径修复 (确保能找到 database)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask import Flask
# 引入你的数据库模型
from database.models import db, User, Item

# 2. 配置应用
app = Flask(__name__)
# 确保连的是同一个数据库 softapp.db
db_path = os.path.join(current_dir, 'softapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 3. 开始干活
if __name__ == '__main__':
    print(f"🔄 正在连接数据库: {db_path}")
    with app.app_context():
        # A. 创建所有表 (如果表不存在)
        try:
            db.create_all()
            print("✅ 数据库表结构创建成功！")
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            sys.exit(1)

        # B. 检查并添加用户
        existing_user = User.query.filter_by(username='李晨').first()
        if not existing_user:
            user = User(username='李晨', password_hash='123456', phone='17731882550')
            db.session.add(user)
            db.session.commit()
            print("👤 用户 [李晨] 创建成功！密码: 123456")
        else:
            print("ℹ️ 用户 [李晨] 已经存在，跳过创建。")

    print("\n🚀 修复完成！现在请去网页登录吧！")