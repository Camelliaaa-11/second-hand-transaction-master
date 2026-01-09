import sqlite3
import os


def init_db():
    db_file = 'second_hand.db'

    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️ 旧数据库已删除: {db_file}")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 1. 用户表
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password_hash TEXT DEFAULT '123456',
        phone TEXT,
        avatar_url TEXT DEFAULT 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. 商品表
    cursor.execute('''
    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER DEFAULT 1,
        title TEXT NOT NULL,
        description TEXT,
        category_name TEXT, 
        price REAL NOT NULL,
        status TEXT DEFAULT '上架',
        view_count INTEGER DEFAULT 0,
        is_urgent BOOLEAN DEFAULT 0,
        image_data TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. ⭐ 新增：收藏表
    cursor.execute('''
    CREATE TABLE favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. ⭐ 新增：评价表
    cursor.execute('''
    CREATE TABLE reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        user_name TEXT,
        content TEXT,
        rating INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    print("🌱 正在写入初始数据...")
    cursor.execute("INSERT INTO users (username, phone) VALUES ('李晨', '17731882550')")

    # 插入一个商品
    cursor.execute('''
        INSERT INTO items (title, description, category_name, price, is_urgent, image_data) 
        VALUES ('测试商品-iPhone', '这是一个测试用的手机', '数码产品', 2999.00, 1, '')
    ''')

    # 插入一条测试评价
    cursor.execute('''
        INSERT INTO reviews (item_id, user_name, content, rating)
        VALUES (1, '买家小王', '手机成色很新，好评！', 5)
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库结构升级完成！(含收藏+评价)")


if __name__ == '__main__':
    init_db()