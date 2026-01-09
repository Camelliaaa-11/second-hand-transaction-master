# database/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 用户表
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希值')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    credit_score = db.Column(db.Integer, default=80, comment='信用分（范围：0-100）')
    # 新增头像字段，方便后续扩展
    avatar = db.Column(db.String(255), default='', comment='头像URL')

    # 关系
    items = db.relationship('Item', backref='seller', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='sender',
                                    lazy=True)
    received_messages = db.relationship('Message',
                                        foreign_keys='Message.receiver_id',
                                        backref='receiver',
                                        lazy=True)
    buy_orders = db.relationship('Order',
                                 foreign_keys='Order.buyer_id',
                                 backref='buyer',
                                 lazy=True)
    sell_orders = db.relationship('Order',
                                  foreign_keys='Order.seller_id',
                                  backref='seller_user',
                                  lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    bargain_logs = db.relationship('BargainLog',
                                   foreign_keys='BargainLog.buyer_id',
                                   backref='buyer',
                                   lazy=True)
    browse_history = db.relationship('BrowseHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews_given = db.relationship('Review',
                                    foreign_keys='Review.reviewer_id',
                                    backref='reviewer',
                                    lazy=True)
    reviews_received = db.relationship('Review',
                                       foreign_keys='Review.reviewed_id',
                                       backref='reviewed',
                                       lazy=True)


# 分类表
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, comment='分类ID')
    name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    sort_order = db.Column(db.Integer, default=0, comment='排序')

    # 关系
    items = db.relationship('Item', backref='category_ref', lazy=True)


# 商品表
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True, comment='商品ID')
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='卖家ID')
    title = db.Column(db.String(100), nullable=False, comment='商品标题')
    description = db.Column(db.Text, comment='商品描述')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), comment='分类ID')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='原价')
    current_price = db.Column(db.Numeric(10, 2), nullable=False, comment='当前价格')
    contact_phone = db.Column(db.String(20), comment='联系手机')
    category = db.Column(db.String(50), default='其他')
    # ⭐⭐⭐ 重点修复：补上了 image_data 字段 ⭐⭐⭐
    image_data = db.Column(db.String(500), default='', comment='商品图片URL')

    # 新增字段
    is_urgent_sale = db.Column(db.Boolean, default=False, comment='是否急售')
    seller_min_price = db.Column(db.Numeric(10, 2), nullable=True, comment='卖家心理底价')

    status = db.Column(
        db.Enum('上架', '下架', '已售出', '议价中', '已下架'),
        default='上架',
        comment='商品状态'
    )
    view_count = db.Column(db.Integer, default=0, comment='浏览数')
    favorite_count = db.Column(db.Integer, default=0, comment='收藏数')
    bargain_enabled = db.Column(db.Boolean, default=True, comment='是否允许议价')
    min_price = db.Column(db.Numeric(10, 2), comment='最低接受价')
    is_new = db.Column(db.Boolean, default=True, comment='是否全新')
    quality = db.Column(
        db.Enum('全新', '九成新', '七成新', '五成新'),
        default='九成新',
        comment='成色'
    )
    created_at = db.Column(db.DateTime, default=datetime.now, comment='发布时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    orders = db.relationship('Order', backref='item', lazy=True)
    messages = db.relationship('Message', backref='item', lazy=True)
    favorites = db.relationship('Favorite', backref='item', lazy=True, cascade='all, delete-orphan')
    bargain_logs = db.relationship('BargainLog', backref='item', lazy=True, cascade='all, delete-orphan')
    browse_history = db.relationship('BrowseHistory', backref='item', lazy=True, cascade='all, delete-orphan')


# 议价记录表
class BargainLog(db.Model):
    __tablename__ = 'bargain_logs'
    id = db.Column(db.Integer, primary_key=True, comment='议价记录ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='买家ID')
    offered_price = db.Column(db.Numeric(10, 2), nullable=False, comment='出价')
    seller_response = db.Column(
        db.Enum('接受', '拒绝', '待回复', '还价'),
        default='待回复',
        comment='卖家回应'
    )
    seller_counter_price = db.Column(db.Numeric(10, 2), comment='卖家还价')
    message = db.Column(db.String(500), comment='议价留言')
    buyer_contact = db.Column(db.String(20), comment='买家联系方式')
    round_number = db.Column(db.Integer, default=1, comment='议价轮次')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='出价时间')
    responded_at = db.Column(db.DateTime, comment='回应时间')


# 订单表
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, comment='订单ID')
    order_no = db.Column(db.String(50), unique=True, nullable=False, comment='订单编号')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='买家ID')
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='卖家ID')
    final_price = db.Column(db.Numeric(10, 2), nullable=False, comment='成交价')
    status = db.Column(
        db.Enum('待付款', '已付款', '已发货', '已完成', '已取消', '退款中'),
        default='待付款',
        comment='订单状态'
    )
    payment_method = db.Column(
        db.Enum('余额', '微信', '支付宝', '货到付款'),
        comment='支付方式'
    )
    payment_id = db.Column(db.String(100), comment='支付交易号')
    buyer_phone = db.Column(db.String(20), nullable=False, comment='买家手机')
    seller_phone = db.Column(db.String(20), nullable=False, comment='卖家手机')
    shipping_address = db.Column(db.Text, comment='收货地址')
    contact_phone = db.Column(db.String(20), comment='联系电话')
    buyer_note = db.Column(db.Text, comment='买家留言')
    seller_note = db.Column(db.Text, comment='卖家留言')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    paid_at = db.Column(db.DateTime, comment='付款时间')
    shipped_at = db.Column(db.DateTime, comment='发货时间')
    completed_at = db.Column(db.DateTime, comment='完成时间')

    # 关系
    reviews = db.relationship('Review', backref='order', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='order_ref', lazy=True)


# 消息表
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, comment='消息ID')
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='发送者ID')
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='接收者ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), comment='关联商品ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), comment='关联订单ID')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    msg_type = db.Column(
        db.Enum('文本', '图片', '系统', '议价通知'),
        default='文本',
        comment='消息类型'
    )
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='发送时间')
    read_at = db.Column(db.DateTime, comment='阅读时间')


# 收藏表
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True, comment='收藏ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='收藏时间')


# 评价表
# 评价表
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True, comment='评价ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='订单ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='评价者ID')
    reviewed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='被评价者ID')
    
    # ⭐⭐⭐ 修正点：改成 items.id (复数) ⭐⭐⭐
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), comment='关联商品ID')
    
    rating = db.Column(
        db.Enum('1', '2', '3', '4', '5'),
        nullable=False,
        comment='评分(1-5)'
    )
    content = db.Column(db.Text, comment='评价内容')
    type = db.Column(
        db.Enum('买家评价卖家', '卖家评价买家'),
        comment='评价类型'
    )
    is_anonymous = db.Column(db.Boolean, default=False, comment='是否匿名')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='评价时间')


# 浏览历史表
class BrowseHistory(db.Model):
    __tablename__ = 'browse_history'
    id = db.Column(db.Integer, primary_key=True, comment='历史ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    browse_count = db.Column(db.Integer, default=1, comment='浏览次数')
    last_browsed_at = db.Column(db.DateTime, default=datetime.now, comment='最后浏览时间')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='首次浏览时间')