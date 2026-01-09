import sys
import os

# 1. 强力路径修复：把根目录插到最前面 (Priority #1)
# 获取 agents 文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取根目录路径 (agents 的上一级)
root_dir = os.path.dirname(current_dir)

# 强制把根目录加入到 Python 搜索路径的第一位！
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from flask import Flask, request, jsonify
from flask_cors import CORS
from database.models import db, Item, Category, Favorite, Review, User, Order

# ⭐ 关键修复：尝试引入智能体，如果出错就跳过，保证服务器不崩
try:
    # 这里的写法去掉了那个害人的 "." (点)
    from .seller_agent import SellerAgent
    print("✅ 智能体模块加载成功")
except ImportError as e:
    print(f"⚠️ 智能体模块加载跳过 (使用模拟回复): {e}")
    SellerAgent = None
except Exception as e:
    print(f"⚠️ 智能体模块加载出错: {e}")
    SellerAgent = None

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# 2. 连接数据库
# ==========================================
db_path = os.path.join(root_dir, 'softapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET'])
def home():
    return "Backend (Fixed Version) is Running!"

# --- 配图辅助函数 ---
def get_magic_image(cat_name):
    if '电子' in cat_name or '数码' in cat_name:
        return 'https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg'
    elif '书' in cat_name:
        return 'https://img.yzcdn.cn/vant/cat.jpeg'
    elif '衣' in cat_name:
        return 'https://fastly.jsdelivr.net/npm/@vant/assets/apple-1.jpeg'
    else:
        return 'https://fastly.jsdelivr.net/npm/@vant/assets/apple-2.jpeg'

# ==========================================
# 3. 核心功能接口
# ==========================================

