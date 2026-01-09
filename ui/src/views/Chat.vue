<template>
  <div class="chat-room">
    <van-nav-bar :title="friendName" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="msg-container" ref="msgBox">
      <div v-for="msg in list" :key="msg.id" :class="['msg-row', isMe(msg.senderId) ? 'right' : 'left']">
        <div class="avatar" v-if="!isMe(msg.senderId)">{{ friendName.charAt(0) }}</div>
        
        <div class="bubble">
          <div 
            v-if="msg.item" 
            class="mini-item" 
            @click="$router.push(`/detail/${msg.item.id}`)"
          >
            <img :src="msg.item.img" />
            <div class="mini-info">
              <div class="mini-title">{{ msg.item.title }}</div>
              <div class="mini-price">¥{{ msg.item.price }}</div>
            </div>
          </div>

          <div v-if="msg.msg_type === '议价通知' || (msg.content && (msg.content.includes('【议价申请】') || msg.content.includes('【卖家还价】')))" class="bargain-card">
            <div class="b-title">{{ msg.content.includes('【卖家还价】') ? '💰 卖家还价' : '🗡️ 砍价申请' }}</div>
            <div class="b-text">{{ msg.content }}</div>
            
            <div v-if="!isMe(msg.senderId)" class="b-actions">
               <!-- 卖家收到买家议价 -->
               <template v-if="!msg.content.includes('【卖家还价】')">
                 <van-button size="mini" type="primary" @click="getSellerAdvice(msg)">🤖智能回复</van-button>
                 <div style="width: 10px;"></div>
                 <van-button size="mini" type="danger" @click="handleBargain(msg, 'reject')">拒绝</van-button>
                 <div style="width: 10px;"></div>
                 <van-button size="mini" type="success" @click="handleBargain(msg, 'accept')">同意改价</van-button>
               </template>
               
               <!-- 买家收到卖家还价 -->
               <template v-else>
                 <van-button size="mini" type="warning" @click="openBuyerCounterOffer(msg)">💬 我要还价</van-button>
                 <div style="width: 10px;"></div>
                 <van-button size="mini" type="danger" @click="handleBargain(msg, 'reject')">拒绝</van-button>
                 <div style="width: 10px;"></div>
                 <van-button size="mini" type="success" @click="handleBargain(msg, 'accept')">接受还价</van-button>
               </template>
            </div>
          </div>

          <div v-else>{{ msg.content }}</div>
        </div>

        <div class="avatar my-avatar" v-if="isMe(msg.senderId)">我</div>
      </div>
      <div id="bottom-anchor"></div>
    </div>

    <div class="input-area">
      <van-button 
        size="small" 
        type="primary" 
        icon="guide-o"
        @click="openSellerAdviceForLatest"
        style="margin-right: 8px;"
      >
        🤖智能回复
      </van-button>
      <input v-model="text" type="text" placeholder="发消息..." @keyup.enter="send" />
      <button :disabled="!text" @click="send">发送</button>
    </div>

    <!-- 卖家智能回复弹窗 -->
    <van-dialog 
      v-model:show="showSellerAdviceDialog" 
      title="🤖 AI智能回复助手" 
      show-cancel-button 
      confirm-button-text="采纳并发送"
      @confirm="adoptSellerAdvice"
    >
      <div style="padding: 20px;">
        <van-loading v-if="loadingSellerAdvice" size="24px">AI正在分析...</van-loading>
        
        <div v-else-if="sellerAdvice">
          <!-- 建议动作 -->
          <van-tag 
            :type="getActionTagType(sellerAdvice.action)" 
            size="large" 
            style="margin-bottom: 10px;"
          >
            {{ getActionText(sellerAdvice.action) }}
          </van-tag>
          
          <!-- 推荐价格 -->
          <div v-if="sellerAdvice.price" style="margin: 15px 0;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">AI推荐价格</div>
            <div style="font-size: 28px; color: #ff5000; font-weight: bold;">
              ¥{{ sellerAdvice.price }}
            </div>
          </div>
          
          <!-- 自定义价格 -->
          <van-field
            v-model.number="customSellerPrice"
            type="number"
            label="调整价格"
            placeholder="可以修改报价"
            :rules="[{ pattern: /^\d+(\.\d{1,2})?$/, message: '请输入正确的价格' }]"
            style="margin-top: 10px;"
          >
            <template #button>
              <span style="color: #999; font-size: 12px;">元</span>
            </template>
          </van-field>
          
          <!-- AI建议话术 -->
          <div style="background: #f7f8fa; padding: 12px; border-radius: 8px; margin: 15px 0;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">💬 建议话术</div>
            <div style="font-size: 14px; color: #333; line-height: 1.6;">
              {{ displayMessage }}
            </div>
          </div>
          
          <!-- AI分析理由 -->
          <div style="margin-top: 15px;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">🧠 策略分析</div>
            <div style="font-size: 13px; color: #666; line-height: 1.5;">
              {{ sellerAdvice.reasoning }}
            </div>
          </div>
          
          <!-- 自定义调整 -->
          <van-field
            v-model="customSellerMessage"
            type="textarea"
            rows="3"
            label="微调话术"
            placeholder="也可以自己修改"
            style="margin-top: 15px;"
          />
        </div>
        
        <div v-else style="text-align: center; padding: 20px; color: #999;">
          未能获取智能建议
        </div>
      </div>
    </van-dialog>

    <!-- 买家再次还价弹窗 -->
    <van-dialog 
      v-model:show="showBuyerCounterDialog" 
      title="💬 买家再次还价" 
      show-cancel-button 
      confirm-button-text="发送还价"
      @confirm="sendBuyerCounterOffer"
    >
      <div style="padding: 20px;">
        <div v-if="currentSellerCounterMsg">
          <div style="margin-bottom: 15px;">
            <div style="font-size: 12px; color: #999;">卖家还价</div>
            <div style="font-size: 24px; color: #ff5000; font-weight: bold;">
              ¥{{ extractPrice(currentSellerCounterMsg.content) }}
            </div>
          </div>
          
          <van-field
            v-model.number="buyerCounterPrice"
            type="number"
            label="你的还价"
            placeholder="输入你想出的价格"
            :rules="[{ pattern: /^\d+(\.\d{1,2})?$/, message: '请输入正确的价格' }]"
          >
            <template #button>
              <span style="color: #999; font-size: 12px;">元</span>
            </template>
          </van-field>
          
          <div style="margin-top: 15px; font-size: 12px; color: #999;">
            💡 提示：输入一个新的价格，继续和卖家协商
          </div>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import io from 'socket.io-client';
