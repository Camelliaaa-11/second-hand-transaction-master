from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, User, Item, Order, Message, Category, BargainLog, Favorite, Review, BrowseHistory
from datetime import datetime
import os
import time
import requests

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True,  # 如果使用 HTTPS
    SESSION_COOKIE_HTTPONLY=True,
)
AGENT_API_URL = "http://192.168.31.180:5011"  # 智能体服务的端口
AGENT_BUYER_ADVICE_URL = f"{AGENT_API_URL}/api/v1/advice/buyer"
AGENT_SELLER_ADVICE_URL = f"{AGENT_API_URL}/api/v1/advice/seller"
AGENT_TIMEOUT = 3  # 超时时间（秒）

# ==================== 数据库配置 ====================
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:123456@localhost:3306/softapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭修改追踪，提高性能
app.config['SQLALCHEMY_ECHO'] = True  # 开发时显示SQL语句

# ==================================================
# 文件上传配置
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# 创建上传文件夹
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'items'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
# 允许跨域
CORS(app, 
     resources={r"/api/*": {"origins": "*"}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"]
)
# 初始化数据库
db.init_app(app)
# 创建数据库表（如果不存在）
with app.app_context():
    db.create_all()
    print("数据库表已创建/更新")
# 初始化SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    manage_session=False  # 重要：让Flask管理会话
)
# 在线用户字典
online_users = {}

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
# 安全上传文件
# ==================== REST API 接口 ====================
# ---------- 用户相关 ----------
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.form
    if not data or 'username' not in data or not data['username']:
        return jsonify({'code': 400, 'message': '用户名不能为空'})
    if 'password' not in data or not data['password']:
        return jsonify({'code': 400, 'message': '密码不能为空'})
    if 'phone' not in data or not data['phone']:
        return jsonify({'code': 400, 'message': '手机号不能为空'})
    # 检查用户名，密码，手机号是否已存在
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'code': 400, 'message': '手机号已被使用'})
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'message': '用户名已存在'})
    # 处理头像上传
    avatar_url = None
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        avatar_url = save_uploaded_file(avatar_file, 'avatars')
    user = User(
        username=data['username'],
        password_hash=data['password'], 
        phone=data['phone'],
        credit_score=80
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {'user_id': user.id, 'username': user.username}
    })

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'})
    user = User.query.filter_by(username=data['username']).first()
    # 简化密码验证
    if not user or user.password_hash != data['password']:
        return jsonify({'code': 401, 'message': '用户名或密码错误'})
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'phone': user.phone,
            'credit_score': user.credit_score
        }
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'code': 200, 'message': '登出成功'})

