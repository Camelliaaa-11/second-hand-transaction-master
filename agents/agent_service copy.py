"""
智能体Web API服务
"""
import sqlite3  # <--- 新增
import os       # <--- 新增
# ... 原有的导入 ...
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import traceback

from .context import BuyerContext, SellerContext
from .negotiation_session import NegotiationSession
from .market_data import MarketDataService

# 初始化Flask应用
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
def get_db_connection():
    # 获取当前目录的上一级目录下的 db 文件
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'second_hand.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
# 初始化智能体
negotiation_session = NegotiationSession()


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'service': '二手交易智能体',
        'version': '1.0.0',
        'endpoints': {
            '/health': '健康检查',
            '/api/v1/buyer/advice': '买家建议',
            '/api/v1/seller/response': '卖家回应',
            '/api/v1/negotiation/auto': '自动谈判',
            '/api/v1/negotiation/history': '谈判历史'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'agent',
        'timestamp': '2024'
    })


@app.route('/api/v1/buyer/advice', methods=['POST'])
def get_buyer_advice():
    """
    为买家生成砍价建议

    请求体：
    {
        "user_id": 123,
        "item_id": 456,
        "item_category": "phone",
        "item_condition": "GOOD",
        "item_listed_price": 2000.0,
        "buyer_max_budget": 1800.0,
        "buyer_urgency": 3,
        "seller_id": 789
    }
    """
    try:
        data = request.json

        # 验证必要字段
        required_fields = ['item_id', 'item_listed_price', 'buyer_max_budget']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # 获取市场数据
        category = data.get('item_category', 'phone')
        condition = data.get('item_condition', 'GOOD')
        market_avg_price = MarketDataService.get_historical_average_price(category, condition)

        # 获取用户信用
        seller_credit = MarketDataService.get_user_credit_score(data.get('seller_id', 0))
        buyer_credit = MarketDataService.get_user_credit_score(data.get('user_id', 0))

        # 创建买家上下文
        buyer_ctx = BuyerContext(
            user_id=data.get('user_id', 0),
            item_id=data['item_id'],
            item_category=category,
            item_condition=condition,
            item_listed_price=float(data['item_listed_price']),
            market_avg_price=market_avg_price,
            buyer_max_budget=float(data['buyer_max_budget']),
            buyer_urgency=int(data.get('buyer_urgency', 3)),
            seller_credit_score=seller_credit,
            buyer_credit_score=buyer_credit,
            preferred_tone=data.get('preferred_tone', 'POLITE')
        )

        # 生成建议
        from .buyer_agent import BuyerAgent
        buyer_agent = BuyerAgent()
        advice = buyer_agent.generate_first_offer(buyer_ctx)

        return jsonify({
            'success': True,
            'data': advice,
            'context': {
                'market_avg_price': market_avg_price,
                'buyer_credit': buyer_credit,
                'seller_credit': seller_credit
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/v1/seller/response', methods=['POST'])
def get_seller_response():
    """
    为卖家生成回应建议

    请求体：
    {
        "user_id": 789,
        "item_id": 456,
        "item_listed_price": 2000.0,
        "seller_min_price": 1600.0,
        "buyer_offer": 1500.0,
        "is_urgent_sale": false,
        "buyer_id": 123,
        "item_category": "phone",
        "item_condition": "GOOD"
    }
    """
    try:
        data = request.json

        # 验证必要字段
        required_fields = ['item_id', 'item_listed_price', 'seller_min_price', 'buyer_offer']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        # 获取市场数据
        category = data.get('item_category', 'phone')
        condition = data.get('item_condition', 'GOOD')
        market_avg_price = MarketDataService.get_historical_average_price(category, condition)

        # 获取用户信用
        buyer_credit = MarketDataService.get_user_credit_score(data.get('buyer_id', 0))
        seller_credit = MarketDataService.get_user_credit_score(data.get('user_id', 0))

        # 创建卖家上下文
        seller_ctx = SellerContext(
            user_id=data.get('user_id', 0),
            item_id=data['item_id'],
            item_category=category,
            item_condition=condition,
            item_listed_price=float(data['item_listed_price']),
            market_avg_price=market_avg_price,
            seller_min_price=float(data['seller_min_price']),
            is_urgent_sale=bool(data.get('is_urgent_sale', False)),
            buyer_credit_score=buyer_credit,
            seller_credit_score=seller_credit,
            seller_stubbornness=int(data.get('seller_stubbornness', 3))
        )

        # 设置谈判轮次（如果有历史）
        if 'negotiation_round' in data:
            seller_ctx.negotiation_round = int(data['negotiation_round'])

        # 生成回应
        from .seller_agent import SellerAgent
        seller_agent = SellerAgent()
        response = seller_agent.respond_to_offer(seller_ctx, float(data['buyer_offer']))

        return jsonify({
            'success': True,
            'data': response,
            'context': {
                'market_avg_price': market_avg_price,
                'buyer_credit': buyer_credit,
                'seller_credit': seller_credit
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/v1/negotiation/auto', methods=['POST'])
def auto_negotiation():
    """
    执行自动谈判演示

    请求体：
    {
        "buyer": {
            "user_id": 123,
            "item_id": 456,
            "item_category": "phone",
            "item_condition": "GOOD",
            "item_listed_price": 2000.0,
            "buyer_max_budget": 1800.0,
            "buyer_urgency": 3,
            "seller_id": 789
        },
        "seller": {
            "user_id": 789,
            "item_id": 456,
            "item_listed_price": 2000.0,
            "seller_min_price": 1600.0,
            "is_urgent_sale": false,
            "buyer_id": 123
        }
    }
    """
    try:
        data = request.json

        # 验证数据
        if 'buyer' not in data or 'seller' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing buyer or seller data'
            }), 400

        buyer_data = data['buyer']
        seller_data = data['seller']

        # 获取市场数据
        category = buyer_data.get('item_category', 'phone')
        condition = buyer_data.get('item_condition', 'GOOD')
        market_avg_price = MarketDataService.get_historical_average_price(category, condition)

        # 获取用户信用
        buyer_credit = MarketDataService.get_user_credit_score(buyer_data.get('user_id', 0))
        seller_credit = MarketDataService.get_user_credit_score(seller_data.get('user_id', 0))

        # 创建买家上下文
        buyer_ctx = BuyerContext(
            user_id=buyer_data.get('user_id', 0),
            item_id=buyer_data['item_id'],
            item_category=category,
            item_condition=condition,
            item_listed_price=float(buyer_data['item_listed_price']),
            market_avg_price=market_avg_price,
            buyer_max_budget=float(buyer_data['buyer_max_budget']),
            buyer_urgency=int(buyer_data.get('buyer_urgency', 3)),
            seller_credit_score=seller_credit,
            buyer_credit_score=buyer_credit
        )

        # 创建卖家上下文
        seller_ctx = SellerContext(
            user_id=seller_data.get('user_id', 0),
            item_id=seller_data['item_id'],
            item_category=category,
            item_condition=condition,
            item_listed_price=float(seller_data['item_listed_price']),
            market_avg_price=market_avg_price,
            seller_min_price=float(seller_data['seller_min_price']),
            is_urgent_sale=bool(seller_data.get('is_urgent_sale', False)),
            buyer_credit_score=buyer_credit,
            seller_credit_score=seller_credit
        )

        # 执行自动谈判
        result = negotiation_session.simulate_auto_negotiation(buyer_ctx, seller_ctx, verbose=False)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# --- 接口1: 获取商品列表 (包含图片) ---
@app.route('/api/v1/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY created_at DESC').fetchall()
    conn.close()

    items_list = []
    for item in items:
        # ⭐ 核心逻辑：如果有真实图片数据，就用真实的；否则用默认图
        real_img = item['image_data']
        display_img = real_img if (
                    real_img and len(real_img) > 10) else 'https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg'

        items_list.append({
            'id': item['id'],
            'title': item['title'],
            'price': item['price'],
            'desc': item['description'],
            'category': item['category_name'],
            'isUrgent': bool(item['is_urgent']),
            'img': display_img,  # ⭐ 这里现在是真图了
            'want': item['view_count']
        })
    return jsonify({'success': True, 'data': items_list})


# --- 接口2: 发布商品 (接收图片) ---
@app.route('/api/v1/items', methods=['POST'])
def create_item():
    try:
        data = request.json
        print(f"📦 收到发布请求，标题: {data.get('title')}")

        # 简单检查图片数据长度，防止日志刷屏
        img_len = len(data.get('img', ''))
        print(f"📷 图片数据长度: {img_len} 字符")

        conn = get_db_connection()
        cursor = conn.cursor()

        # ⭐ 插入数据 (包含 image_data)
        cursor.execute('''
            INSERT INTO items (title, price, description, category_name, is_urgent, status, image_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title', '无标题'),
            float(data.get('price', 0)),
            data.get('desc', ''),
            data.get('category', '其他'),
            True,
            '上架',
            data.get('img', '')  # ⭐ 把前端传来的 Base64 字符串存进去
        ))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '发布成功'})

    except Exception as e:
        print(f"❌ 发布失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

    # ... 前面的代码保持不变 ...

    # --- 接口3: 切换收藏状态 (点爱心) ---
@app.route('/api/v1/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    item_id = data.get('item_id')
    user_id = 1  # 演示用，默认是当前用户ID=1

    conn = get_db_connection()
    # 检查是否已经收藏
    exist = conn.execute('SELECT * FROM favorites WHERE user_id = ? AND item_id = ?', (user_id, item_id)).fetchone()

    if exist:
        # 如果有，就取消收藏
        conn.execute('DELETE FROM favorites WHERE user_id = ? AND item_id = ?', (user_id, item_id))
        is_fav = False
    else:
        # 如果没有，就添加收藏
        conn.execute('INSERT INTO favorites (user_id, item_id) VALUES (?, ?)', (user_id, item_id))
        is_fav = True

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_favorite': is_fav})

# --- 接口4: 获取某商品的评价列表 ---
@app.route('/api/v1/reviews/<int:item_id>', methods=['GET'])
def get_reviews(item_id):
    conn = get_db_connection()
    reviews = conn.execute('SELECT * FROM reviews WHERE item_id = ? ORDER BY created_at DESC',
                           (item_id,)).fetchall()
    conn.close()

    reviews_list = []
    for r in reviews:
        reviews_list.append({
            'id': r['id'],
            'userName': r['user_name'],
            'content': r['content'],
            'rating': r['rating'],
            'date': r['created_at']
        })
    return jsonify({'success': True, 'data': reviews_list})

# --- 接口5: 发布评价 ---
@app.route('/api/v1/reviews', methods=['POST'])
def create_review():
    data = request.json
    conn = get_db_connection()
    conn.execute('INSERT INTO reviews (item_id, user_name, content, rating) VALUES (?, ?, ?, ?)',
                 (data['item_id'], '李晨', data['content'], data['rating']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- 接口6: 获取我收藏的商品列表 (用于个人中心) ---
@app.route('/api/v1/my/favorites', methods=['GET'])
def get_my_favorites():
    conn = get_db_connection()
    # 联表查询：查 favorites 表，顺便把 items 表的标题价格拿出来
    items = conn.execute('''
        SELECT i.* FROM items i
        JOIN favorites f ON i.id = f.item_id
        WHERE f.user_id = 1
    ''').fetchall()
    conn.close()

    # 转换格式
    items_list = []
    for item in items:
        # 处理图片显示逻辑
        real_img = item['image_data']
        display_img = real_img if (
                    real_img and len(real_img) > 10) else 'https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg'

        items_list.append({
            'id': item['id'],
            'title': item['title'],
            'price': item['price'],
            'img': display_img
        })
    return jsonify({'success': True, 'data': items_list})


# ==========================================
# 7. ⭐ 用户认证模块 (注册 & 登录)
# ==========================================

# 注册接口
@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')

    # 1. 检查手机号或用户名是否已存在
    if User.query.filter((User.username == username) | (User.phone == phone)).first():
        return jsonify({'success': False, 'message': '用户名或手机号已存在'})

    # 2. 创建新用户
    # 注意：实际项目中密码应该加密(hash)，这里为了演示方便直接存明文
    new_user = User(
        username=username,
        password_hash=password,  # 暂时存明文
        phone=phone
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '注册成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# 登录接口
@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # 1. 查找用户
    user = User.query.filter_by(username=username).first()

    # 2. 验证密码 (这里直接比对明文，配合 init_data.py 里的 '123456')
    if user and user.password_hash == password:
        # 登录成功，返回用户信息
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'phone': user.phone,
                # 给个随机头像
                'avatar': 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
            }
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)