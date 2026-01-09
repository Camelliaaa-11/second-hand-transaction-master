
from zhipuai import ZhipuAI
import json
import re 
import random
import sys
import os
import webbrowser # 👈 确保引入了这个
# 👇 强行引入 threading 驱动，防止打包后找不到
import engineio.async_drivers.threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime 
import time
from sqlalchemy import or_ 
from flask_socketio import SocketIO, emit, join_room, leave_room
from database.models import db, Item, Category, Favorite, Review, User, Order, Message, BargainLog
# 👇 强行引入 threading 驱动，防止打包后找不到

# ==========================================
# ==== 智能体相关常量（来自 app.py） ====
import requests
import time
from werkzeug.utils import secure_filename
import os
AGENT_API_URL = "http://192.168.31.180:5011"  # 智能体服务的端口
AGENT_BUYER_ADVICE_URL = f"{AGENT_API_URL}/api/v1/advice/buyer"
AGENT_SELLER_ADVICE_URL = f"{AGENT_API_URL}/api/v1/advice/seller"
AGENT_TIMEOUT = 3  # 超时时间（秒）
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ==================== 工具函数 ====================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder='items'):
    """保存上传的文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
        file.save(filepath)
        return f"/static/uploads/{subfolder}/{filename}"
    return None
# ⭐ 核心修复：自动判断路径 (兼容代码运行和EXE运行)
# ==========================================
if getattr(sys, 'frozen', False):
    # 【EXE模式】
    # 1. 数据库要在 exe 旁边找 (sys.executable 是 exe 的路径)
    root_dir = os.path.dirname(sys.executable)
    # 2. 前端文件在临时解压目录里找 (sys._MEIPASS 是打包后的临时目录)
    static_folder = os.path.join(sys._MEIPASS, 'ui', 'dist')
else:
    # 【代码模式】
    # 1. 数据库在当前文件旁边
    root_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. 前端文件在 ./ui/dist
    static_folder = './ui/dist'

# 打印路径方便调试
print(f"📂 运行模式: {'EXE打包版' if getattr(sys, 'frozen', False) else 'Python代码版'}")
print(f"📂 数据库路径: {root_dir}")
print(f"📂 前端路径: {static_folder}")

# ==========================================
# 初始化 Flask (指向正确的 static_folder)
# ==========================================
app = Flask(__name__, static_folder=static_folder, static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

# 连接数据库
db_path = os.path.join(root_dir, 'softapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 初始化 SocketIO
# 初始化 SocketIO (强制使用 threading 模式，兼容 exe 打包)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

with app.app_context():
    # 尝试创建表，如果数据库不存在
    db.create_all()

# --- 辅助函数 ---
def get_magic_image(cat_name):
    if '电子' in cat_name: return 'https://fastly.jsdelivr.net/npm/@vant/assets/ipad.jpeg'
    return 'https://fastly.jsdelivr.net/npm/@vant/assets/apple-1.jpeg'
# ================= 业务接口 =================

# ==========================================
# ⭐ Socket.IO 实时事件处理
# 修改：获取聊天记录 (带商品信息版)
# ==========================================
@app.route('/api/v1/messages/history', methods=['GET'])
def get_chat_history():
    uid = request.args.get('userId')
    friend_id = request.args.get('friendId')
    
    msgs = Message.query.filter(
        or_(
            (Message.sender_id == uid) & (Message.receiver_id == friend_id),
            (Message.sender_id == friend_id) & (Message.receiver_id == uid)
        )
    ).order_by(Message.created_at.asc()).all()
    
    res = []
    for m in msgs:
        # ⭐ 核心修改：如果这条消息有关联商品，查出来！
        item_info = None
        if m.item_id:
            item = Item.query.get(m.item_id)
            if item:
                item_info = {
                    'id': item.id,
                    'title': item.title,
                    'price': item.current_price,
                    'img': item.image_data if item.image_data else get_magic_image(item.category_ref.name if item.category_ref else '')
                }

        res.append({
            'id': m.id,
            'senderId': m.sender_id,
            'content': m.content,
            'time': m.created_at.strftime('%H:%M'),
            'item': item_info  # ⭐ 把商品信息塞进去
        })
    return jsonify({'success': True, 'data': res})
# ==========================================
# 新增：通用列表查询接口 (我买的/卖的/发布的)
# ==========================================
# ==========================================
# 新增：通用列表查询接口 (已修复图片问题)
# ==========================================
@app.route('/api/v1/user/common_list', methods=['POST'])
def get_user_common_list():
    data = request.json
    user_id = data.get('user_id')
    list_type = data.get('type') # published, bought, sold, favorites
    
    res_list = []
    
    try:
        if list_type == 'published':
            # 查询我发布的商品
            items = Item.query.filter_by(seller_id=user_id).order_by(Item.created_at.desc()).all()
            for i in items:
                # 兼容处理图片
                img = i.image_data if i.image_data else ''
                res_list.append({
                    'id': i.id, 'title': i.title, 'price': float(i.current_price),
                    # ⭐ 核心修复：两个名字都给，前端用哪个都有图！
                    'img': img, 
                    'img_data': img, 
                    'status': i.status
                })
                
        elif list_type == 'bought':
            # 查询我买到的订单
            orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()
            for o in orders:
                item = Item.query.get(o.item_id)
                img = item.image_data if item and item.image_data else ''
                res_list.append({
                    'id': o.id, 
                    'item_id': o.item_id,
                    'item_title': item.title if item else '商品已删除',
                    # ⭐ 核心修复
                    'item_img': img,
                    'img': img, 
                    'price': float(o.final_price),
                    'status': o.status,
                    'time': o.created_at.strftime('%Y-%m-%d %H:%M')
                })
                
        elif list_type == 'sold':
            # 查询我卖出的订单
            orders = Order.query.filter_by(seller_id=user_id).order_by(Order.created_at.desc()).all()
            for o in orders:
                if o.order_no.startswith('MSG'): continue 
                
                item = Item.query.get(o.item_id)
                img = item.image_data if item and item.image_data else ''
                res_list.append({
                    'id': o.id, 
                    'item_id': o.item_id,
                    'item_title': item.title if item else '商品已删除',
                    # ⭐ 核心修复
                    'item_img': img,
                    'img': img, 
                    'price': float(o.final_price),
                    'status': o.status,
                    'time': o.created_at.strftime('%Y-%m-%d %H:%M')
                })

        elif list_type == 'favorites':
             # 查询我收藏的
             favs = Favorite.query.filter_by(user_id=user_id).all()
             for f in favs:
                 item = Item.query.get(f.item_id)
                 if item:
                     img = item.image_data if item.image_data else ''
                     res_list.append({
                        'id': item.id, 'title': item.title, 'price': float(item.current_price),
                        # ⭐ 核心修复
                        'img': img, 
                        'img_data': img,
                        'status': item.status
                    })

        return jsonify({'success': True, 'data': res_list})

    except Exception as e:
        print(f"列表查询失败: {e}")
        return jsonify({'success': False, 'message': str(e)})
# ==========================================
# 🌐 前端页面托管
# ==========================================
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# 防止刷新页面 404 (把所有未知路径都导向首页，交给 Vue 路由处理)
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')
# 1. 监听：用户加入聊天室
@socketio.on('join')
def on_join(data):
    # 生成房间号规则：小的ID在前，大的在后，确保两人无论谁进，房间号都一样
    uid1 = int(data['myId'])
    uid2 = int(data['friendId'])
    room = f"chat_{min(uid1, uid2)}_{max(uid1, uid2)}"
    
    join_room(room)
    print(f"用户 {uid1} 已加入房间: {room}")

# 2. 监听：发送消息
@socketio.on('send_msg')
def on_send(data):
    try:
        sender_id = data['senderId']
        receiver_id = data['receiverId']
        content = data['content']
        
        # A. 先存入数据库 (保证历史记录不丢失)
        new_msg = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            msg_type='文本'
        )
        db.session.add(new_msg)
        db.session.commit()
        
        # B. 广播给房间里的两个人 (实时推送)
        room = f"chat_{min(int(sender_id), int(receiver_id))}_{max(int(sender_id), int(receiver_id))}"
        
        # 把消息发回给前端
        msg_data = {
            'id': new_msg.id,
            'senderId': sender_id,
            'content': content,
            'time': new_msg.created_at.strftime('%H:%M') # 刚刚生成的
        }
        
        # emit 给房间里的所有人
        emit('new_msg', msg_data, room=room)
        print(f"消息已推送到房间 {room}: {content}")
        
    except Exception as e:
        print(f"发送消息出错: {e}")

@app.route('/api/v1/categories', methods=['GET'])
def get_categories():
    try:
        cats = Category.query.all()
        if not cats:
            defaults = ['电子数码', '书籍资料', '生活用品', '美妆护肤', '运动器材', '虚拟商品']
            for name in defaults:
                db.session.add(Category(name=name))
            db.session.commit()
            cats = Category.query.all()
        res = [{'text': c.name, 'value': c.id} for c in cats]
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'data': []})

@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter((User.username == data['username']) | (User.phone == data['phone'])).first():
        return jsonify({'success': False, 'message': '用户已存在'})
    new_user = User(username=data['username'], password_hash=data['password'], phone=data['phone'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': '注册成功'})

@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password_hash == data['password']:
        return jsonify({
            'success': True, 
            'message': '登录成功',
            'data': {'id': user.id, 'username': user.username, 'phone': user.phone, 'avatar': user.avatar}
        })
    return jsonify({'success': False, 'message': '账号或密码错误'})


# ==========================================
# 🛒 发布商品接口 (最终修复版)
# ==========================================
@app.route('/api/v1/items', methods=['POST'])
def create_item():
    try:
        data = request.json
        
        if not data.get('seller_id') or not data.get('title') or not data.get('price'):
            return jsonify({'success': False, 'message': '缺少必要信息'})

        # 获取价格数值
        price_val = float(data.get('price'))

        new_item = Item(
            seller_id = data.get('seller_id'),
            title = data.get('title'),
            
            # ✅ 修复核心：两个价格字段都填上！
            price = price_val,         # 填补那个导致报错的坑
            current_price = price_val, # 当前售价
            
            category = data.get('category', '其他'),
            description = data.get('description', ''),
            image_data = data.get('image'),
            
            # 兼容 is_urgent 或 is_urgent_sale
            is_urgent_sale = data.get('is_urgent_sale', False),
            
            status = '上架',
            created_at = datetime.now(),
            view_count = 0
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '发布成功'})

    except Exception as e:
        print(f"❌ 发布严重报错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'发布失败: {str(e)}'})
# run_server.py
# run_server.py

@app.route('/api/v1/items', methods=['GET'])
def get_items():
    category = request.args.get('category')
    search = request.args.get('search')
    
    # ⭐ 核心修改：先建立查询，并且默认只查 '上架' 的
    # 这样下架的商品就不会出现在首页了
    query = Item.query.filter(Item.status == '上架')

    # 如果有分类筛选
    if category and category != 'all':
        query = query.filter(Item.category == category)
        
    # 如果有搜索关键词
    if search:
        query = query.filter(Item.title.contains(search))
        
    # 按时间倒序
    items = query.order_by(Item.created_at.desc()).all()
    
    res = []
    for i in items:
        res.append({
            'id': i.id,
            'title': i.title,
            'price': str(i.current_price),
            'category': i.category,
            'img': i.image_data,
            'status': i.status,
            'view': i.view_count,
            'seller': i.seller.username if i.seller else '未知'
        })
    return jsonify({'success': True, 'data': res})
# ==========================================
# 补全：获取商品详情接口
# ==========================================
@app.route('/api/v1/items/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': '商品不存在'})
            
        # 增加浏览量
        item.view_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': item.id,
                'title': item.title,
                'price': str(item.current_price),
                'desc': item.description,
                
                # ⭐ 关键修复：确保图片和卖家信息都返回
                'img': item.image_data, 
                'image_data': item.image_data, 
                
                'category': item.category,
                'view': item.view_count,
                'status': item.status, # 返回上下架状态
                'create_time': item.created_at.strftime('%Y-%m-%d %H:%M'),
                
                'seller': {
                    'id': item.seller.id,
                    'name': item.seller.username
                } if item.seller else None
            }
        })
    except Exception as e:
        print(f"获取详情失败: {e}")
        return jsonify({'success': False, 'message': '服务器出错了'})
# ⭐⭐⭐ 修复收藏功能 (不再死板用6号用户) ⭐⭐⭐
@app.route('/api/v1/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    uid = data.get('userId') # 从前端获取真实用户ID
    item_id = data.get('item_id')
    
    fav = Favorite.query.filter_by(user_id=uid, item_id=item_id).first()
    if fav:
        db.session.delete(fav)
        state = False
    else:
        db.session.add(Favorite(user_id=uid, item_id=item_id))
        state = True
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': state})

@app.route('/api/v1/favorite/check', methods=['POST'])
def check_favorite():
    data = request.json
    fav = Favorite.query.filter_by(user_id=data.get('userId'), item_id=data.get('item_id')).first()
    return jsonify({'success': True, 'is_favorite': bool(fav)})

# ⭐⭐⭐ 修复评论功能 (自动创建订单以支持评论) ⭐⭐⭐
@app.route('/api/v1/reviews/<int:item_id>', methods=['GET'])
def get_reviews(item_id):
    # 1. 先查出这个商品关联的所有订单 (为了兼容旧数据)
    orders = Order.query.filter_by(item_id=item_id).all()
    order_ids = [o.id for o in orders]
    
    # 2. ⭐ 核心修改：查询条件改成“或者” (OR)
    # 条件A：是这些订单里的评价 (Review.order_id 在 list 里)
    # 条件B：直接关联了这个商品ID (Review.item_id == item_id) -> 刚才发的留言就是这种
    
    if order_ids:
        reviews = Review.query.filter(
            or_(
                Review.order_id.in_(order_ids), # 条件A
                Review.item_id == item_id       # 条件B
            )
        ).order_by(Review.created_at.desc()).all()
    else:
        # 如果还没人买过，就只查直接留言
        reviews = Review.query.filter_by(item_id=item_id).order_by(Review.created_at.desc()).all()
        
    # 3. 组装数据返回给前端
    res = []
    for r in reviews:
        # 这里的 reviewer_id 是你数据库里的字段名
        user = User.query.get(r.reviewer_id) 
        res.append({
            'id': r.id,
            'userId': r.reviewer_id,  # 👈 必须返回这个，前端删除功能要用！
            'userName': user.username if user else '匿名',
            'avatar': user.avatar if user else '', # 头像
            'content': r.content,
            'date': r.created_at.strftime('%Y-%m-%d')
        })
        
    return jsonify({'success': True, 'data': res})

# ==========================================
# 修改后：发布评价/留言 (自动同步发送私信)
# ==========================================
@app.route('/api/v1/reviews', methods=['POST'])
def add_review():
    try:
        data = request.json
        item_id = data.get('item_id')
        user_id = data.get('userId')
        content = data.get('content')
        
        # 1. 找有没有现成订单
        order = Order.query.filter_by(item_id=item_id, buyer_id=user_id).first()
        
        # 2. 如果没有订单 (只是留言)，造个虚拟订单
        if not order:
            item = Item.query.get(item_id)
            if not item: return jsonify({'success': False, 'message': '商品不存在'})
            
            import uuid
            order = Order(
                order_no=f"MSG_{int(time.time())}_{uuid.uuid4().hex[:4]}", 
                item_id=item_id, buyer_id=user_id, seller_id=item.seller_id,
                final_price=0, status='已完成', buyer_phone='-', seller_phone='-'
            )
            db.session.add(order)
            db.session.commit()

        # 3. 保存评论
        new_r = Review(
            order_id=order.id, reviewer_id=user_id, reviewed_id=order.seller_id,
            rating='5', content=content, type='买家评价卖家',
            item_id=item_id # ⭐ 加上 item_id，确保可以直接查询
        )
        db.session.add(new_r)

        # ⭐⭐ 核心新增：同时在消息表里存一条，这样消息列表就能收到了！ ⭐⭐
        # 既然是买家留言，那就是 买家 -> 发给 -> 卖家
        new_msg = Message(
            sender_id=user_id,
            receiver_id=order.seller_id,
            item_id=item_id,
            content=f"[留言] {content}", # 加个前缀区分
            msg_type='文本',
            is_read=False
        )
        db.session.add(new_msg)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        print(f"留言失败: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ==========================================
# 修改后：获取我的列表 (剔除虚拟订单)
# ==========================================
# run_server.py

@app.route('/api/v1/my/list', methods=['GET'])
def get_user_list():
    type_ = request.args.get('type')
    uid = request.args.get('userId')
    
    items_res = []
    
    try:
        if type_ == 'published':
            items_res = Item.query.filter_by(seller_id=uid).order_by(Item.created_at.desc()).all()
        elif type_ == 'sold':
            orders = Order.query.filter_by(seller_id=uid).order_by(Order.created_at.desc()).all()
            real_orders = [o for o in orders if not o.order_no.startswith('MSG')]
            items_res = [o.item for o in real_orders if o.item]
        elif type_ == 'bought':
            orders = Order.query.filter_by(buyer_id=uid).order_by(Order.created_at.desc()).all()
            real_orders = [o for o in orders if not o.order_no.startswith('MSG')]
            items_res = [o.item for o in real_orders if o.item]
        elif type_ == 'favorites':
            favs = Favorite.query.filter_by(user_id=uid).order_by(Favorite.created_at.desc()).all()
            items_res = [f.item for f in favs if f.item]

        res = []
        for i in items_res:
            if i:
                cat = i.category if hasattr(i, 'category') else '其他'
                # 优先使用 image_data
                img_val = i.image_data if i.image_data else get_magic_image(cat)
                
                res.append({
                    'id': i.id, 
                    'title': i.title, 
                    'price': float(i.current_price),
                    # ⭐ 核心修复：全都给！
                    'img': img_val,
                    'image_data': img_val,
                    'img_data': img_val, 
                    'status': i.status
                })
                
        return jsonify({'success': True, 'data': res})
        
    except Exception as e:
        print(f"获取列表报错: {e}")
        return jsonify({'success': False, 'data': [], 'message': str(e)})

# ==========================================
# 修复版：更稳健的统计接口
@app.route('/api/v1/user/stats/<int:user_id>', methods=['GET'])
def get_user_stats(user_id):
    try:
        # 1. 我发布的
        published = Item.query.filter_by(seller_id=user_id).count()
        
        # 2. 我卖出的 (查 Order 表，卖家是我，且状态不是'待付款')
        # 这里不做复杂的 MSG 过滤了，直接查 Order 表最稳
        sold = Order.query.filter_by(seller_id=user_id, status='已付款').count()
        
        # 3. 我买到的 (查 Order 表，买家是我)
        bought = Order.query.filter_by(buyer_id=user_id).count()
        
        # 4. 我收藏的 (如果没有收藏表，就默认为0，防止报错)
        try:
            fav = Favorite.query.filter_by(user_id=user_id).count()
        except:
            fav = 0
        
        print(f"📊 统计查询成功 - 用户ID:{user_id} | 发布:{published} 卖出:{sold} 买到:{bought}")
        
        return jsonify({
            'success': True,
            'data': {
                'published': published,
                'sold': sold,
                'bought': bought,
                'favorite': fav
            }
        })
    except Exception as e:
        # 如果真的出错了，把错误打印出来，方便我们看黑框框
        print(f"❌ 统计接口严重报错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': True, 'data': {'published': 0, 'sold': 0, 'bought': 0, 'favorite': 0}})
# ==========================================
# 新增接口：获取我的消息列表 (会话列表)
# ==========================================
@app.route('/api/v1/my/messages', methods=['GET'])
def get_my_messages():
    try:
        uid = request.args.get('userId')
        if not uid: return jsonify({'success': False, 'data': []})
        
        # 1. 查找所有跟我也关的消息 (我是发送者 OR 我是接收者)
        # 按时间倒序，最新的在前面
        msgs = Message.query.filter(
            or_(Message.sender_id == uid, Message.receiver_id == uid)
        ).order_by(Message.created_at.desc()).all()
        
        conversations = {}
        
        for m in msgs:
            # 2. 判断“对方”是谁
            if str(m.sender_id) == str(uid):
                other_id = m.receiver_id
            else:
                other_id = m.sender_id
            
            # 3. 如果这个人的会话还没收录，就收录第一条 (因为是倒序，第一条就是最新的)
            if other_id not in conversations:
                other_user = User.query.get(other_id)
                if other_user:
                    conversations[other_id] = {
                        'id': other_id, # 对方的ID
                        'name': other_user.username,
                        'avatar': other_user.avatar,
                        'last_msg': m.content,
                        'time': m.created_at.strftime('%m-%d %H:%M'),
                        'unread': 0 # 这里先简化，以后做未读红点
                    }
        
        # 转成列表返回
        return jsonify({'success': True, 'data': list(conversations.values())})
        
    except Exception as e:
        print(f"获取消息失败: {e}")
        return jsonify({'success': False, 'data': []})

# ==========================================
# 新增：获取未读消息总数 (用于 TabBar 红点)
# ==========================================
@app.route('/api/v1/messages/unread_count', methods=['GET'])
def get_unread_count():
    uid = request.args.get('userId')
    if not uid: return jsonify({'success': False, 'count': 0})
    
    # 统计：收件人是我，且 is_read 为 False 的所有消息
    count = Message.query.filter_by(receiver_id=uid, is_read=False).count()
    return jsonify({'success': True, 'count': count})

# ==========================================
# 新增：标记消息为已读 (进入聊天时调用)
# ==========================================
@app.route('/api/v1/messages/read', methods=['POST'])
def mark_messages_read():
    data = request.json
    uid = data.get('userId')
    friend_id = data.get('friendId')
    
    # 找到所有“他发给我的”且“未读”的消息，全部改成已读
    msgs = Message.query.filter_by(sender_id=friend_id, receiver_id=uid, is_read=False).all()
    for m in msgs:
        m.is_read = True
    db.session.commit()
    return jsonify({'success': True})

# ==========================================
# 新增：创建订单 (模拟支付)
# ==========================================
# 修复版：把 '已支付' 改为 '已付款'
@app.route('/api/v1/orders/create', methods=['POST'])
def create_trade_order():
    try:
        data = request.json
        item_id = data.get('item_id')
        buyer_id = data.get('buyer_id')
        address = data.get('address', '校内宿舍')

        # 1. 检查商品
        item = Item.query.get(item_id)
        if not item: 
            return jsonify({'success': False, 'message': '商品不存在'})
        
        if item.status == '已售出': 
            return jsonify({'success': False, 'message': '手慢了，商品已被抢走！'})
        
        # 强制转成数字
        buyer_id = int(buyer_id)
        if int(item.seller_id) == buyer_id:
            return jsonify({'success': False, 'message': '不能买自己的东西哦'})

        # 2. 生成订单
        import uuid
        order_no = f"ORD_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        
        new_order = Order(
            order_no=order_no,
            item_id=item_id,
            buyer_id=buyer_id,
            seller_id=item.seller_id,
            final_price=item.current_price,
            
            # ⭐⭐⭐ 核心修复：改成数据库认识的 '已付款' ⭐⭐⭐
            status='已付款', 
            
            buyer_phone='-',
            seller_phone='-',
            shipping_address=address
        )
        
        # 3. 标记商品为已售出
        item.status = '已售出'
        
        db.session.add(new_order)
        db.session.commit()
        
        print(f"✅ 订单创建成功！买家ID: {buyer_id}, 状态: 已付款")
        return jsonify({'success': True, 'order_id': new_order.id})
        
    except Exception as e:
        print("下单失败:", e)
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
# ==========================================
# 新增：删除留言 (适配你的字段名)
# ==========================================
@app.route('/api/v1/reviews/delete', methods=['POST'])
def delete_review():
    try:
        data = request.json
        review_id = data.get('review_id')
        operator_id = data.get('user_id') # 发起删除请求的人的ID

        review = Review.query.get(review_id)
        if not review:
            return jsonify({'success': False, 'message': '留言不存在'})

        # 获取商品信息（为了判断是不是卖家）
        item = Item.query.get(review.item_id)
        
        # 权限检查：
        # 1. 是留言作者本人 (用 reviewer_id)
        # 2. 或者是该商品的卖家
        is_author = str(review.reviewer_id) == str(operator_id)
        is_seller = item and str(item.seller_id) == str(operator_id)

        if is_author or is_seller:
            db.session.delete(review)
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '你没权限删除这条留言'})

    except Exception as e:
        print("删除报错:", e)
        return jsonify({'success': False, 'message': '删除出错'})
# ==========================================
# 🤖 议价智能体模块 (Bargain Agent)
# ==========================================

# 检查买家是否有进行中的议价
@app.route('/api/v1/bargain/check', methods=['POST'])
def check_bargain_status():
    try:
        data = request.json
        item_id = data.get('item_id')
        buyer_id = data.get('buyer_id')
        
        # 查找是否有进行中的议价（待回复或还价状态）
        active_bargain = BargainLog.query.filter(
            BargainLog.item_id == item_id,
            BargainLog.buyer_id == buyer_id,
            BargainLog.seller_response.in_(['待回复', '还价'])
        ).first()
        
        print(f"检查议价状态: item_id={item_id}, buyer_id={buyer_id}, 有进行中的议价={active_bargain is not None}")
        if active_bargain:
            print(f"  -> 议价记录: ID={active_bargain.id}, 价格={active_bargain.offered_price}, 状态={active_bargain.seller_response}")
        
        return jsonify({
            'success': True,
            'has_active_bargain': active_bargain is not None,
            'bargain': {
                'id': active_bargain.id,
                'offered_price': active_bargain.offered_price,
                'seller_response': active_bargain.seller_response,
                'created_at': active_bargain.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } if active_bargain else None
        })
    except Exception as e:
        print("检查议价状态出错:", e)
        return jsonify({'success': False, 'message': '检查失败'})

# 1. 买家发起砍价
@app.route('/api/v1/bargain/offer', methods=['POST'])
def make_bargain_offer():
    try:
        data = request.json
        item_id = data.get('item_id')
        buyer_id = data.get('buyer_id')
        # 兼容两种参数名
        price = data.get('price') or data.get('offered_price') # 买家出的价
        
        if not price:
            return jsonify({'success': False, 'message': '价格参数缺失'})
        
        item = Item.query.get(item_id)
        if not item: return jsonify({'success': False, 'message': '商品不存在'})
        if str(item.seller_id) == str(buyer_id): return jsonify({'success': False, 'message': '不能砍自己的价'})
        
        # 记录议价日志
        log = BargainLog(
            item_id=item_id,
            buyer_id=buyer_id,
            offered_price=price,
            seller_response='待回复'
        )
        db.session.add(log)
        
        # 🤖 智能体动作：给卖家发通知
        msg = Message(
            sender_id=buyer_id,
            receiver_id=item.seller_id,
            item_id=item_id,
            content=f"【议价申请】买家出价 ¥{price} (原价 ¥{item.current_price})，请在详情页或消息列表处理。",
            msg_type='议价通知' # 特殊类型，前端可以识别并显示“同意/拒绝”按钮
        )
        db.session.add(msg)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '砍价申请已发送，等待卖家处理'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': '出价失败'})

# 2. 卖家处理砍价 (核心功能：同意即改价)
@app.route('/api/v1/bargain/handle', methods=['POST'])
def handle_bargain():
    try:
        data = request.json
        log_id = data.get('log_id') # 议价记录ID (如果前端没存，也可以传 item_id 和 buyer_id 查最近一条)
        # 这里为了简化，我们假设前端通过消息直接操作，或者我们根据 item_id 和 buyer_id 找最近的记录
        item_id = data.get('item_id')
        buyer_id = data.get('buyer_id')
        action = data.get('action') # 'accept' (同意)、'reject' (拒绝) 或 'counter' (还价)
        counter_price = data.get('counter_price') # 卖家还价的价格
        
        # 找最近的一条待回复或还价的记录
        log = BargainLog.query.filter(
            BargainLog.item_id == item_id,
            BargainLog.buyer_id == buyer_id,
            BargainLog.seller_response.in_(['待回复', '还价'])
        ).order_by(BargainLog.created_at.desc()).first()
            
        if not log:
            return jsonify({'success': False, 'message': '找不到有效的议价记录'})

        # 调试：打印找到的记录信息
        print(f"找到的议价记录: ID={log.id}, 价格={log.offered_price}, 状态={log.seller_response}, 创建时间={log.created_at}")

        item = Item.query.get(item_id)

        if action == 'accept':
            # ✅ 接受议价（买家或卖家都可能接受）
            log.seller_response = '接受'
            log.responded_at = datetime.now()
            
            print(f"更新议价记录状态为'接受': ID={log.id}")
            
            # 🤖 智能体核心动作：自动改价！
            old_price = item.current_price
            item.current_price = log.offered_price # 改成议价的价格
            
            print(f"商品价格已更新: {old_price} -> {item.current_price}")
            
            # 通知买家
            reply_msg = Message(
                sender_id=item.seller_id,
                receiver_id=buyer_id,
                item_id=item_id,
                content=f"【议价成功】卖家接受了您的出价！价格已从 ¥{old_price} 调整为 ¥{item.current_price}，快去支付吧！",
                msg_type='系统'
            )
            db.session.add(reply_msg)
            
        elif action == 'counter':
            # 🔄 卖家还价
            log.seller_response = '还价'
            log.responded_at = datetime.now()
            
            # 创建新的议价记录，角色互换（现在是卖家出价给买家）
            counter_log = BargainLog(
                item_id=item_id,
                buyer_id=buyer_id,
                offered_price=counter_price,
                seller_response='还价'
            )
            db.session.add(counter_log)
            
            # 通知买家
            reply_msg = Message(
                sender_id=item.seller_id,
                receiver_id=buyer_id,
                item_id=item_id,
                content=f"【卖家还价】卖家还价 ¥{counter_price}，您可以继续议价或接受。",
                msg_type='议价通知'
            )
            db.session.add(reply_msg)
            
        elif action == 'reject':
            # ❌ 卖家拒绝
            log.seller_response = '拒绝'
            log.responded_at = datetime.now()
            
            # 通知买家
            reply_msg = Message(
                sender_id=item.seller_id,
                receiver_id=buyer_id,
                item_id=item_id,
                content=f"【议价失败】卖家觉得 ¥{log.offered_price} 太低了，拒绝了您的申请。",
                msg_type='系统'
            )
            db.session.add(reply_msg)
            
        db.session.commit()
        return jsonify({'success': True, 'message': '处理成功'})

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': str(e)})   
# ==========================================
# 🧠 真实 AI 智能模块 (GLM-4V)
# ==========================================
@app.route('/api/v1/ai/generate', methods=['POST'])
def ai_generate():
    try:
        data = request.json
        image_data = data.get('image') # 前端传来的 Base64 图片
        
        if not image_data:
            return jsonify({'success': False, 'message': '请先上传图片'})

        # ⭐⭐⭐ 请在这里填入你刚才申请的 API Key ⭐⭐⭐
        api_key = "d3894857d1e0413e9cdca7f149488fe2.dF2En4CZtmHyDieb" 
        
        client = ZhipuAI(api_key=api_key) 

        print("🤖 AI 正在观察图片...")
        
        # 调用视觉大模型
        response = client.chat.completions.create(
            model="glm-4v-flash",  # 使用视觉模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "你是一个二手交易平台的智能助手。请识别这张图片中的物品，并帮我生成发布信息。\n请直接返回一个纯 JSON 格式的数据（不要包含 ```json 等标记），必须包含以下 4 个字段：\n1. title: 简短吸引人的标题(15字内)\n2. desc: 详细的转手文案(包含成色、使用体验，50字左右)\n3. price: 预估二手价格(纯数字，不要带单位)\n4. category: 只能从['电子数码', '书籍资料', '生活用品', '服饰鞋包', '美妆护肤', '运动器材', '乐器文玩', '代步工具', '虚拟商品', '其他'] 中选一个最匹配的。\n"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data # 直接把前端传的 data:image... 塞进去
                            }
                        }
                    ]
                }
            ]
        )
        
        # 获取 AI 的回答
        content = response.choices[0].message.content
        print("🤖 AI 回复内容:", content)
        
        # 🧹 清洗数据：有时候 AI 会好心加 ```json ... ```，我们要把它去掉
        content = content.replace("```json", "").replace("```", "").strip()
        
        # 转成 Python 字典
        ai_result = json.loads(content)
        
        return jsonify({'success': True, 'data': ai_result})

    except Exception as e:
        print(f"❌ AI 调用失败: {e}")
        return jsonify({'success': False, 'message': 'AI 看走眼了，请重试'}) 
# run_server.py 新增接口

@app.route('/api/v1/items/status', methods=['POST'])
def update_item_status():
    try:
        data = request.json
        item_id = data.get('item_id')
        new_status = data.get('status') # '上架' 或 '下架'
        
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'success': False, 'message': '商品不存在'})
            
        # 修改状态
        item.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'已{new_status}'})
    except Exception as e:
        print(f"修改状态失败: {e}")
        return jsonify({'success': False, 'message': '操作失败'})

# ==========================================
# 智能体API路由
# ==========================================
@app.route('/api/agent/buyer-advice', methods=['POST'])
@app.route('/api/v1/buyer/advice', methods=['POST'])
def get_buyer_advice():
    """获取买家砍价建议"""
    try:
        data = request.json
        if not data:
            return jsonify({'code': 400, 'message': '缺少请求数据'})
        
        # 调用智能体服务（本地5011端口）
        agent_url = "http://127.0.0.1:5011/api/agent/buyer/advice"
        
        response = requests.post(agent_url, json=data, timeout=5)
        
        if response.status_code == 200:
            agent_response = response.json()
            print(f"智能体返回: {agent_response}")  # 调试信息
            if agent_response.get('success'):
                return jsonify({
                    'code': 200,
                    'message': '获取建议成功',
                    'data': agent_response.get('data', {}),
                    'meta': agent_response.get('meta', {})
                })
            else:
                # 返回智能体的错误信息
                return jsonify({
                    'code': 500,
                    'message': agent_response.get('message', '智能体服务返回异常'),
                    'error': str(agent_response)
                })
        
        return jsonify({
            'code': 500,
            'message': f'智能体服务HTTP错误: {response.status_code}'
        })
        
    except requests.RequestException as e:
        print(f"智能体服务调用失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'智能体服务连接失败: {str(e)}'
        })
    except Exception as e:
        print(f"获取买家建议失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取建议失败',
            'error': str(e)
        })

@app.route('/api/agent/seller-advice', methods=['POST'])
@app.route('/api/v1/seller/response', methods=['POST'])
def get_seller_advice():
    """获取卖家回应建议"""
    try:
        data = request.json
        if not data:
            return jsonify({'code': 400, 'message': '缺少请求数据'})
        
        # 调用智能体服务
        agent_url = "http://127.0.0.1:5011/api/agent/seller/response"
        
        response = requests.post(agent_url, json=data, timeout=5)
        
        if response.status_code == 200:
            agent_response = response.json()
            if agent_response.get('success'):
                return jsonify({
                    'code': 200,
                    'message': '获取建议成功',
                    'data': agent_response.get('data', {}),
                    'meta': agent_response.get('meta', {})
                })
        
        return jsonify({
            'code': 500,
            'message': '智能体服务返回异常'
        })
        
    except requests.RequestException as e:
        print(f"智能体服务调用失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'智能体服务连接失败: {str(e)}'
        })
    except Exception as e:
        print(f"获取卖家建议失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取建议失败',
            'error': str(e)
        })
        
# ==========================================
# 启动部分 (带异常捕获和暂停)
# ==========================================
if __name__ == '__main__':
    try:
        print("🚀 正在启动服务器...")
        
        # 延迟 1.5 秒再打开浏览器
        def open_browser():
            time.sleep(1.5)
            # 使用默认浏览器打开，不强制 open_new，兼容性更好
            webbrowser.open('http://127.0.0.1:5001')

        import threading
        threading.Thread(target=open_browser).start()

        # 启动 SocketIO
        socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)

    except Exception as e:
        # 🛑 关键：如果报错，把错误打印出来，并且暂停住，不让窗口关闭！
        import traceback
        traceback.print_exc()
        print("\n❌ 严重错误！程序即将退出...")
        input("按任意键退出...")  # 👈 这句会让黑框框停住！