# ---------- 商品相关 ----------
@app.route('/api/items', methods=['GET'])
def get_items():
    """获取商品列表"""
    page = int(request.args.get('page', 1))# 页码，默认在第一页
    page_size = int(request.args.get('page_size', 20))# 每页数量
    query = Item.query.filter_by(status='上架')# 只含“上架”状态的商品
    category = request.args.get('category')
    if category:# 分类搜索
        query = query.filter_by(category_id=category)
    keyword = request.args.get('keyword')
    if keyword:# 关键词搜索
        query = query.filter(Item.title.like(f'%{keyword}%'))
    # 总页数
    total = query.count()
    items = query.order_by(Item.created_at.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()
    item_list = []
    for item in items: # 商品响应结构
        cover_image = '' # 初始图片为空
        if item.description and '图片链接：' in item.description:
            # 提取描述中的图片链接
            desc = item.description
            start = desc.find('图片链接：') + 5
            end = desc.find('\n', start)
            if end == -1:
                end = len(desc)
            images_str = desc[start:end]
            images = [img.strip() for img in images_str.split(',')]
            if images:
                cover_image = images[0]# 用第一张做封面
        item_list.append({
            'id': item.id,
            'title': item.title,
            'price': float(item.current_price),
            'category': item.category_ref.name if item.category_ref else '其他',
            'condition': item.quality,
            'cover_image': cover_image,  # 可根据实际需要添加图片字段
            'seller': {
                'id': item.seller.id,
                'username': item.seller.username,
                'credit_score': item.seller.credit_score
            },
            'view_count': item.view_count,
            'favorite_count': item.favorite_count,
            'is_urgent_sale': item.is_urgent_sale,
            'bargain_enabled': item.bargain_enabled,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify({# 响应结构
        'code': 200,
        'data': {
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': item_list # 商品列表数组
        }
    })

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    """获取商品详情"""
    item = Item.query.get_or_404(item_id)
    # 增加浏览次数
    item.view_count += 1
    # 记录浏览历史
    if 'user_id' in session:# 登陆后
        history = BrowseHistory.query.filter_by(
            user_id=session['user_id'],
            item_id=item_id
        ).first()# 查看是否有浏览记录
        if history:
            history.browse_count += 1
            history.last_browsed_at = datetime.now()# 更新浏览时间
        else:
            history = BrowseHistory(
                user_id=session['user_id'],
                item_id=item_id,
                browse_count=1# 第一次浏览
            )
            db.session.add(history)
    db.session.commit()
    return jsonify({
        'code': 200,
        'data': {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'price': float(item.current_price),
            'original_price': float(item.price),
            'category': item.category_ref.name if item.category_ref else '其他',
            'condition': item.quality,
            'status': item.status,
            'seller': {
                'id': item.seller.id,
                'username': item.seller.username,
                'credit_score': item.seller.credit_score,
                'phone': item.seller.phone
            },
            'contact_phone': item.contact_phone,
            'is_urgent_sale': item.is_urgent_sale,
            'bargain_enabled': item.bargain_enabled,
            'min_price': float(item.min_price) if item.min_price else None,
            'is_new': item.is_new,
            'view_count': item.view_count,
            'favorite_count': item.favorite_count,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

@app.route('/api/items', methods=['POST'])
def create_item():
    """发布商品（支持图片上传）"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    # 处理表单数据
    title = request.form.get('title')
    price = request.form.get('price')
    category_id = request.form.get('category_id') #分类也是必要的
    if not title or not price or not category_id:
        return jsonify({'code': 400, 'message': '标题,价格和分类不能为空'})
    # 验证分类是否存在
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'code': 400, 'message': '请从一下类别中选择:电子产品、书籍资料、衣物服饰、生活用品、运动器材、其他物品。'})
    # 处理图片上传
    image_urls = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file.filename:  # 确保文件不为空
                image_url = save_uploaded_file(file, 'items')
                if image_url:
                    image_urls.append(image_url)
    item = Item(
        title=title,
        description=request.form.get('description', ''),
        price=float(price),
        current_price=float(price),
        category_id=category_id,
        quality=request.form.get('quality', '九成新'),
        status='上架',
        seller_id=session['user_id'],
        contact_phone=request.form.get('contact_phone', ''),
        is_urgent_sale=request.form.get('is_urgent_sale', 'false').lower() == 'true',
        bargain_enabled=request.form.get('bargain_enabled', 'true').lower() == 'true',
        min_price=float(request.form['min_price']) if 'min_price' in request.form and request.form['min_price'] else None,
        is_new=request.form.get('is_new', 'true').lower() == 'true'
    )
    # 保存图片URL（可以存储在description或其他字段中）
    if image_urls:
        item.description = f"{item.description}\n\n图片链接：{', '.join(image_urls)}"
    db.session.add(item)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '商品发布成功',
        'data': {'item_id': item.id, 'images': image_urls}
    })

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """单独图片上传接口"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有文件'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '未选择文件'})
    image_url = save_uploaded_file(file, 'items')
    if image_url:
        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {'url': image_url}
        })
    else:return jsonify({'code': 400, 'message': '文件类型不允许'})

# ---------- 评价相关 ----------
@app.route('/api/reviews', methods=['POST'])
def create_review():
    """创建评价"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'order_id' not in data or 'rating' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})
    order = Order.query.get(data['order_id'])
    if not order:
        return jsonify({'code': 400, 'message': '订单不存在'})
    # 检查用户是否有评价权限
    reviewer_id = session['user_id']
    if reviewer_id != order.buyer_id and reviewer_id != order.seller_id:
        return jsonify({'code': 403, 'message': '无权评价此订单'})
    # 检查是否已经评价过
    existing_review = Review.query.filter_by(
        order_id=data['order_id'],
        reviewer_id=reviewer_id
    ).first()
    if existing_review:
        return jsonify({'code': 400, 'message': '已经评价过此订单'})
    
    # 确定评价类型和被评价者
    if reviewer_id == order.buyer_id:
        review_type = '买家评价卖家'
        reviewed_id = order.seller_id
    else:
        review_type = '卖家评价买家'
        reviewed_id = order.buyer_id
    review = Review(
        order_id=data['order_id'], # 订单id
        reviewer_id=reviewer_id, # 评价者id
        reviewed_id=reviewed_id, # 被评价者id
        rating=str(data['rating']),  # 转换为字符串以匹配Enum
        content=data.get('content', ''), # 评价内容
        type=review_type, # 评价类型
        is_anonymous=data.get('is_anonymous', False) # 是否匿名
    )
    db.session.add(review)
    # 更新被评价者的信用分
    reviewed_user = User.query.get(reviewed_id)
    if reviewed_user:
        # 简单信用分计算：根据评分调整
        rating_value = int(data['rating'])
        if rating_value >= 4:
            reviewed_user.credit_score = min(100, reviewed_user.credit_score + 2)
        elif rating_value <= 2:
            reviewed_user.credit_score = max(0, reviewed_user.credit_score - 3)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '评价成功',
        'data': {'review_id': review.id}
    })

#这部分在哪里体现?
@app.route('/api/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """获取用户的评价"""
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    # 获取所有user_id作为被评价者的评价
    reviews_query = Review.query.filter_by(reviewed_id=user_id)
    total = reviews_query.count()
    reviews = reviews_query.order_by(Review.created_at.desc()) \
                          .offset((page - 1) * page_size) \
                          .limit(page_size) \
                          .all()
    # 时间最新的排在最前面，计算偏移量，限制每页数量，执行查询
    review_list = []
    for review in reviews:
        review_list.append({
            'id': review.id,
            'order_id': review.order_id,
            'reviewer': {
                'id': review.reviewer.id,
                'username': review.reviewer.username if not review.is_anonymous else '匿名用户'
            },# 匿名不显示名字
            'rating': int(review.rating),
            'content': review.content,
            'type': review.type,
            'is_anonymous': review.is_anonymous,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M')
        })
    # 计算平均评分
    avg_rating = db.session.query(db.func.avg(db.cast(Review.rating, db.Integer)))\
                          .filter_by(reviewed_id=user_id)\
                          .scalar() or 0
    # 评分转为整数后，计算平均值。没有评价返回0
    return jsonify({
        'code': 200,
        'data': {
            'user_id': user_id,
            'average_rating': round(float(avg_rating), 1),
            'total_reviews': total,
            'page': page,
            'page_size': page_size,
            'reviews': review_list
        }
    })

# ---------- 议价相关 ----------
@app.route('/api/bargain', methods=['POST'])
def create_bargain():
    """发起议价"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'item_id' not in data or 'offered_price' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})
    # 商品ID，出价，验证这些完整参数
    item = Item.query.get(data['item_id'])
    if not item or item.status != '上架':
        return jsonify({'code': 400, 'message': '商品不可用'})
    if item.seller_id == session['user_id']:
        return jsonify({'code': 400, 'message': '不能对自己的商品议价'})
    if not item.bargain_enabled:
        return jsonify({'code': 400, 'message': '该商品不支持议价'})
    # 商品状态验证(上架，可议价，不是自己的商品)
    bargain = BargainLog(
        item_id=item.id,
        buyer_id=session['user_id'],
        offered_price=float(data['offered_price']),
        message=data.get('message', ''),
        buyer_contact=data.get('buyer_contact', ''),# 联系电话
        seller_response='待回复'
    )
    # 更新商品状态
    item.status = '议价中'
    db.session.add(bargain) # 添加议价记录
    db.session.commit() # 提交到数据库

    # 实时通知卖家
    seller_socket_id = online_users.get(item.seller_id) #在线判断
    if seller_socket_id: # 只有卖家在线时才发送，避免错误
        socketio.emit('new_bargain', {
            'bargain_id': bargain.id,
            'buyer_name': session['username'],
            'item_title': item.title,
            'item_price': float(item.price),  # 商品原价
            'offered_price': float(data['offered_price']),
            'message': data.get('message', ''),  # 买家留言
            'buyer_contact': data.get('buyer_contact', ''),  # 买家联系方式
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, room=seller_socket_id) # 只推送给卖家，不会广播给其他人
    return jsonify({
        'code': 200,
        'message': '议价请求已发送',
        'data': {'bargain_id': bargain.id,
                 'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
    })

@app.route('/api/bargain/<int:bargain_id>/response', methods=['PUT'])
def respond_to_bargain(bargain_id):
    """卖家回应议价请求"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'response' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})
    bargain = BargainLog.query.get_or_404(bargain_id)
    item = Item.query.get(bargain.item_id)

    # 检查权限
    if item.seller_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    response_type = data['response']  # '接受', '拒绝', '还价'
    if response_type not in ['接受', '拒绝', '还价']:
        return jsonify({'code': 400, 'message': '无效的回应类型'})
    
    if response_type == '接受':
        checkout_data = {
            'checkout_id': f'BARGAIN_CHECKOUT_{bargain.id}',
            'type': 'bargain',  # 类型：议价
            'bargain_id': bargain.id,
            'item_id': item.id,
            'final_price': float(bargain.offered_price),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        # 存储到session或数据库
        session['pending_checkout'] = checkout_data
        # 商品状态变为"议价成功待结算"
        item.status = '议价成功待结算'
        # 通知买家去结算
        if buyer_socket_id:
            socketio.emit('bargain_accepted', {
                'bargain_id': bargain.id,
                'checkout_id': checkout_data['checkout_id'],
                'item_title': item.title,
                'final_price': bargain.offered_price,
                'message': '议价成功，请前往结算页面完成订单'
            }, room=buyer_socket_id)
        
        return jsonify({
            'code': 200,
            'message': '已接受议价，等待买家结算',
            'data': {
                'bargain_id': bargain.id,
                'checkout_id': checkout_data['checkout_id'],
                'requires_checkout': True  # 前端需要引导到结算页
            }
        })
    # 对于"拒绝"和"还价"的情况
    else:
        if response_type == '拒绝':
            item.status = '上架'
        elif response_type == '还价':
            if 'counter_price' not in data:
                return jsonify({'code': 400, 'message': '还价需要提供价格'})
            bargain.seller_counter_price = float(data['counter_price'])
        # 更新议价记录
        bargain.seller_response = response_type
        bargain.responded_at = datetime.now()
        db.session.commit()
        # 通知买家
        buyer_socket_id = online_users.get(bargain.buyer_id)
        if buyer_socket_id:
            socketio.emit('bargain_response', {
                'bargain_id': bargain.id,
                'response': response_type,
                'counter_price': bargain.seller_counter_price if response_type == '还价' else None,
                'item_title': item.title
            }, room=buyer_socket_id)
        return jsonify({
            'code': 200,
            'message': f'已{response_type}议价请求',
            'data': {'bargain_id': bargain.id}
        })


# ---------- 订单相关 ----------
@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'item_id' not in data:
        return jsonify({'code': 400, 'message': '请选择商品'})
    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'code': 400, 'message': '商品不存在'})
    
    # 允许上架和议价中的商品被购买
    if item.status not in ['上架', '议价中']:
        return jsonify({'code': 400, 'message': f'商品状态为{item.status}，不可购买'})
    if item.seller_id == session['user_id']:
        return jsonify({'code': 400, 'message': '不能购买自己的商品'})
    
    # 检查是否有未完成的议价
    pending_bargain = BargainLog.query.filter_by(
        item_id=item.id,
        buyer_id=session['user_id'],
        seller_response='待回复'
    ).first()
    
    # 获取买家电话
    buyer_phone = data.get('buyer_phone', '')
    if not buyer_phone:
        # 从用户信息中获取手机号
        user = User.query.get(session['user_id'])
        if user and user.phone:
            buyer_phone = user.phone
        else:
            return jsonify({'code': 400, 'message': '请提供联系电话或完善个人信息'})
    # 生成订单号
    order_no = f'ORD{int(time.time())}{session["user_id"]}'
    # 确定最终价格
    final_price = item.current_price
    if 'final_price' in data:
        final_price = float(data['final_price'])
    
    order = Order(
        order_no=order_no,
        item_id=item.id,
        buyer_id=session['user_id'],
        seller_id=item.seller_id,
        final_price=final_price,
        status='待付款',
        buyer_phone=buyer_phone,  # 确保提供买家电话
        seller_phone=item.seller.phone,  # 确保提供卖家电话
        buyer_note=data.get('buyer_note', ''),
        shipping_address=data.get('shipping_address', ''),
        contact_phone=data.get('contact_phone', buyer_phone)  # 默认使用买家电话
    )
    # 标记商品为已售出
    item.status = '已售出'
    # 如果有议价记录，更新状态
    if pending_bargain:
        pending_bargain.seller_response = '接受'
        pending_bargain.responded_at = datetime.now()
    db.session.add(order)
    db.session.commit()
    # 自动发送一条消息
    message = Message(
        sender_id=session['user_id'],
        receiver_id=item.seller_id,
        order_id=order.id,
        content=f'我想购买您的《{item.title}》，订单号：{order_no}，请确认。',
        msg_type='系统'
    )
    db.session.add(message)
    db.session.commit()
    
    # 通知卖家
    seller_socket_id = online_users.get(item.seller_id)
    if seller_socket_id:
        socketio.emit('new_order', {
            'order_id': order.id,
            'buyer_name': session['username'],
            'item_title': item.title,
            'order_no': order_no
        }, room=seller_socket_id)
    
    return jsonify({
        'code': 200,
        'message': '订单创建成功',
        'data': {
            'order_id': order.id,
            'order_no': order.order_no
        }
    })

@app.route('/api/orders/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    """支付订单"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    order = Order.query.get_or_404(order_id)
    # 检查权限
    if order.buyer_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    if order.status != '待付款':
        return jsonify({'code': 400, 'message': '订单状态不是待付款'})
    order.status = '已付款'
    order.paid_at = datetime.now()
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '支付成功',
        'data': {'order_id': order.id, 'status': '已付款'}
    })

@app.route('/api/orders/user', methods=['GET'])
def get_user_orders():
    """获取当前用户的所有订单"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    user_id = session['user_id']

    try:
        # 查询用户作为买家和卖家的订单
        orders = Order.query.filter(
            (Order.buyer_id == user_id) | (Order.seller_id == user_id)
        ).order_by(Order.created_at.desc()).all()
        order_list = []
        for order in orders:
            # 确定用户角色
            user_role = 'buyer' if order.buyer_id == user_id else 'seller'
            order_list.append({
                'id': order.id,
                'order_no': order.order_no,
                'item_title': order.item.title if order.item else '商品已删除',
                'final_price': float(order.final_price),
                'status': order.status,
                'seller_id': order.seller_id,
                'seller_name': order.seller_user.username if order.seller_user else '未知用户',
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M')
            })
        return jsonify({
            'code': 200,
            'data': {
                'orders': order_list
            }
        })
    except Exception as e:
        print(f"获取用户订单失败: {e}")
        return jsonify({'code': 500, 'message': '获取订单失败', 'error': str(e)})
# ---------- 获取订单详情 ----------
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """获取订单详情"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    order = Order.query.get_or_404(order_id)  # 这里使用主键id查询
    user_id = session['user_id']
    # 检查用户权限
    if order.buyer_id != user_id and order.seller_id != user_id:
        return jsonify({'code': 403, 'message': '无权查看此订单'})
    return jsonify({
        'code': 200,
        'data': {
            'id': order.id,  # 数据库主键ID
            'order_no': order.order_no,  # 业务订单编号
            'item': {
                'id': order.item_id,
                'title': order.item.title if order.item else '商品已删除',
                'description': order.item.description if order.item else '',
                'price': float(order.item.price) if order.item else 0,
            },
            'final_price': float(order.final_price),
            'status': order.status,
            'buyer': {
                'id': order.buyer_id,
                'username': order.buyer.username if order.buyer else '',
                'phone': order.buyer_phone
            },
            'seller': {
                'id': order.seller_id,
                'username': order.seller_user.username if order.seller_user else '',  # 修正为 seller_user
                'phone': order.seller_phone
            },
            'buyer_note': order.buyer_note,
            'seller_note': order.seller_note,
            'shipping_address': order.shipping_address,
            'contact_phone': order.contact_phone,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
        }
    })

# ---------- 更新订单状态 ----------
@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """更新订单状态（付款、发货、完成等）"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'status' not in data:
        return jsonify({'code': 400, 'message': '缺少状态参数'})
    order = Order.query.get_or_404(order_id)  # 使用主键id
    user_id = session['user_id']
    # 检查用户权限（只有买家和卖家可以更新）
    if order.buyer_id != user_id and order.seller_id != user_id:
        return jsonify({'code': 403, 'message': '无权更新此订单'})
    
    # 验证状态转换逻辑
    valid_statuses = ['待付款', '已付款', '已发货', '已完成', '已取消', '退款中']
    new_status = data['status']
    if new_status not in valid_statuses:
        return jsonify({'code': 400, 'message': '无效的状态'})
    # 简单的状态机验证
    status_flow = {
        '待付款': ['已付款', '已取消'],
        '已付款': ['已发货', '退款中'],
        '已发货': ['已完成', '退款中'],
        '已完成': [],  # 最终状态
        '已取消': [],   # 最终状态
        '退款中': ['已取消']
    }
    if new_status not in status_flow.get(order.status, []):
        return jsonify({'code': 400, 'message': f'不能从{order.status}变更为{new_status}'})
    # 更新订单状态
    old_status = order.status
    order.status = new_status
    # 记录特定时间
    if new_status == '已付款' and not order.paid_at:
        order.paid_at = datetime.now()
    elif new_status == '已发货' and not order.shipped_at:
        order.shipped_at = datetime.now()
    elif new_status == '已完成' and not order.completed_at:
        order.completed_at = datetime.now()
    db.session.commit()
    
    # 通知对方用户
    other_user_id = order.seller_id if user_id == order.buyer_id else order.buyer_id
    other_socket_id = online_users.get(other_user_id)
    if other_socket_id:
        socketio.emit('order_status_updated', {
            'order_id': order.id,
            'order_no': order.order_no,  # 同时发送订单编号
            'old_status': old_status,
            'new_status': new_status,
            'updated_by': session['username']
        }, room=other_socket_id)
    return jsonify({
        'code': 200,
        'message': '订单状态更新成功',
        'data': {
            'order_id': order.id,
            'order_no': order.order_no,
            'status': new_status
        }
    })

# ---------- 取消订单 ----------
@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单（只有待付款状态可以取消）"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    order = Order.query.get_or_404(order_id)  # 使用主键id
    user_id = session['user_id']
    # 检查用户权限
    if order.buyer_id != user_id and order.seller_id != user_id:
        return jsonify({'code': 403, 'message': '无权取消此订单'})
    # 只能取消特定状态的订单
    if order.status not in ['待付款']:
        return jsonify({'code': 400, 'message': f'{order.status}状态的订单不能取消'})
    # 更新订单状态
    order.status = '已取消'
    # 恢复商品状态为可售
    item = Item.query.get(order.item_id)
    if item:
        item.status = '上架'
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '订单已取消',
        'data': {
            'order_id': order.id,
            'order_no': order.order_no,
            'status': '已取消'
        }
    })

# ---------- 结算相关 ----------
@app.route('/api/checkout/prepare', methods=['POST'])
def prepare_checkout():
    """准备结算（生成结算信息）"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'items' not in data:
        return jsonify({'code': 400, 'message': '请选择结算商品'})
    user_id = session['user_id']
    items_data = data['items']  # 格式: [{"item_id": 1, "quantity": 1}, ...]
    # 验证商品并计算总价
    checkout_items = []
    total_price = 0
    shipping_fee = 5.00  # 运费，可配置
    for item_data in items_data:
        item_id = item_data.get('item_id')
        quantity = item_data.get('quantity', 1)
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'code': 400, 'message': f'商品ID {item_id} 不存在'})
        if item.status != '上架':
            return jsonify({'code': 400, 'message': f'商品《{item.title}》已下架或售出'})
        if item.seller_id == user_id:
            return jsonify({'code': 400, 'message': f'不能购买自己的商品《{item.title}》'})
        
        # 计算商品总价
        item_total = float(item.current_price) * quantity
        checkout_items.append({
            'item_id': item.id,
            'title': item.title,
            'price': float(item.current_price),
            'quantity': quantity,
            'item_total': item_total,
            'seller': {
                'id': item.seller.id,
                'username': item.seller.username
            }
        })
        total_price += item_total
    # 生成结算唯一标识
    checkout_id = f'CHECKOUT_{int(time.time())}_{user_id}'
    # 存储结算信息到session（实际项目中应该存到数据库）
    checkout_data = {
        'checkout_id': checkout_id,
        'items': checkout_items,
        'total_price': total_price,
        'shipping_fee': shipping_fee,
        'grand_total': total_price + shipping_fee,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    # 临时存储在session中（注意：session有大小限制）
    session['checkout_data'] = checkout_data
    return jsonify({
        'code': 200,
        'message': '结算信息准备完成',
        'data': checkout_data
    })

@app.route('/api/checkout/confirm', methods=['POST'])
def confirm_checkout():# 多个商品购买
    """确认结算并创建订单"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'checkout_id' not in data:
        return jsonify({'code': 400, 'message': '缺少结算信息'})
    # 验证结算信息
    checkout_data = session.get('checkout_data')
    if not checkout_data or checkout_data['checkout_id'] != data['checkout_id']:
        return jsonify({'code': 400, 'message': '结算信息无效或已过期'})
    user_id = session['user_id']
    shipping_address = data.get('shipping_address', '')
    contact_phone = data.get('contact_phone', '')
    buyer_note = data.get('buyer_note', '')
    if not shipping_address:
        return jsonify({'code': 400, 'message': '请填写收货地址'})
    if not contact_phone:
        # 尝试从用户信息获取
        user = User.query.get(user_id)
        if user and user.phone:
            contact_phone = user.phone
        else:
            return jsonify({'code': 400, 'message': '请填写联系电话'})
    # 按卖家分组创建订单
    orders_by_seller = {}
    for item in checkout_data['items']:
        seller_id = item['seller']['id']
        if seller_id not in orders_by_seller:
            orders_by_seller[seller_id] = {
                'seller_id': seller_id,
                'seller_username': item['seller']['username'],
                'items': [],
                'total_price': 0
            }
        orders_by_seller[seller_id]['items'].append(item)
        orders_by_seller[seller_id]['total_price'] += item['item_total']
    # 为每个卖家创建订单
    created_orders = []
    for seller_id, seller_data in orders_by_seller.items():
        # 生成订单号
        order_no = f'ORD{int(time.time())}{user_id}{seller_id}'
        # 计算这个卖家的订单总价（含运费分摊）
        seller_items_count = len(seller_data['items'])
        total_items_count = len(checkout_data['items'])
        seller_shipping_fee = (checkout_data['shipping_fee'] * seller_items_count / total_items_count) if total_items_count > 0 else 0
        order = Order(
            order_no=order_no,
            item_id=seller_data['items'][0]['item_id'],  # 暂时只存第一个商品，可扩展为多商品订单
            buyer_id=user_id,
            seller_id=seller_id,
            final_price=seller_data['total_price'] + seller_shipping_fee,
            status='待付款',
            buyer_phone=contact_phone,
            seller_phone='',  # 从卖家信息获取
            shipping_address=shipping_address,
            contact_phone=contact_phone,
            buyer_note=buyer_note
        )
        # 获取卖家电话
        seller = User.query.get(seller_id)
        if seller and seller.phone:
            order.seller_phone = seller.phone
        db.session.add(order)
        db.session.flush()  # 获取order.id
        # 标记商品为已售出
        for item_data in seller_data['items']:
            item = Item.query.get(item_data['item_id'])
            if item:
                item.status = '已售出'
        created_orders.append({
            'order_id': order.id,
            'order_no': order.order_no,
            'seller_username': seller_data['seller_username'],
            'total': float(seller_data['total_price'] + seller_shipping_fee),
            'items_count': seller_items_count
        })
    db.session.commit()
    # 清空结算信息
    session.pop('checkout_data', None)
    return jsonify({
        'code': 200,
        'message': f'成功创建{len(created_orders)}个订单',
        'data': {
            'orders': created_orders,
            'checkout_id': checkout_data['checkout_id']
        }
    })

@app.route('/api/checkout/<string:checkout_id>', methods=['GET'])
def get_checkout_status(checkout_id):
    """获取结算状态"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    checkout_data = session.get('checkout_data')
    if not checkout_data or checkout_data['checkout_id'] != checkout_id:
        return jsonify({'code': 404, 'message': '结算信息不存在或已过期'})
    return jsonify({
        'code': 200,
        'data': checkout_data
    })

@app.route('/api/orders/<int:order_id>/ship', methods=['POST'])
def ship_order(order_id):
    """发货"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    order = Order.query.get_or_404(order_id)
    # 检查权限
    if order.seller_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    if order.status != '已付款':
        return jsonify({'code': 400, 'message': '订单尚未付款'})

    order.status = '已发货'
    order.shipped_at = datetime.now()
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '发货成功',
        'data': {'order_id': order.id, 'status': '已发货'}
    })

@app.route('/api/orders/<int:order_id>/complete', methods=['POST'])
def complete_order(order_id):
    """确认收货"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    order = Order.query.get_or_404(order_id)
    
    # 检查权限
    if order.buyer_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    if order.status != '已发货':
        return jsonify({'code': 400, 'message': '订单尚未发货'})
    order.status = '已完成'
    order.completed_at = datetime.now()
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '确认收货成功',
        'data': {'order_id': order.id, 'status': '已完成'}
    })

# ---------- 消息相关 ----------
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取聊天记录"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    user_id = session['user_id']
    other_user_id = request.args.get('other_user_id', type=int)
    query = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
    )
    messages = query.order_by(Message.created_at).all()
    # 标记为已读
    for msg in messages:
        if msg.receiver_id == user_id and not msg.is_read:
            msg.is_read = True
            msg.read_at = datetime.now()
    db.session.commit()
    
    message_list = []
    for msg in messages:
        message_list.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'sender_name': msg.sender.username,
            'content': msg.content,
            'msg_type': msg.msg_type,
            'is_read': msg.is_read,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({
        'code': 200,
        'data': message_list
    })