// ⭐ 引入 Toast
import { showSuccessToast, showFailToast } from 'vant';

const route = useRoute();
const friendId = route.params.id;
const friendName = route.query.name || '聊天';
const text = ref('');
const list = ref([]);
const socket = ref(null); 

// 卖家智能回复相关
const showSellerAdviceDialog = ref(false);
const sellerAdvice = ref(null);
const loadingSellerAdvice = ref(false);
const customSellerMessage = ref('');
const customSellerPrice = ref(0);
const currentBargainMsg = ref(null);

// 买家还价相关
const showBuyerCounterDialog = ref(false);
const buyerCounterPrice = ref(0);
const currentSellerCounterMsg = ref(null);

// 计算显示的消息内容（根据自定义价格动态更新）
const displayMessage = computed(() => {
  if (!sellerAdvice.value?.message) return '';
  
  let message = sellerAdvice.value.message;
  const originalPrice = sellerAdvice.value.price;
  const newPrice = customSellerPrice.value;
  
  // 如果用户修改了价格
  if (newPrice > 0 && newPrice !== originalPrice) {
    // 判断当前用户是买家还是卖家（通过查看currentBargainMsg来判断）
    const isBuyerRole = currentBargainMsg.value && 
                        (currentBargainMsg.value.sender_id === myId || currentBargainMsg.value.senderId === myId);
    
    if (isBuyerRole) {
      // 买家角色：如果改价比卖家还价低，用"便宜点啦"语气
      if (newPrice < originalPrice) {
        message = `便宜点啦，${newPrice}可以不`;
      } else {
        // 买家提高价格或持平，直接替换
        const pricePattern = new RegExp(`${originalPrice}(\\.\\d+)?元?`, 'g');
        if (pricePattern.test(message)) {
          message = message.replace(pricePattern, `${newPrice}元`);
        } else {
          message = `${newPrice}元，` + message;
        }
      }
    } else {
      // 卖家角色：如果改价比AI推荐高，用"可以的话就拍下吧"语气
      if (newPrice > originalPrice) {
        message = `${newPrice}可以的话就拍下吧`;
      } else {
        // 价格持平或降低时，检查是否需要替换价格
        const pricePattern = new RegExp(`${originalPrice}(\\.\\d+)?元?`, 'g');
        if (pricePattern.test(message)) {
          message = message.replace(pricePattern, `${newPrice}元`);
        } else {
          // 如果不包含价格，根据动作类型生成话术
          if (sellerAdvice.value.action === 'ACCEPT') {
            message = `好的，${newPrice}元成交！`;
          } else if (sellerAdvice.value.action === 'COUNTER_OFFER') {
            message = `${newPrice}元可以出手，您看怎么样？`;
          } else {
            message = `${newPrice}元，` + message;
          }
        }
      }
    }
  }
  
  return message;
});

