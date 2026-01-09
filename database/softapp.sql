
-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2026-01-02 10:15:59
-- 服务器版本： 5.7.26
-- PHP 版本： 7.3.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `softapp`
--

-- --------------------------------------------------------

--
-- 表的结构 `bargain_logs`
--

CREATE TABLE `bargain_logs` (
  `id` int(11) NOT NULL COMMENT '议价记录ID',
  `item_id` int(11) NOT NULL COMMENT '商品ID',
  `buyer_id` int(11) NOT NULL COMMENT '买家ID',
  `offered_price` decimal(10,2) NOT NULL COMMENT '出价',
  `seller_response` enum('接受','拒绝','待回复','还价') DEFAULT '待回复' COMMENT '卖家回应',
  `seller_counter_price` decimal(10,2) DEFAULT NULL COMMENT '卖家还价',
  `message` varchar(500) DEFAULT NULL COMMENT '议价留言',
  `buyer_contact` varchar(20) DEFAULT NULL COMMENT '买家联系方式',
  `round_number` int(11) DEFAULT '1' COMMENT '议价轮次',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '出价时间',
  `responded_at` datetime DEFAULT NULL COMMENT '回应时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='议价记录表';

--
-- 转存表中的数据 `bargain_logs`
--

INSERT INTO `bargain_logs` (`id`, `item_id`, `buyer_id`, `offered_price`, `seller_response`, `seller_counter_price`, `message`, `buyer_contact`, `round_number`, `created_at`, `responded_at`) VALUES
(1, 1, 2, '4800.00', '拒绝', NULL, '您好，4800可以出吗？诚心要', '13800138002', 1, '2025-12-24 16:06:45', NULL),
(2, 1, 3, '4900.00', '接受', NULL, '4900今天就能交易，方便吗？', '13800138003', 1, '2025-12-24 16:06:45', NULL),
(3, 2, 1, '4200.00', '还价', '4300.00', '4200可以的话我马上付款', '13800138001', 1, '2025-12-24 16:06:45', NULL),
(4, 2, 1, '4300.00', '待回复', NULL, '好的，4300可以接受', '13800138001', 1, '2025-12-24 16:06:45', NULL),
(5, 4, 2, '280.00', '拒绝', NULL, '同学，280元出吗？', '13800138002', 1, '2025-12-24 16:06:45', NULL),
(6, 4, 5, '290.00', '待回复', NULL, '290可以吗？明天可以取', '13800138005', 1, '2025-12-24 16:06:45', NULL),
(7, 7, 1, '45.00', '接受', NULL, '45今天下午取', '13800138001', 1, '2025-12-24 16:06:45', NULL),
(8, 9, 4, '30.00', '拒绝', NULL, '30出吗？考研急需', '13800138004', 1, '2025-12-24 16:06:45', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `browse_history`
--

CREATE TABLE `browse_history` (
  `id` int(11) NOT NULL COMMENT '历史ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `item_id` int(11) NOT NULL COMMENT '商品ID',
  `browse_count` int(11) DEFAULT '1' COMMENT '浏览次数',
  `last_browsed_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '最后浏览时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '首次浏览时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览历史表';

--
-- 转存表中的数据 `browse_history`
--

INSERT INTO `browse_history` (`id`, `user_id`, `item_id`, `browse_count`, `last_browsed_at`, `created_at`) VALUES
(1, 1, 1, 3, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(2, 1, 2, 5, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(3, 1, 4, 2, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(4, 2, 1, 8, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(5, 2, 3, 2, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(6, 2, 5, 4, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(7, 3, 2, 6, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(8, 3, 7, 3, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(9, 4, 1, 2, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(10, 4, 9, 5, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(11, 5, 4, 3, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(12, 5, 10, 2, '2025-12-24 17:03:06', '2025-12-24 17:03:06'),
(13, 6, 1, 4, '2025-12-29 10:22:16', '2025-12-28 22:33:48'),
(14, 6, 3, 5, '2025-12-29 10:36:29', '2025-12-28 22:34:02'),
(15, 6, 11, 6, '2025-12-29 11:18:37', '2025-12-28 22:49:02'),
(16, 6, 7, 2, '2025-12-28 22:49:21', '2025-12-28 22:49:20'),
(17, 6, 6, 4, '2025-12-29 11:11:15', '2025-12-29 10:22:01'),
(18, 7, 11, 4, '2025-12-29 14:48:19', '2025-12-29 10:35:43'),
(19, 6, 4, 3, '2025-12-29 11:01:07', '2025-12-29 10:59:42'),
(20, 7, 8, 2, '2025-12-29 15:01:22', '2025-12-29 15:01:15'),
(21, 6, 12, 3, '2025-12-29 15:13:57', '2025-12-29 15:13:49');

-- --------------------------------------------------------

--
-- 表的结构 `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL COMMENT '分类ID',
  `name` enum('电子产品','书籍资料','衣物服饰','生活用品','运动器材','其他物品') NOT NULL COMMENT '分类名称',
  `sort_order` int(11) DEFAULT '0' COMMENT '排序'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

--
-- 转存表中的数据 `categories`
--

INSERT INTO `categories` (`id`, `name`, `sort_order`) VALUES
(1, '电子产品', 1),
(2, '书籍资料', 2),
(3, '衣物服饰', 3),
(4, '生活用品', 4),
(5, '运动器材', 5),
(6, '其他物品', 6);

-- --------------------------------------------------------

--
-- 表的结构 `favorites`
--

CREATE TABLE `favorites` (
  `id` int(11) NOT NULL COMMENT '收藏ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `item_id` int(11) NOT NULL COMMENT '商品ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

--
-- 转存表中的数据 `favorites`
--

INSERT INTO `favorites` (`id`, `user_id`, `item_id`, `created_at`) VALUES
(1, 1, 2, '2025-12-24 19:01:49'),
(2, 1, 7, '2025-12-24 19:01:49'),
(3, 2, 1, '2025-12-24 19:01:49'),
(4, 2, 4, '2025-12-24 19:01:49'),
(5, 2, 6, '2025-12-24 19:01:49'),
(6, 3, 1, '2025-12-24 19:01:49'),
(7, 3, 2, '2025-12-24 19:01:49'),
(8, 3, 10, '2025-12-24 19:01:49'),
(9, 4, 3, '2025-12-24 19:01:49'),
(10, 4, 9, '2025-12-24 19:01:49'),
(11, 5, 1, '2025-12-24 19:01:49'),
(12, 5, 4, '2025-12-24 19:01:49');

-- --------------------------------------------------------

--
-- 表的结构 `items`
--

CREATE TABLE `items` (
  `id` int(11) NOT NULL COMMENT '商品ID',
  `seller_id` int(11) NOT NULL COMMENT '卖家ID',
  `title` varchar(100) NOT NULL COMMENT '商品标题',
  `description` text COMMENT '商品描述',
  `category_id` int(11) DEFAULT NULL COMMENT '分类ID',
  `price` decimal(10,2) NOT NULL COMMENT '原价',
  `current_price` decimal(10,2) NOT NULL COMMENT '当前价格',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系手机',
  `status` enum('上架','下架','已售出','议价中','已下架') DEFAULT '上架' COMMENT '商品状态',
  `view_count` int(11) DEFAULT '0' COMMENT '浏览数',
  `favorite_count` int(11) DEFAULT '0' COMMENT '收藏数',
  `bargain_enabled` tinyint(1) DEFAULT '1' COMMENT '是否允许议价',
  `min_price` decimal(10,2) DEFAULT NULL COMMENT '最低接受价',
  `is_urgent_sale` tinyint(1) DEFAULT '0' COMMENT '是否急售',
  `seller_min_price` decimal(10,2) DEFAULT NULL COMMENT '卖家心理底价',
  `is_new` tinyint(1) DEFAULT '1' COMMENT '是否全新',
  `quality` enum('全新','九成新','七成新','五成新') DEFAULT '九成新' COMMENT '成色',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

--
-- 转存表中的数据 `items`
--

INSERT INTO `items` (`id`, `seller_id`, `title`, `description`, `category_id`, `price`, `current_price`, `contact_phone`, `status`, `view_count`, `favorite_count`, `bargain_enabled`, `min_price`, `is_urgent_sale`, `seller_min_price`, `is_new`, `quality`, `created_at`, `updated_at`) VALUES
(1, 1, 'iPhone 13 Pro 256G 蓝色', '九成新，无划痕，全套配件，电池健康度95%', 1, '5200.00', '5000.00', '13800138001', '已售出', 161, 23, 1, NULL, 0, NULL, 0, '九成新', '2025-12-24 16:06:45', '2025-12-29 10:22:18'),
(2, 2, '联想ThinkPad X1 Carbon', '轻薄商务本，i7-1165G7，16G内存，512G固态', 1, '4800.00', '4500.00', '13800138002', '议价中', 89, 12, 1, NULL, 0, NULL, 0, '七成新', '2025-12-24 16:06:45', '2025-12-24 16:06:45'),
(3, 3, '高等数学（同济第七版）', '大二教材，有少量笔记，保存完好', 2, '35.00', '30.00', '13800138003', '已售出', 50, 5, 0, NULL, 0, NULL, 0, '七成新', '2025-12-24 16:06:45', '2025-12-29 10:36:31'),
(4, 4, '波司登冬季羽绒服 L码', '黑色长款，只穿过一次，几乎全新', 3, '320.00', '300.00', '13800138004', '已售出', 70, 8, 1, NULL, 0, NULL, 0, '九成新', '2025-12-24 16:06:45', '2025-12-29 11:01:08'),
(5, 1, 'AirPods Pro 二代', '降噪功能完好，配件齐全，送保护套', 1, '850.00', '800.00', '13800138001', '已售出', 123, 15, 1, NULL, 0, NULL, 0, '九成新', '2025-12-24 16:06:45', '2025-12-24 16:06:45'),
(6, 2, 'Java编程思想（第5版）', '经典编程书籍，适合计算机专业学生', 2, '90.00', '75.00', '13800138002', '已售出', 39, 3, 1, NULL, 0, NULL, 0, '五成新', '2025-12-24 16:06:45', '2025-12-29 11:11:16'),
(7, 3, '小米充电宝 20000mAh', '支持快充，双USB输出，使用一年', 4, '65.00', '50.00', '13800138003', '已售出', 58, 7, 0, NULL, 0, NULL, 0, '七成新', '2025-12-24 16:06:45', '2025-12-28 22:49:22'),
(8, 4, '耐克篮球鞋 42码', '实战篮球鞋，防滑耐磨，适合室外场地', 5, '250.00', '220.00', '13800138004', '已售出', 80, 9, 1, NULL, 0, NULL, 0, '五成新', '2025-12-24 16:06:45', '2025-12-29 15:01:23'),
(9, 5, '考研英语词汇书', '全新未使用，附带词汇音频', 2, '40.00', '35.00', '13800138005', '已售出', 26, 2, 0, NULL, 0, NULL, 1, '全新', '2025-12-24 16:06:45', '2025-12-28 21:08:16'),
(10, 3, '保温杯 500ml', '不锈钢材质，保温效果好', 4, '50.00', '40.00', '13800138003', '已售出', 33, 4, 1, NULL, 0, NULL, 1, '全新', '2025-12-24 16:06:45', '2025-12-28 21:06:49'),
(11, 6, '111', '', 1, '111.00', '111.00', '', '已售出', 10, 0, 1, NULL, 0, NULL, 1, '全新', '2025-12-28 21:18:54', '2025-12-29 14:48:20'),
(12, 7, '呃呃呃', '', 1, '12.00', '12.00', '', '已售出', 3, 0, 1, NULL, 0, NULL, 1, '全新', '2025-12-29 15:13:36', '2025-12-29 15:13:58'),
(13, 6, '222', '', 1, '12.00', '12.00', '', '上架', 0, 0, 1, NULL, 0, NULL, 1, '全新', '2025-12-29 16:03:12', '2025-12-29 16:03:12');

--
-- 触发器 `items`
--
DELIMITER $$
CREATE TRIGGER `after_item_seller_update` AFTER UPDATE ON `items` FOR EACH ROW BEGIN
    -- 检查卖家是否变更
    IF OLD.seller_id != NEW.seller_id THEN
        -- 更新所有相关收藏记录的卖家ID
        UPDATE favorites 
        SET seller_id = NEW.seller_id
        WHERE item_id = NEW.id;
        
        -- 可选：记录变更日志
        -- INSERT INTO change_log (table_name, record_id, old_value, new_value)
        -- VALUES ('favorites', NEW.id, OLD.seller_id, NEW.seller_id);
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL COMMENT '消息ID',
  `sender_id` int(11) NOT NULL COMMENT '发送者ID',
  `receiver_id` int(11) NOT NULL COMMENT '接收者ID',
  `item_id` int(11) DEFAULT NULL COMMENT '关联商品ID',
  `content` text NOT NULL COMMENT '消息内容',
  `msg_type` enum('文本','图片','系统','议价通知') DEFAULT '文本' COMMENT '消息类型',
  `is_read` tinyint(1) DEFAULT '0' COMMENT '是否已读',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  `read_at` datetime DEFAULT NULL COMMENT '阅读时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

--
-- 转存表中的数据 `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `receiver_id`, `item_id`, `content`, `msg_type`, `is_read`, `created_at`, `read_at`) VALUES
(1, 2, 1, 1, '你好，这个手机还能便宜吗？', '文本', 0, '2025-12-24 16:10:04', NULL),
(2, 1, 2, 1, '最低4900，不讲价了，成色很好', '文本', 0, '2025-12-24 16:10:04', NULL),
(3, 1, 3, 2, '你的电脑4200可以出吗？', '文本', 0, '2025-12-24 16:10:04', NULL),
(4, 3, 1, 2, '最低4300，已经很便宜了', '文本', 0, '2025-12-24 16:10:04', NULL),
(5, 5, 4, 4, '羽绒服280可以吗？', '文本', 0, '2025-12-24 16:10:04', NULL),
(6, 4, 5, 4, '最低300，不议价', '文本', 0, '2025-12-24 16:10:04', NULL),
(7, 1, 3, 7, '充电宝45出吗？', '文本', 0, '2025-12-24 16:10:04', NULL),
(8, 3, 1, 7, '可以，下午来取', '文本', 0, '2025-12-24 16:10:04', NULL),
(9, 2, 5, 9, '考研书还在吗？', '文本', 0, '2025-12-24 16:10:04', NULL),
(10, 5, 2, 9, '在的，35出', '文本', 0, '2025-12-24 16:10:04', NULL),
(11, 2, 1, 1, '你好，这个手机还能便宜吗？', '文本', 0, '2025-12-24 17:03:06', NULL),
(12, 1, 2, 1, '最低4900，不讲价了，成色很好', '文本', 0, '2025-12-24 17:03:06', NULL),
(13, 1, 3, 2, '你的电脑4200可以出吗？', '文本', 0, '2025-12-24 17:03:06', NULL),
(14, 3, 1, 2, '最低4300，已经很便宜了', '文本', 0, '2025-12-24 17:03:06', NULL),
(15, 5, 4, 4, '羽绒服280可以吗？', '文本', 0, '2025-12-24 17:03:06', NULL),
(16, 4, 5, 4, '最低300，不议价', '文本', 0, '2025-12-24 17:03:06', NULL),
(17, 1, 3, 7, '充电宝45出吗？', '文本', 0, '2025-12-24 17:03:06', NULL),
(18, 3, 1, 7, '可以，下午来取', '文本', 0, '2025-12-24 17:03:06', NULL),
(19, 2, 5, 9, '考研书还在吗？', '文本', 0, '2025-12-24 17:03:06', NULL),
(20, 5, 2, 9, '在的，35出', '文本', 0, '2025-12-24 17:03:06', NULL);

-- --------------------------------------------------------

--
-- 表的结构 `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL COMMENT '订单ID',
  `order_no` varchar(50) NOT NULL COMMENT '订单编号',
  `item_id` int(11) NOT NULL COMMENT '商品ID',
  `buyer_id` int(11) NOT NULL COMMENT '买家ID',
  `seller_id` int(11) NOT NULL COMMENT '卖家ID',
  `final_price` decimal(10,2) NOT NULL COMMENT '成交价',
  `status` enum('待付款','已付款','已发货','已完成','已取消','退款中') DEFAULT '待付款' COMMENT '订单状态',
  `payment_method` enum('余额','微信','支付宝','货到付款') DEFAULT NULL COMMENT '支付方式',
  `payment_id` varchar(100) DEFAULT NULL COMMENT '支付交易号',
  `buyer_phone` varchar(20) NOT NULL COMMENT '买家手机',
  `seller_phone` varchar(20) NOT NULL COMMENT '卖家手机',
  `shipping_address` text COMMENT '收货地址',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `buyer_note` text COMMENT '买家留言',
  `seller_note` text COMMENT '卖家留言',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `paid_at` datetime DEFAULT NULL COMMENT '付款时间',
  `shipped_at` datetime DEFAULT NULL COMMENT '发货时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

--
-- 转存表中的数据 `orders`
--

INSERT INTO `orders` (`id`, `order_no`, `item_id`, `buyer_id`, `seller_id`, `final_price`, `status`, `payment_method`, `payment_id`, `buyer_phone`, `seller_phone`, `shipping_address`, `contact_phone`, `buyer_note`, `seller_note`, `created_at`, `paid_at`, `shipped_at`, `completed_at`) VALUES
(7, 'ORD20231215001', 5, 2, 1, '800.00', '已完成', '支付宝', NULL, '13800138002', '13800138001', '学生宿舍3号楼201室', NULL, '请下午6点后配送', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(8, 'ORD20231215002', 1, 3, 1, '4900.00', '已付款', '微信', NULL, '13800138003', '13800138001', '教学楼A座305教室', NULL, '希望今天能收到', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(9, 'ORD20231215003', 2, 1, 2, '4300.00', '待付款', NULL, NULL, '13800138001', '13800138002', '图书馆自习区', NULL, '周末交易', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(10, 'ORD20231215004', 7, 1, 3, '45.00', '已发货', '余额', NULL, '13800138001', '13800138003', '宿舍区快递站', NULL, '', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(11, 'ORD20231215005', 3, 4, 3, '30.00', '已完成', '微信', NULL, '13800138004', '13800138003', '体育馆门口', NULL, '明天下午3点取', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(12, 'ORD20231215006', 9, 2, 5, '35.00', '已付款', '支付宝', NULL, '13800138002', '13800138005', '教学楼B座', NULL, '急用，谢谢', NULL, '2025-12-24 16:10:04', NULL, NULL, NULL),
(13, 'ORD17669272086', 10, 6, 3, '40.00', '待付款', NULL, NULL, '1235', '13800138003', NULL, NULL, '我想购买这本书', NULL, '2025-12-28 21:06:49', NULL, NULL, NULL),
(14, 'ORD17669272956', 9, 6, 5, '35.00', '待付款', NULL, NULL, '1235', '13800138005', NULL, NULL, '我想购买这本书', NULL, '2025-12-28 21:08:16', NULL, NULL, NULL),
(15, 'ORD17669333626', 7, 6, 3, '50.00', '待付款', NULL, NULL, '1235', '13800138003', NULL, NULL, '', NULL, '2025-12-28 22:49:22', NULL, NULL, NULL),
(16, 'ORD17669749376', 1, 6, 1, '5000.00', '待付款', NULL, NULL, '1235', '13800138001', NULL, NULL, '', NULL, '2025-12-29 10:22:18', NULL, NULL, NULL),
(17, 'ORD17669757906', 3, 6, 3, '30.00', '待付款', NULL, NULL, '222', '13800138003', NULL, NULL, '', NULL, '2025-12-29 10:36:31', NULL, NULL, NULL),
(18, 'ORD17669772686', 4, 6, 4, '300.00', '待付款', NULL, NULL, '1235', '13800138004', NULL, NULL, '', NULL, '2025-12-29 11:01:08', NULL, NULL, NULL),
(19, 'ORD17669778756', 6, 6, 2, '75.00', '待付款', NULL, NULL, '1235', '13800138002', NULL, NULL, '', NULL, '2025-12-29 11:11:16', NULL, NULL, NULL),
(20, 'ORD17669909007', 11, 7, 6, '111.00', '待付款', NULL, NULL, '222', '1235', '', '222', '', NULL, '2025-12-29 14:48:20', NULL, NULL, NULL),
(21, 'ORD17669916827', 8, 7, 4, '220.00', '待付款', NULL, NULL, '222', '13800138004', '', '222', '', NULL, '2025-12-29 15:01:23', NULL, NULL, NULL),
(22, 'ORD17669924376', 12, 6, 7, '12.00', '待付款', NULL, NULL, '1235', '222', '', '1235', '', NULL, '2025-12-29 15:13:58', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- 表的结构 `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL COMMENT '评价ID',
  `order_id` int(11) NOT NULL COMMENT '订单ID',
  `reviewer_id` int(11) NOT NULL COMMENT '评价者ID',
  `reviewed_id` int(11) NOT NULL COMMENT '被评价者ID',
  `rating` enum('1','2','3','4','5') NOT NULL COMMENT '评分(1-5)',
  `content` text COMMENT '评价内容',
  `type` enum('买家评价卖家','卖家评价买家') DEFAULT NULL COMMENT '评价类型',
  `is_anonymous` tinyint(1) DEFAULT '0' COMMENT '是否匿名',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评价表';

--
-- 转存表中的数据 `reviews`
--

INSERT INTO `reviews` (`id`, `order_id`, `reviewer_id`, `reviewed_id`, `rating`, `content`, `type`, `is_anonymous`, `created_at`) VALUES
(7, 7, 2, 1, '5', '卖家很靠谱，耳机音质很好，交易顺利', '买家评价卖家', 0, '2025-12-24 17:03:06'),
(8, 8, 3, 1, '4', '手机成色很好，物超所值，希望下次还能交易', '买家评价卖家', 0, '2025-12-24 17:03:06'),
(9, 9, 1, 2, '4', '卖家态度很好，沟通顺畅', '卖家评价买家', 0, '2025-12-24 17:03:06'),
(10, 10, 1, 3, '5', '充电宝很好用，谢谢卖家', '买家评价卖家', 0, '2025-12-24 17:03:06'),
(11, 11, 4, 3, '5', '教材很实用，卖家很耐心讲解', '买家评价卖家', 0, '2025-12-24 17:03:06'),
(12, 12, 2, 5, '4', '书是新的，价格合理，发货快', '买家评价卖家', 0, '2025-12-24 17:03:06');

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希值',
  `phone` varchar(20) NOT NULL COMMENT '手机号',
  `credit_score` int(11) DEFAULT '80' COMMENT '信用分（范围：0-100）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `phone`, `credit_score`) VALUES
(1, '张三', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '13800138001', 80),
(2, '李四', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '13800138002', 80),
(3, '王五', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '13800138003', 80),
(4, '赵六', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '13800138004', 80),
(5, '测试用户', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '13800138005', 80),
(6, '555', '555', '1235', 80),
(7, '222', '222', '222', 80);

--
-- 转储表的索引
--

--
-- 表的索引 `bargain_logs`
--
ALTER TABLE `bargain_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_item_id` (`item_id`),
  ADD KEY `idx_buyer_id` (`buyer_id`),
  ADD KEY `idx_seller_response` (`seller_response`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `idx_buyer_contact` (`buyer_contact`);

--
-- 表的索引 `browse_history`
--
ALTER TABLE `browse_history`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `idx_user_item` (`user_id`,`item_id`),
  ADD KEY `item_id` (`item_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_last_browsed` (`last_browsed_at`);

--
-- 表的索引 `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `idx_sort_order` (`sort_order`);

--
-- 表的索引 `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `idx_user_item` (`user_id`,`item_id`),
  ADD KEY `item_id` (`item_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- 表的索引 `items`
--
ALTER TABLE `items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_seller_id` (`seller_id`),
  ADD KEY `idx_category_id` (`category_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_price` (`current_price`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `idx_quality` (`quality`);
ALTER TABLE `items` ADD FULLTEXT KEY `idx_title_desc` (`title`,`description`);

--
-- 表的索引 `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sender_receiver` (`sender_id`,`receiver_id`),
  ADD KEY `idx_receiver_read` (`receiver_id`,`is_read`),
  ADD KEY `idx_item_id` (`item_id`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- 表的索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_no` (`order_no`),
  ADD KEY `idx_order_no` (`order_no`),
  ADD KEY `idx_buyer_id` (`buyer_id`),
  ADD KEY `idx_seller_id` (`seller_id`),
  ADD KEY `idx_item_id` (`item_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_buyer_phone` (`buyer_phone`),
  ADD KEY `idx_seller_phone` (`seller_phone`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- 表的索引 `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `idx_order_reviewer_type` (`order_id`,`reviewer_id`,`type`),
  ADD KEY `reviewer_id` (`reviewer_id`),
  ADD KEY `idx_reviewed_id` (`reviewed_id`),
  ADD KEY `idx_rating` (`rating`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `phone` (`phone`),
  ADD KEY `idx_username` (`username`),
  ADD KEY `idx_phone` (`phone`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `bargain_logs`
--
ALTER TABLE `bargain_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '议价记录ID', AUTO_INCREMENT=9;

--
-- 使用表AUTO_INCREMENT `browse_history`
--
ALTER TABLE `browse_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '历史ID', AUTO_INCREMENT=22;

--
-- 使用表AUTO_INCREMENT `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '分类ID', AUTO_INCREMENT=7;

--
-- 使用表AUTO_INCREMENT `favorites`
--
ALTER TABLE `favorites`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '收藏ID', AUTO_INCREMENT=13;

--
-- 使用表AUTO_INCREMENT `items`
--
ALTER TABLE `items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '商品ID', AUTO_INCREMENT=14;

--
-- 使用表AUTO_INCREMENT `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '消息ID', AUTO_INCREMENT=21;

--
-- 使用表AUTO_INCREMENT `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '订单ID', AUTO_INCREMENT=23;

--
-- 使用表AUTO_INCREMENT `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '评价ID', AUTO_INCREMENT=13;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID', AUTO_INCREMENT=8;

--
-- 限制导出的表
--

--
-- 限制表 `bargain_logs`
--
ALTER TABLE `bargain_logs`
  ADD CONSTRAINT `bargain_logs_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bargain_logs_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- 限制表 `browse_history`
--
ALTER TABLE `browse_history`
  ADD CONSTRAINT `browse_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `browse_history_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE;

--
-- 限制表 `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE CASCADE;

--
-- 限制表 `items`
--
ALTER TABLE `items`
  ADD CONSTRAINT `items_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `items_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL;

--
-- 限制表 `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`) ON DELETE SET NULL;

--
-- 限制表 `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

--
-- 限制表 `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`reviewed_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