@app.route('/api/chat/users', methods=['GET'])
def get_chat_users():
    """获取与当前用户有过聊天的所有用户"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    user_id = session['user_id']
    
    try:
        # 查询所有与当前用户有过消息往来的用户
        # 方法1：查询发送给当前用户的消息
        sender_ids = db.session.query(Message.sender_id).filter(
            Message.receiver_id == user_id
        ).distinct().all()
        # 方法2：查询当前用户发送的消息
        receiver_ids = db.session.query(Message.receiver_id).filter(
            Message.sender_id == user_id
        ).distinct().all()
        # 合并所有用户ID（排除自己）
        user_ids = set()
        for (sender_id,) in sender_ids:
            if sender_id != user_id:
                user_ids.add(sender_id)
        for (receiver_id,) in receiver_ids:
            if receiver_id != user_id:
                user_ids.add(receiver_id)
        # 获取用户信息
        users = []
        for uid in list(user_ids)[:20]:  # 最多20个
            user = User.query.get(uid)
            if user:
                # 获取最后一条消息
                last_msg = Message.query.filter(
                    ((Message.sender_id == user_id) & (Message.receiver_id == uid)) |
                    ((Message.sender_id == uid) & (Message.receiver_id == user_id))
                ).order_by(Message.created_at.desc()).first()
                # 获取未读消息数量
                unread_count = Message.query.filter_by(
                    sender_id=uid,
                    receiver_id=user_id,
                    is_read=False
                ).count()
                users.append({
                    'id': user.id,
                    'username': user.username,
                    'last_message': last_msg.content if last_msg else '',
                    'last_message_time': last_msg.created_at.strftime('%Y-%m-%d %H:%M') if last_msg else '',
                    'unread_count': unread_count
                })
        return jsonify({
            'code': 200,
            'data': users
        })
    except Exception as e:
        print(f"获取聊天用户失败: {e}")
        return jsonify({'code': 500, 'message': '获取聊天用户失败'})

@app.route('/api/messages/unread/<int:other_user_id>', methods=['GET'])
def get_unread_count(other_user_id):
    """获取与特定用户的未读消息数"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    count = Message.query.filter_by(
        sender_id=other_user_id,
        receiver_id=session['user_id'],
        is_read=False
    ).count()
    return jsonify({'code': 200, 'data': {'unread_count': count}})