const userStr = localStorage.getItem('user');
const myId = userStr ? JSON.parse(userStr).id : 0;

const isMe = (senderId) => {
  return String(senderId) === String(myId);
};

const scrollToBottom = () => {
  nextTick(() => {
    const anchor = document.getElementById('bottom-anchor');
    if (anchor) anchor.scrollIntoView({ behavior: "smooth" });
  });
};

const fetchHistory = async () => {
  try {
    const res = await axios.get(`/api/v1/messages/history`, {
      params: { userId: myId, friendId: friendId }
    });
    if (res.data.success) {
      list.value = res.data.data;
      scrollToBottom();
    }
    await axios.post('/api/v1/messages/read', {
      userId: myId,
      friendId: friendId
    });
  } catch (e) { console.error(e); }
};

const send = () => {
  if (!text.value) return;
  socket.value.emit('send_msg', {
    senderId: myId,
    receiverId: friendId,
    content: text.value,
    msg_type: '文本' // ⭐ 明确标记为文本
  });
  text.value = '';
};

// ⭐⭐⭐ 修复版：万能适配，防止参数丢失 ⭐⭐⭐
const handleBargain = async (msg, action) => {
  // 1. 获取商品ID (优先从 item 对象里取，如果没有再找 item_id)
  const theItemId = (msg.item && msg.item.id) || msg.item_id || msg.itemId;
  
  // 2. 判断是买家议价还是卖家还价
  const isSellerCounter = msg.content && msg.content.includes('【卖家还价】');
  
  // 3. 获取买家ID
  let theBuyerId;
  if (isSellerCounter) {
    // 如果是卖家还价，买家ID就是当前用户
    theBuyerId = myId;
  } else {
    // 如果是买家议价，买家ID就是消息发送者
    theBuyerId = msg.sender_id || msg.senderId;
  }

  // 调试打印：按F12看控制台，确认这两个数是不是都有值
  console.log("正在处理议价:", { item_id: theItemId, buyer_id: theBuyerId, action, isSellerCounter });

  if (!theItemId || !theBuyerId) {
    return showFailToast('参数缺失，无法操作，请尝试刷新页面');
  }

  try {
    const res = await axios.post('/api/v1/bargain/handle', {
      item_id: theItemId,
      buyer_id: theBuyerId,
      action: action
    });
    
    if (res.data.success) {
      showSuccessToast(action === 'accept' ? '已同意，价格已修改' : '已拒绝');
      
      // 更新本地界面
      list.value.push({
        id: Date.now(),
        senderId: myId, // 这里用 senderId 保持一致
        sender_id: myId,
        content: action === 'accept' ? '【系统】我同意了议价，价格已修改。' : '【系统】我拒绝了议价。',
        msg_type: '系统'
      });
      scrollToBottom();
    } else {
      showFailToast(res.data.message);
    }
  } catch (e) {
    console.error(e);
    showFailToast('网络错误');
  }
};

// 卖家获取智能回复建议
const getSellerAdvice = async (msg) => {
  currentBargainMsg.value = msg;
  const theItemId = (msg.item && msg.item.id) || msg.item_id || msg.itemId;
  const theBuyerId = msg.sender_id || msg.senderId;
  
  if (!theItemId || !theBuyerId) {
    showFailToast('缺少必要信息');
    return;
  }
  
  showSellerAdviceDialog.value = true;
  loadingSellerAdvice.value = true;
  sellerAdvice.value = null;
  customSellerMessage.value = '';
  
  try {
    // 从消息内容中提取买家出价
    const buyerOffer = extractBuyerOffer(msg.content);
    
    const data = {
      user_id: myId,
      item_id: theItemId,
      item_listed_price: msg.item?.price || 0,
      seller_min_price: (msg.item?.price || 0) * 0.7, // 假设底价为标价的70%
      buyer_offer: buyerOffer,
      is_urgent_sale: false,
      buyer_id: theBuyerId,
      item_category: msg.item?.category || '其他',
      item_condition: msg.item?.quality || 'GOOD'
    };
    
    const res = await axios.post('/api/agent/seller-advice', data);
    
    if (res.data.code === 200 && res.data.data) {
      sellerAdvice.value = res.data.data;
      // 不初始化customSellerMessage，让用户手动修改时才有值
      customSellerPrice.value = res.data.data.price || 0;
    } else {
      showFailToast(res.data.message || '获取智能建议失败');
    }
  } catch (e) {
    console.error('获取卖家智能建议失败:', e);
    showFailToast('网络错误，请稍后重试');
  } finally {
    loadingSellerAdvice.value = false;
  }
};