# 注册
@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter((User.username == data['username']) | (User.phone == data['phone'])).first():
        return jsonify({'success': False, 'message': '用户已存在'})
    
    new_user = User(username=data['username'], password_hash=data['password'], phone=data['phone'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': '注册成功'})

# 登录
@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password_hash == data['password']:
        return jsonify({
            'success': True, 
            'message': '登录成功',
            'data': {'id': user.id, 'username': user.username, 'phone': user.phone, 'avatar': ''}
        })
    return jsonify({'success': False, 'message': '账号或密码错误'})

# 商品列表
@app.route('/api/v1/items', methods=['GET'])
def get_items():
    items = Item.query.order_by(Item.created_at.desc()).all()
    res = []
    for i in items:
        cat = i.category_ref.name if hasattr(i, 'category_ref') and i.category_ref else '其他'
        res.append({
            'id': i.id, 'title': i.title, 'price': float(i.current_price),
            'desc': i.description, 'category': cat, 'isUrgent': i.is_urgent_sale,
            'img': get_magic_image(cat), 'view': i.view_count
        })
    return jsonify({'success': True, 'data': res})

# 收藏/取消
@app.route('/api/v1/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    uid = 6 # 默认李晨
    fav = Favorite.query.filter_by(user_id=uid, item_id=data['item_id']).first()
    if fav:
        db.session.delete(fav)
        state = False
    else:
        db.session.add(Favorite(user_id=uid, item_id=data['item_id']))
        state = True
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': state})

# 我的收藏
@app.route('/api/v1/my/favorites', methods=['GET'])
def my_favorites():
    favs = Favorite.query.filter_by(user_id=6).all()
    res = []
    for f in favs:
        i = f.item
        cat = i.category_ref.name if i.category_ref else '其他'
        res.append({
            'id': i.id, 'title': i.title, 'price': float(i.current_price),
            'img': get_magic_image(cat)
        })
    return jsonify({'success': True, 'data': res})

# 评价列表
@app.route('/api/v1/reviews/<int:item_id>', methods=['GET'])
def get_reviews(item_id):
    orders = Order.query.filter_by(item_id=item_id).all()
    order_ids = [o.id for o in orders]
    reviews = Review.query.filter(Review.order_id.in_(order_ids)).all()
    res = []
    for r in reviews:
        user = User.query.get(r.reviewer_id)
        res.append({
            'id': r.id, 'userName': user.username if user else '匿名',
            'content': r.content, 'rating': int(r.rating), 'date': r.created_at.strftime('%Y-%m-%d')
        })
    return jsonify({'success': True, 'data': res})

# 发布评价
@app.route('/api/v1/reviews', methods=['POST'])
def add_review():
    data = request.json
    demo_order = Order.query.filter_by(item_id=data['item_id']).first()
    oid = demo_order.id if demo_order else 1
    new_r = Review(order_id=oid, reviewer_id=6, reviewed_id=1, rating=str(data['rating']), content=data['content'], type='买家评价卖家')
    db.session.add(new_r)
    db.session.commit()
    return jsonify({'success': True})

# 智能体对话

# ========== 新增：买家议价建议接口 ==========
from .buyer_agent import BuyerAgent
from .context import BuyerContext, SellerContext

@app.route('/api/agent/buyer/advice', methods=['POST'])
def buyer_advice():
    data = request.json
    try:
        # 构造BuyerContext需要的参数
        ctx = BuyerContext(
            user_id=data.get('user_id', 0),
            item_id=data.get('item_id', 0),
            item_category=data.get('item_category', '其他'),
            item_condition=data.get('item_condition', 'GOOD'),
            item_listed_price=float(data.get('item_listed_price', 0)),
            market_avg_price=float(data.get('market_avg_price', 0) or data.get('item_listed_price', 0)),
            buyer_max_budget=float(data.get('buyer_max_budget', 0)),
            buyer_urgency=int(data.get('buyer_urgency', 3)),
            seller_credit_score=int(data.get('seller_credit_score', 80)),
            buyer_credit_score=int(data.get('buyer_credit_score', 80))
        )
        agent = BuyerAgent()
        # 判断是否首轮出价
        if data.get('is_first', True):
            result = agent.generate_first_offer(ctx)
        else:
            seller_price = data.get('seller_price', 0)
            result = agent.generate_counter_offer(ctx, seller_price)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"买家智能体错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'买家智能体出错: {e}'})

# ========== 新增：卖家回应建议接口 ==========
@app.route('/api/agent/seller/response', methods=['POST'])
def seller_response():
    data = request.json
    try:
        # 构造SellerContext需要的参数
        ctx = SellerContext(
            user_id=data.get('user_id', 0),
            item_id=data.get('item_id', 0),
            item_category=data.get('item_category', '其他'),
            item_condition=data.get('item_condition', 'GOOD'),
            item_listed_price=float(data.get('item_listed_price', 0)),
            market_avg_price=float(data.get('market_avg_price', 0) or data.get('item_listed_price', 0)),
            seller_min_price=float(data.get('seller_min_price', 0)),
            is_urgent_sale=bool(data.get('is_urgent_sale', False)),
            buyer_credit_score=int(data.get('buyer_credit_score', 80)),
            seller_credit_score=int(data.get('seller_credit_score', 80))
        )
        agent = SellerAgent() if SellerAgent else None
        buyer_offer = float(data.get('buyer_offer', 0))
        if agent:
            result = agent.respond_to_offer(ctx, buyer_offer)
        else:
            result = {'action': 'MOCK', 'price': ctx.seller_min_price, 'message': '模拟回复', 'reasoning': '未加载真实智能体'}
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"卖家智能体错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'卖家智能体出错: {e}'})

# 保留原有对话接口
@app.route('/api/agent/chat', methods=['POST'])
def chat_agent():
    data = request.json
    msg = data.get('message', '')
    # 尝试调用真实 Agent
    if SellerAgent:
        try:
            reply = f"（智能体在线）收到：{msg}"
        except:
            reply = "智能体正如火如荼地思考中... (功能连接中)"
    else:
        if "便宜" in msg: reply = "亲，这已经是跳楼价了！"
        elif "学生" in msg: reply = "学生党不容易，给您抹个零！"
        else: reply = "收到： " + msg
    return jsonify({'success': True, 'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)