@app.route('/api/messages/read/<int:message_id>', methods=['POST'])
def mark_as_read(message_id):
    """标记单条消息为已读"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'code': 404, 'message': '消息不存在'})
    if message.receiver_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    message.is_read = True
    message.read_at = datetime.now()
    db.session.commit()
    return jsonify({'code': 200, 'message': '已标记为已读'})

@app.route('/api/messages/read-all/<int:other_user_id>', methods=['POST'])
def mark_all_as_read(other_user_id):
    """标记与特定用户的所有消息为已读"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    messages = Message.query.filter_by(
        sender_id=other_user_id,
        receiver_id=session['user_id'],
        is_read=False
    ).all()
    for msg in messages:
        msg.is_read = True
        msg.read_at = datetime.now()
    db.session.commit()
    return jsonify({'code': 200, 'message': f'已标记{len(messages)}条消息为已读'})

# ---------- 收藏相关 -----------
@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'item_id' not in data:
        return jsonify({'code': 400, 'message': '缺少商品ID'})

    # 检查是否已收藏
    existing = Favorite.query.filter_by(
        user_id=session['user_id'],
        item_id=data['item_id']
    ).first()
    if existing:
        return jsonify({'code': 400, 'message': '已收藏过此商品'})
    favorite = Favorite(
        user_id=session['user_id'],
        item_id=data['item_id']
    )
    # 更新商品收藏数
    item = Item.query.get(data['item_id'])
    if item:
        item.favorite_count += 1
    db.session.add(favorite)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '收藏成功',
        'data': {'favorite_id': favorite.id}
    })

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户的收藏列表"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    favorites = Favorite.query.filter_by(user_id=session['user_id'])\
                              .order_by(Favorite.created_at.desc())\
                              .all()
    favorite_list = []
    for fav in favorites:
        item = fav.item
        favorite_list.append({
            'id': fav.id,
            'item': {
                'id': item.id,
                'title': item.title,
                'price': float(item.current_price),
                'status': item.status,
                'cover_image': '',  # 可根据需要添加
                'seller_username': item.seller.username
            },
            'created_at': fav.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify({
        'code': 200,
        'data': favorite_list
    })

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def remove_favorite(favorite_id):
    """取消收藏"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    favorite = Favorite.query.get_or_404(favorite_id)
    # 检查权限
    if favorite.user_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权操作'})
    # 更新商品收藏数
    if favorite.item:
        favorite.item.favorite_count = max(0, favorite.item.favorite_count - 1)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '已取消收藏'
    })

# ---------- 智能体相关 ----------
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告: requests 库未安装，智能体API调用将不可用")

@app.route('/api/agent/buyer-advice', methods=['POST'])
def get_buyer_advice():
    """获取买家砍价建议"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'item_id' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})

    user_id = session['user_id']
    item_id = data['item_id']
    try:
        # 获取商品信息
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'code': 400, 'message': '商品不存在'})
        # 获取买家用户信息
        buyer = User.query.get(user_id)
        # 构建智能体请求
        agent_request = {
            'user_id': user_id,
            'item_id': item_id,
            'item_listed_price': float(item.current_price),
            'buyer_max_budget': data.get('buyer_max_budget', float(item.current_price) * 0.8),
            'buyer_urgency': data.get('buyer_urgency', 3),
            'seller_id': item.seller_id,
            'item_category': item.category_ref.name if item.category_ref else '其他',
            'item_condition': item.quality or '九成新'
        }
        # 调用智能体API
        try:
            response = requests.post(
                AGENT_BUYER_ADVICE_URL,
                json=agent_request,
                timeout=AGENT_TIMEOUT
            )
            if response.status_code == 200:
                agent_response = response.json()
                if agent_response.get('success'):
                    return jsonify({
                        'code': 200,
                        'message': '获取建议成功',
                        'data': agent_response.get('data', {}),
                        'meta': agent_response.get('meta', {})
                    })
        except requests.RequestException as e:
            print(f"智能体服务调用失败: {e}")
        return jsonify({
            'code': 500,
            'message': '智能体服务返回异常'
        })
    except Exception as e:
        print(f"获取买家建议失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取建议失败',
            'error': str(e)
        })
    
