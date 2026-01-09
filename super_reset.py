import os
import sys

# 1. 定位环境
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from flask import Flask
from database.models import db, User, Item, Category, Order, Favorite, Review

# 2. 配置应用
app = Flask(__name__)
db_path = os.path.join(current_dir, 'softapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        print(f"🔄 正在执行超级重置...")
        
        # 3. 彻底清空并重建表
        db.drop_all()
        db.create_all()
        print("✅ 数据库表结构重建完成")

        # 4. 初始化所有分类 (这次全加上！)
        categories = ['电子数码', '书籍资料', '生活用品', '美妆护肤', '运动器材', '虚拟商品']
        cat_objects = []
        for name in categories:
            c = Category(name=name)
            db.session.add(c)
            cat_objects.append(c)
        db.session.commit()
        print(f"✅ 已添加 {len(categories)} 个分类")

        # 5. 重建用户：李晨
        user = User(username='李晨', password_hash='123456', phone='17731882550')
        db.session.add(user)
        db.session.commit()
        print("✅ 用户 [李晨] 重建成功 (ID=1)")

        # 6. 随便加个测试商品，防止首页是个大白板
        demo_item = Item(
            title='九成新 iPhone 13 (演示)',
            price=2999.0,
            current_price=2999.0,
            description='系统自动生成的测试商品',
            image_data='https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg',
            seller_id=user.id,
            category_id=cat_objects[0].id, # 归到电子数码
            status='上架'
        )
        db.session.add(demo_item)
        db.session.commit()

        print("\n🎉🎉🎉 超级重置完成！现在去启动后端吧！")