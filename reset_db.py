import os
import sys
# 1. 强力路径修复
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database.models import db, User, Item, Category

# 2. 配置应用
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'softapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        print(f"🔄 正在重置数据库: {db_path}")
        # 3. 彻底重来：先删后建
        db.drop_all()
        db.create_all()
        print("✅ 表结构重建完成")

        # 4. 创建用户：李晨
        user = User(username='李晨', password_hash='123456', phone='17731882550')
        db.session.add(user)
        
        # 5. 造点数据：分类和商品
        cat = Category(name='电子数码')
        db.session.add(cat)
        db.session.commit() # 提交以获取 ID

        item = Item(title='九成新 iPhone 13', price=2999.0, description='自用手机', 
                   seller_id=user.id, category_id=cat.id, status='上架')
        db.session.add(item)
        
        db.session.commit()
        print("🎉 数据注入成功！用户: 李晨 / 123456")