@app.route('/api/agent/seller-advice', methods=['POST'])
def get_seller_advice():
    """获取卖家回应建议"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'item_id' not in data or 'buyer_offer' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})
    user_id = session['user_id']
    item_id = data['item_id']
    buyer_offer = float(data['buyer_offer'])
    try:
        # 获取商品信息
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'code': 400, 'message': '商品不存在'})
        # 检查权限（必须是卖家）
        if item.seller_id != user_id:
            return jsonify({'code': 403, 'message': '无权操作'})
        # 获取买家信息
        buyer_id = data.get('buyer_id')
        buyer = User.query.get(buyer_id) if buyer_id else None
        # 构建智能体请求
        agent_request = {
            'user_id': user_id,
            'item_id': item_id,
            'item_listed_price': float(item.current_price),
            'seller_min_price': float(item.min_price) if item.min_price else float(item.current_price) * 0.7,
            'buyer_offer': buyer_offer,
            'is_urgent_sale': item.is_urgent_sale,
            'buyer_id': buyer_id,
            'negotiation_round': data.get('negotiation_round', 0)
        }
        # 调用智能体API
        try:
            response = requests.post(
                AGENT_SELLER_ADVICE_URL,
                json=agent_request,
                timeout=AGENT_TIMEOUT
            )
            if response.status_code == 200:
                agent_response = response.json()
                if agent_response.get('success'):
                    return jsonify({
                        'code': 200,
                        'message': '获取建议成功',
                        'data': agent_response.get('data', {}),
                        'meta': agent_response.get('meta', {})
                    })
        except requests.RequestException as e:
            print(f"智能体服务调用失败: {e}")
        return jsonify({
            'code': 500,
            'message': '智能体服务返回异常'
        })
    except Exception as e:
        print(f"获取卖家建议失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取建议失败',
            'error': str(e)
        })
    
@app.route('/api/agent/chat-advice', methods=['POST'])
def get_chat_advice():
    """获取聊天中的智能建议"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    if not data or 'other_user_id' not in data or 'item_id' not in data:
        return jsonify({'code': 400, 'message': '缺少必要参数'})
    user_id = session['user_id']
    other_user_id = data['other_user_id']
    item_id = data['item_id']
    try:
        # 获取商品信息
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'code': 400, 'message': '商品不存在'})
        # 判断用户角色（买家还是卖家）
        user_role = 'buyer' if user_id != item.seller_id else 'seller'
        other_role = 'seller' if user_role == 'buyer' else 'buyer'
        # 获取最近的消息
        recent_message = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == user_id))
        ).order_by(Message.created_at.desc()).first()
        # 获取对方的报价（如果有）
        buyer_offer = None
        if recent_message and '¥' in recent_message.content:
            # 简单提取价格（实际应该更智能）
            import re
            matches = re.findall(r'¥(\d+(?:\.\d+)?)', recent_message.content)
            if matches:
                buyer_offer = float(matches[0])
        if user_role == 'buyer':
            # 买家获取建议
            advice_data = {
                'item_id': item_id,
                'buyer_max_budget': data.get('buyer_max_budget', float(item.current_price) * 0.8),
                'buyer_urgency': data.get('buyer_urgency', 3),
                'buyer_offer': buyer_offer
            }
            # 调用买家建议API（内部转发）
            from flask import session as flask_session
            with app.test_request_context():
                flask_session.update(session)
                response = get_buyer_advice_internal(advice_data, user_id)
        else:
            # 卖家获取建议
            advice_data = {
                'item_id': item_id,
                'buyer_offer': buyer_offer or float(item.current_price) * 0.8,
                'buyer_id': other_user_id if user_role == 'seller' else user_id
            }
            # 调用卖家建议API（内部转发）
            from flask import session as flask_session
            with app.test_request_context():
                flask_session.update(session)
                response = get_seller_advice_internal(advice_data, user_id)
        return response
    except Exception as e:
        print(f"获取聊天建议失败: {e}")
        return jsonify({
            'code': 500,
            'message': '获取建议失败',
            'error': str(e)
        })
    