// 为最近的议价消息打开智能回复
const openSellerAdviceForLatest = () => {
  // 从后往前找最近的议价消息
  for (let i = list.value.length - 1; i >= 0; i--) {
    const msg = list.value[i];
    if ((msg.msg_type === '议价通知' || (msg.content && msg.content.includes('【议价申请】'))) && !isMe(msg.senderId)) {
      getSellerAdvice(msg);
      return;
    }
  }
  showFailToast('没有找到议价消息');
};

// 从消息内容中提取买家出价
const extractBuyerOffer = (content) => {
  if (!content) return 0;
  // 匹配多种格式：期望价格65、65元、¥65、出价65等
  const patterns = [
    /期望价格[:：]?\s*¥?(\d+\.?\d*)/,
    /出价[:：]?\s*¥?(\d+\.?\d*)/,
    /(\d+\.?\d*)\s*元/,
    /¥\s*(\d+\.?\d*)/
  ];
  
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match) return parseFloat(match[1]);
  }
  
  return 0;
};

// 采纳卖家智能建议并发送
const adoptSellerAdvice = async () => {
  // 使用自定义的消息，或者使用计算后的displayMessage
  let messageToSend = customSellerMessage.value || displayMessage.value;
  
  if (!messageToSend) {
    showFailToast('请输入回复内容');
    return;
  }
  
  // 检查价格是否改变
  const priceChanged = customSellerPrice.value > 0 && customSellerPrice.value !== sellerAdvice.value?.price;
  
  // 如果价格改变了，通过API发起还价
  if (priceChanged && currentBargainMsg.value) {
    try {
      const theItemId = (currentBargainMsg.value.item && currentBargainMsg.value.item.id) || currentBargainMsg.value.item_id || currentBargainMsg.value.itemId;
      const theBuyerId = currentBargainMsg.value.sender_id || currentBargainMsg.value.senderId;
      
      const res = await axios.post('/api/v1/bargain/handle', {
        item_id: theItemId,
        buyer_id: theBuyerId,
        action: 'counter',
        counter_price: customSellerPrice.value
      });
      
      if (!res.data.success) {
        showFailToast(res.data.message || '还价失败');
        return;
      }
    } catch (e) {
      console.error('还价失败:', e);
      showFailToast('还价失败，请稍后重试');
      return;
    }
  }
  
  // 发送消息
  socket.value.emit('send_msg', {
    senderId: myId,
    receiverId: friendId,
    content: messageToSend,
    msg_type: '文本'
  });
  
  // 立即在本地添加消息到列表（让卖家自己也能看到）
  list.value.push({
    id: Date.now(),
    senderId: myId,
    sender_id: myId,
    content: messageToSend,
    msg_type: '文本',
    created_at: new Date()
  });
  scrollToBottom();
  
  showSuccessToast(priceChanged ? 'AI还价已发送' : 'AI建议已发送');
  showSellerAdviceDialog.value = false;
  
  // 如果AI建议接受，并且用户没有修改价格，才自动处理议价
  if (sellerAdvice.value?.action === 'ACCEPT' && currentBargainMsg.value && !priceChanged) {
    // 只有价格没改变时，才接受买家的原始出价
    handleBargain(currentBargainMsg.value, 'accept');
  }
  // 如果价格改变了，已经通过API发起还价，不需要再自动接受
};

// 获取动作标签类型
const getActionTagType = (action) => {
  const map = {
    'ACCEPT': 'success',
    'COUNTER': 'warning',
    'HOLD': 'primary',
    'REJECT': 'danger'
  };
  return map[action] || 'default';
};

// 获取动作文本
const getActionText = (action) => {
  const map = {
    'ACCEPT': '✅ 接受出价',
    'COUNTER': '💰 还价建议',
    'HOLD': '🤝 坚持底价',
    'REJECT': '❌ 拒绝出价'
  };
  return map[action] || '智能建议';
};

// 打开买家还价弹窗
const openBuyerCounterOffer = (msg) => {
  currentSellerCounterMsg.value = msg;
  // 提取卖家还价的价格作为默认值
  const sellerPrice = extractPrice(msg.content);
  buyerCounterPrice.value = sellerPrice ? parseFloat(sellerPrice) - 1 : 0; // 默认比卖家价格低1元
  showBuyerCounterDialog.value = true;
};