def get_buyer_advice_internal(data, user_id):
    """内部调用买家建议（避免重复代码）"""
    # 这里可以复用 get_buyer_advice 的逻辑
    # 简化的内部调用
    item_id = data['item_id']
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'code': 400, 'message': '商品不存在'})
    # 生成简单建议
    listed_price = float(item.current_price)
    max_budget = data.get('buyer_max_budget', listed_price * 0.8)
    suggested_price = min(listed_price * 0.9, max_budget)
    
    return jsonify({
        'code': 200,
        'data': {
            'action': 'MAKE_OFFER',
            'price': suggested_price,
            'message': f'建议报价 {suggested_price:.2f} 元',
            'strategy': 'MODERATE',
            'reasoning': '基于当前价格和预算的建议'
        }
    })

def get_seller_advice_internal(data, user_id):
    """内部调用卖家建议（避免重复代码）"""
    # 简化的内部调用
    item_id = data['item_id']
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'code': 400, 'message': '商品不存在'})
    buyer_offer = data.get('buyer_offer', float(item.current_price) * 0.8)
    min_price = float(item.min_price) if item.min_price else float(item.current_price) * 0.7
    if buyer_offer >= min_price * 1.1:
        action = 'ACCEPT'
        price = buyer_offer
        message = f'可以接受 {buyer_offer:.2f} 元'
    else:
        action = 'COUNTER_OFFER'
        price = max(min_price, buyer_offer * 1.05)
        message = f'建议还价 {price:.2f} 元'
    return jsonify({
        'code': 200,
        'data': {
            'action': action,
            'price': price,
            'message': message,
            'reasoning': f'买家出价 {buyer_offer:.2f} 元'
        }
    })

# ==================== WebSocket 实时聊天 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print(f"客户端尝试连接: {request.sid}")
    # 允许所有连接，验证放在具体的消息处理中
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    for user_id, sid in list(online_users.items()):
        if sid == request.sid:
            del online_users[user_id]
            break

@socketio.on('join_chat')
def handle_join_chat(data):
    """加入聊天房间"""
    if 'user_id' not in session:
        return
    user_id = session['user_id']
    other_user_id = data.get('other_user_id')
    if not other_user_id:
        return
    room_id = f'chat_{min(user_id, other_user_id)}_{max(user_id, other_user_id)}'
    join_room(room_id)
    emit('joined_chat', {'room_id': room_id}, room=request.sid)
    # 加入同一个房间，消息广播该房间

@socketio.on('send_message')
def handle_send_message(data):
    """发送实时消息"""
    print(f"收到发送消息请求: {data}")
    # 检查会话
    if 'user_id' not in session:
        print("未登录用户尝试发送消息")
        return
    sender_id = session['user_id']
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    if not receiver_id or not content:
        print(f"无效的消息参数: receiver_id={receiver_id}, content={content}")
        return
    print(f"发送消息: {sender_id} -> {receiver_id}: {content}")
    
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        msg_type='文本'
    )
    db.session.add(message)
    db.session.commit()
    # 1. 先存数据库（保证不丢失）
    room_id = f'chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}'
    print(f"发送到房间: {room_id}")
    message_data = {
        'id': message.id,
        'sender_id': sender_id,
        'sender_name': session.get('username', '未知用户'),
        'receiver_id': receiver_id,
        'content': content,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    # 2. 再实时推送（保证及时性）
    emit('new_message', message_data, room=room_id)
    # 如果接收者不在线，记录日志
    if receiver_id not in online_users:
        print(f'用户 {receiver_id} 不在线，消息已存储')
    else:
        print(f'用户 {receiver_id} 在线，已发送实时消息')

@socketio.on('authenticate')
def handle_authenticate(data):
    """WebSocket认证"""
    user_id = data.get('user_id')
    if user_id:
        online_users[user_id] = request.sid
        print(f"用户 {user_id} 通过WebSocket认证，Socket ID: {request.sid}")
        emit('authenticated', {'user_id': user_id})
    else:
        print("WebSocket认证失败：缺少user_id")

# ==================== 其他接口 ====================

# ---------- 获取分类列表 ----------
@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有商品分类"""
    categories = Category.query.all() #从数据库获取
    category_list = [{'id': cat.id, 'name': cat.name} for cat in categories]
    return jsonify({'code': 200, 'data': category_list})

# ---------- 获取用户商品 ----------
@app.route('/api/items/user', methods=['GET'])
def get_user_items():
    """获取用户发布的商品"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    user_id = session['user_id']
    items = Item.query.filter_by(seller_id=user_id).order_by(Item.created_at.desc()).all()
    item_list = []
    for item in items:
        item_list.append({
            'id': item.id,
            'title': item.title,
            'price': float(item.current_price),
            'status': item.status,
            'view_count': item.view_count,
            'favorite_count': item.favorite_count,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify({'code': 200, 'data': item_list})

# ---------- 搜索用户 ----------
@app.route('/api/users/search', methods=['GET'])
def search_users():
    """搜索用户"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'code': 400, 'message': '请输入搜索关键词'})
    users = User.query.filter(
        User.username.like(f'%{keyword}%'),
        User.id != session['user_id']  # 排除自己
    ).limit(20).all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'credit_score': user.credit_score
        })
    
    return jsonify({'code': 200, 'data': user_list})

# ---------- 用户信息更新 ----------
@app.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """更新用户个人信息"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    data = request.json
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'})
    
    if 'phone' in data:
        # 检查手机号是否已被其他用户使用
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'code': 400, 'message': '手机号已被使用'})
        user.phone = data['phone']
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'phone': user.phone,
            'credit_score': user.credit_score
        }
    })