// 发送买家还价
const sendBuyerCounterOffer = async () => {
  if (!buyerCounterPrice.value || buyerCounterPrice.value <= 0) {
    showFailToast('请输入有效的价格');
    return;
  }
  
  const msg = currentSellerCounterMsg.value;
  const theItemId = (msg.item && msg.item.id) || msg.item_id || msg.itemId;
  
  if (!theItemId) {
    showFailToast('商品信息缺失，请刷新页面重试');
    return;
  }
  
  try {
    // 调用买家发起议价的API
    const res = await axios.post('/api/v1/bargain/offer', {
      item_id: theItemId,
      buyer_id: myId,
      offered_price: buyerCounterPrice.value
    });
    
    if (res.data.success) {
      // 发送议价消息到聊天
      const bargainMessage = `【议价申请】便宜点啦，${buyerCounterPrice.value}元可以不？`;
      socket.value.emit('send_msg', {
        senderId: myId,
        receiverId: friendId,
        content: bargainMessage,
        msg_type: '文本',
        item_id: theItemId,
        item: msg.item
      });
      
      // 本地添加消息
      list.value.push({
        id: Date.now(),
        senderId: myId,
        sender_id: myId,
        content: bargainMessage,
        msg_type: '文本',
        item_id: theItemId,
        item: msg.item,
        created_at: new Date()
      });
      scrollToBottom();
      
      showSuccessToast('还价已发送');
      showBuyerCounterDialog.value = false;
    } else {
      showFailToast(res.data.msg || '发送失败');
    }
  } catch (e) {
    console.error('买家还价失败:', e);
    showFailToast('发送失败，请重试');
  }
};

// 提取价格的辅助函数
const extractPrice = (content) => {
  if (!content) return null;
  // 匹配各种价格格式：65元、¥65、65.21元等
  const match = content.match(/(\d+\.?\d*)\s*元|¥\s*(\d+\.?\d*)/);
  return match ? (match[1] || match[2]) : null;
};

onMounted(async () => {
  await fetchHistory();

  socket.value = io('http://192.168.92.1:5011', {
    transports: ['websocket']
  });

  socket.value.on('connect', () => {
    console.log("Socket 已连接！");
    socket.value.emit('join', { myId: myId, friendId: friendId });
  });

  socket.value.on('new_msg', (msg) => {
    console.log("收到新消息:", msg);
    list.value.push(msg);
    scrollToBottom();
  });
});

onUnmounted(() => {
  if (socket.value) socket.value.disconnect();
});
</script>

<style scoped>
.chat-room { background: #f5f5f5; min-height: 100vh; display: flex; flex-direction: column; }
.msg-container { flex: 1; padding: 15px; overflow-y: auto; padding-bottom: 60px; }
.msg-row { display: flex; margin-bottom: 15px; align-items: flex-start; }
.msg-row.right { flex-direction: row-reverse; }
.avatar { width: 40px; height: 40px; background: #fff; border-radius: 4px; text-align: center; line-height: 40px; font-weight: bold; color: #333; flex-shrink: 0; }
.my-avatar { background: #a0e959; color: #000; }
.bubble { max-width: 70%; padding: 10px; border-radius: 4px; font-size: 14px; line-height: 1.4; position: relative; margin: 0 10px; word-wrap: break-word; }
.left .bubble { background: #fff; color: #333; }
.right .bubble { background: #95ec69; color: #000; }
.input-area { position: fixed; bottom: 0; left: 0; width: 100%; background: #f7f7f7; padding: 10px; display: flex; box-shadow: 0 -1px 4px rgba(0,0,0,0.05); }
.input-area input { flex: 1; height: 36px; border: none; border-radius: 4px; padding: 0 10px; margin-right: 10px; }
.input-area button { width: 60px; height: 36px; border: none; background: #07c160; color: #fff; border-radius: 4px; font-size: 14px; }
.input-area button:disabled { background: #ccc; }

.mini-item {
  display: flex;
  background: rgba(0,0,0,0.05);
  padding: 5px;
  border-radius: 4px;
  margin-bottom: 5px;
  cursor: pointer;
}
.mini-item img {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 8px;
}
.mini-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-size: 12px;
}
.mini-title {
  color: #333;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mini-price {
  color: #ff5000;
  font-weight: bold;
}

/* ⭐⭐⭐ 议价卡片样式 ⭐⭐⭐ */
.bargain-card { padding: 5px 0; }
.b-title { font-weight: bold; color: #ff5000; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px; font-size: 13px; }
.b-text { font-size: 13px; color: #333; margin-bottom: 8px; }
.b-actions { display: flex; justify-content: flex-end; margin-top: 5px; }
</style>