# ---------- 更新商品信息 ----------
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """更新商品信息"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    item = Item.query.get_or_404(item_id)
    # 检查权限
    if item.seller_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权修改'})
    
    data = request.form
    if 'title' in data:
        item.title = data['title']
    if 'description' in data:
        item.description = data['description']
    if 'price' in data:
        item.price = float(data['price'])
        if item.status == '上架':
            item.current_price = float(data['price'])
    if 'category_id' in data:
        item.category_id = data['category_id']
    if 'quality' in data:
        item.quality = data['quality']
    if 'status' in data:
        if data['status'] in ['上架', '下架', '已下架']:
            item.status = data['status']
    # 处理图片上传
    if 'images' in request.files:
        files = request.files.getlist('images')
        image_urls = []
        for file in files:
            if file.filename:
                image_url = save_uploaded_file(file, 'items')
                if image_url:
                    image_urls.append(image_url)
        
        if image_urls:
            item.description = f"{item.description}\n\n图片链接：{', '.join(image_urls)}"
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '商品信息已更新',
        'data': {'item_id': item.id}
    })

# ---------- 删除商品 ----------
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """删除商品（软删除）"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    item = Item.query.get_or_404(item_id)
    # 检查权限
    if item.seller_id != session['user_id']:
        return jsonify({'code': 403, 'message': '无权删除'})
    # 检查商品是否有未完成的订单
    active_orders = Order.query.filter_by(item_id=item_id)\
                               .filter(Order.status.in_(['待付款', '已付款', '已发货', '待评价']))\
                               .first()
    if active_orders:
        return jsonify({'code': 400, 'message': '商品有未完成的订单，无法删除'})
    # 软删除：标记为已下架
    item.status = '已下架'
    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '商品已下架'
    })

# ---------- 获取用户的商品统计 ----------
@app.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """获取用户的统计信息"""
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '请先登录'})
    user_id = session['user_id']
    # 统计各种状态的商品数量
    items_total = Item.query.filter_by(seller_id=user_id).count()
    items_on_sale = Item.query.filter_by(seller_id=user_id, status='上架').count()
    items_sold = Item.query.filter_by(seller_id=user_id, status='已售出').count()
    # 统计订单
    orders_as_buyer = Order.query.filter_by(buyer_id=user_id).count()
    orders_as_seller = Order.query.filter_by(seller_id=user_id).count()
    # 统计收藏
    favorites_count = Favorite.query.filter_by(user_id=user_id).count()
    # 统计评价
    reviews_received = Review.query.filter_by(reviewed_id=user_id).count()
    return jsonify({
        'code': 200,
        'data': {
            'items': {
                'total': items_total,
                'on_sale': items_on_sale,
                'sold': items_sold
            },
            'orders': {
                'as_buyer': orders_as_buyer,
                'as_seller': orders_as_seller
            },
            'favorites_count': favorites_count,
            'reviews_received': reviews_received
        }
    })

# ==================== 健康检查 ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'code': 200,
        'status': 'healthy',
        'service': '二手书交易平台',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'features': ['用户认证', '商品管理', '订单系统', '议价功能', '评价系统', '智能推荐', '实时聊天']
    })

@app.route('/api/agent/health', methods=['GET'])
def agent_health_check():
    """检查智能体服务状态"""
    try:
        response = requests.get(f"{AGENT_API_URL}/health", timeout=2)
        if response.status_code == 200:
            return jsonify({
                'code': 200,
                'message': '智能体服务正常',
                'data': response.json()
            })
        else:
            return jsonify({
                'code': 503,
                'message': '智能体服务异常',
                'data': {'status_code': response.status_code}
            })
    except Exception as e:
        return jsonify({
            'code': 503,
            'message': '无法连接智能体服务',
            'error': str(e)
        })

# ==================== 主程序入口 ====================
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )