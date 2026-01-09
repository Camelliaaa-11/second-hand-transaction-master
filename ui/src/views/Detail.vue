<template>
  <div class="detail-page">
    <AgentAdviceCard
      v-if="showAdvice"
      :show="showAdvice"
      :advice="advice"
      @adopt="onAdoptAdvice"
      @close="showAdvice = false"
    />
    <van-nav-bar title="商品详情" left-arrow @click-left="$router.back()" fixed placeholder />

    <div v-if="item">
      <div class="img-container">
        <img :src="item.img || item.image_data" alt="商品图片" />
        
        <div class="status-mask" v-if="item.status === '下架'">
          <span>已下架</span>
        </div>
      </div>

      <div class="info-card">
        <div class="price">¥{{ item.price }}</div>
        <div class="title">{{ item.title }}</div>
        <div class="meta">
          <van-tag plain type="primary" style="margin-right: 5px;">{{ item.category }}</van-tag>
          <van-tag v-if="item.status === '下架'" type="warning">商品已下架</van-tag>
          <span class="view-count" style="margin-left: auto;">{{ item.view || 0 }}人围观</span>
        </div>
        <div class="time-row">发布于 {{ item.create_time }}</div>
        
        <div class="desc-box">
          <div class="label">宝贝描述</div>
          <div class="content">{{ item.desc }}</div>
        </div>
      </div>

      <div class="seller-card" v-if="item.seller">
        <div class="seller-left">
          <div class="avatar">{{ item.seller.name.charAt(0) }}</div>
          <div class="seller-info">
            <div class="name">{{ item.seller.name }}</div>
            <div class="credit">信用极好 | 实名认证</div>
          </div>
        </div>
        <van-button 
          v-if="!isMe"
          size="small" 
          round 
          type="primary" 
          plain 
          @click="toChat"
        >
          私聊
        </van-button>
        <van-tag v-else type="success" size="medium">我发布的</van-tag>
      </div>

      <div class="review-card" id="review-section">
        <div class="review-header">
          <div class="label">留言 ({{ reviews.length }})</div>
        </div>

        <div v-for="r in reviews" :key="r.id" class="review-item">
          <div class="r-avatar">{{ (r.userName || r.user_name || '我').charAt(0) }}</div>
          <div class="r-content">
            <div class="r-top">
              <span class="r-name">{{ r.userName || r.user_name || '我' }}</span>
              <div class="r-right">
                <span class="r-time">{{ r.date }}</span>
                <van-icon 
                  v-if="canDelete(r)" 
                  name="delete-o" 
                  class="delete-btn" 
                  @click="handleDeleteReview(r)"
                />
              </div>
            </div>
            <div class="r-text">{{ r.content }}</div>
          </div>
        </div>
        <van-empty v-if="reviews.length === 0" description="还没有留言，点击底部按钮提问吧" />
      </div>
    </div> 
    
    <van-loading v-else size="24px" vertical style="padding-top: 100px;">加载中...</van-loading>

    <van-dialog v-model:show="showBargainDialog" title="发起砍价" show-cancel-button @confirm="sendBargain">
      <div style="padding: 20px;">
        <van-field
          v-model="bargainPrice"
          type="number"
          label="期望价格"
          placeholder="请输入您心里的价位"
          input-align="right"
        >
          <template #left-icon>¥</template>
        </van-field>
      </div>
    </van-dialog>

    <!-- 智能议价弹窗 -->
    <van-dialog 
      v-model:show="showSmartBargainDialog" 
      title="🤖 AI智能议价助手" 
      show-cancel-button 
      confirm-button-text="采纳建议"
      @confirm="adoptSmartAdvice"
      :before-close="onSmartDialogClose"
    >
      <div style="padding: 20px;">
        <van-loading v-if="loadingAdvice" size="24px">正在分析...</van-loading>
        
        <div v-else-if="smartAdvice">
          <!-- 建议策略标签 -->
          <van-tag 
            :type="getStrategyTagType(smartAdvice.strategy)" 
            size="large" 
            style="margin-bottom: 10px;"
          >
            {{ getStrategyText(smartAdvice.strategy) }}
          </van-tag>
          
          <!-- 推荐价格 -->
          <div style="margin: 15px 0;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">AI推荐报价</div>
            <div style="font-size: 28px; color: #ff5000; font-weight: bold;">
              ¥{{ smartAdvice.price }}
            </div>
          </div>
          
          <!-- AI建议话术 -->
          <div style="background: #f7f8fa; padding: 12px; border-radius: 8px; margin: 15px 0;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">💬 建议话术</div>
            <div style="font-size: 14px; color: #333; line-height: 1.6;">
              {{ smartAdvice.message }}
            </div>
          </div>
          
          <!-- AI分析理由 -->
          <div style="margin-top: 15px;">
            <div style="font-size: 12px; color: #999; margin-bottom: 5px;">🧠 策略分析</div>
            <div style="font-size: 13px; color: #666; line-height: 1.5;">
              {{ smartAdvice.reasoning }}
            </div>
          </div>
          
          <!-- 自定义调整 -->
          <van-field
            v-model="customPrice"
            type="number"
            label="微调价格"
            placeholder="也可以自己调整"
            input-align="right"
            style="margin-top: 15px;"
          >
            <template #left-icon>¥</template>
          </van-field>
        </div>
        
        <div v-else style="text-align: center; padding: 20px; color: #999;">
          未能获取智能建议
        </div>
      </div>
    </van-dialog>

    <van-action-bar placeholder style="z-index: 99;">
      <van-action-bar-icon icon="chat-o" text="看留言" @click="scrollToReviews" />
      <van-action-bar-icon 
        :icon="isFav ? 'star' : 'star-o'" 
        :text="isFav ? '已收藏' : '收藏'" 
        :color="isFav ? '#ff5000' : '#666'" 
        @click="toggleFav" 
      />
      <van-action-bar-icon 
        icon="guide-o" 
        text="智能议价" 
        color="#07c160"
        @click="openSmartBargain" 
        :disabled="!canBargain"
      />
      
      <van-action-bar-button 
        type="warning" 
        text="砍一刀" 
        @click="openBargain" 
        :disabled="!canBargain"
        color="#ff976a"
      />

      <van-action-bar-button 
        type="warning" 
        text="我要留言" 
        @click="toAddReview" 
      />
      
      <van-action-bar-button 
        :type="isMe ? 'default' : 'danger'" 
        :text="getBuyBtnText" 
        :disabled="isMe || (item && item.status === '下架')"
        @click="handleBuy" 
      />
    </van-action-bar>

  </div>
</template>

<script setup>

import { ref, computed, onMounted, onActivated } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast, showConfirmDialog, showToast } from 'vant';
import { getBuyerAdvice } from '../api/agent';
import AgentAdviceCard from '../components/AgentAdviceCard.vue';

const route = useRoute();
const router = useRouter();
const itemId = route.params.id;

const item = ref(null);
const reviews = ref([]);
const isFav = ref(false);
const showBargainDialog = ref(false);
const bargainPrice = ref('');

// 智能体建议相关
const showAdvice = ref(false);
const advice = ref({});

// 智能议价相关
const showSmartBargainDialog = ref(false);
const smartAdvice = ref(null);
const loadingAdvice = ref(false);
const customPrice = ref('');

// 议价状态
const hasActiveBargain = ref(false);
const activeBargainInfo = ref(null);

const isMe = computed(() => {
  const userStr = localStorage.getItem('user');
  if (!userStr || !item.value || !item.value.seller) return false;
  const me = JSON.parse(userStr);
  return String(me.id) === String(item.value.seller.id);
});

// 检查是否可以议价
const canBargain = computed(() => {
  return !isMe.value && 
         item.value && 
         item.value.status !== '下架' && 
         !hasActiveBargain.value;
});

// 计算购买按钮文字
const getBuyBtnText = computed(() => {
  if (isMe.value) return '我的商品';
  if (item.value && item.value.status === '下架') return '已下架';
  return '立即购买';
});

const canDelete = (review) => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return false;
  const me = JSON.parse(userStr);
  return String(review.userId) === String(me.id) || isMe.value;
};

const handleDeleteReview = (review) => {
  showConfirmDialog({ title: '提示', message: '确定要删除这条留言吗？' })
    .then(async () => {
      const userStr = localStorage.getItem('user');
      const user = JSON.parse(userStr);
      const res = await axios.post('/api/v1/reviews/delete', { review_id: review.id, user_id: user.id });
      if (res.data.success) {
        showSuccessToast('删除成功');
        fetchReviews();
      }
    }).catch(() => {});
};

// 检查议价状态
const checkBargainStatus = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return;
  
  // 确保商品信息已加载
  if (!item.value || !item.value.seller) return;
  
  // 如果是卖家自己，不需要检查
  const user = JSON.parse(userStr);
  if (String(user.id) === String(item.value.seller.id)) return;
  
  try {
    const res = await axios.post('/api/v1/bargain/check', {
      item_id: itemId,
      buyer_id: user.id
    });
    
    if (res.data.success) {
      hasActiveBargain.value = res.data.has_active_bargain;
      activeBargainInfo.value = res.data.bargain;
      
      if (hasActiveBargain.value) {
        console.log('已有进行中的议价:', activeBargainInfo.value);
      }
    }
  } catch (e) {
    console.error('检查议价状态失败:', e);
  }
};


const openBargain = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  
  // 检查是否有进行中的议价
  if (hasActiveBargain.value && activeBargainInfo.value) {
    showToast({
      message: `您已有进行中的议价（¥${activeBargainInfo.value.offered_price}），请到聊天界面继续协商`,
      position: 'top',
      duration: 3000
    });
    return;
  }
  
  // 优先弹出智能体建议卡片
  if (!item.value) {
    showFailToast('商品信息未加载，请稍后重试');
    return;
  }
  const data = {
    item_listed_price: item.value.price,
    market_avg_price: item.value.price, // 可根据实际传市场价
    buyer_profile: {},
    item_info: item.value,
    is_first: true
  };
  try {
    const res = await getBuyerAdvice(data);
    if (res) {
      advice.value = res;
      showAdvice.value = true;
      bargainPrice.value = '';
      return; // 只弹建议卡片
    } else {
      // 智能体建议失败，直接弹出手动砍价弹窗
      showToast('智能建议获取失败，您可以手动输入价格');
      showBargainDialog.value = true;
      bargainPrice.value = '';
    }
  } catch (e) {
    // 智能体建议失败，直接弹出手动砍价弹窗
    showToast('智能建议获取失败，您可以手动输入价格');
    showBargainDialog.value = true;
    bargainPrice.value = '';
  }
};

const onAdoptAdvice = (price, message) => {
  bargainPrice.value = price;
  showAdvice.value = false;
  showBargainDialog.value = true;
};

const sendBargain = async () => {
  if (!bargainPrice.value) return showFailToast('请输入价格');
  const userStr = localStorage.getItem('user');
  const user = JSON.parse(userStr);
  try {
    const res = await axios.post('/api/v1/bargain/offer', {
      item_id: itemId, buyer_id: user.id, price: bargainPrice.value
    });
    if (res.data.success) {
      showSuccessToast('砍价申请已发送！');
      // 重新检查议价状态
      await checkBargainStatus();
    } else {
      showFailToast(res.data.message);
    }
  } catch (e) { showFailToast('网络错误'); }
};

const fetchDetail = async () => {
  try {
    const t = Date.now();
    const res = await axios.get(`/api/v1/items/${itemId}?t=${t}`);
    if (res.data.success) {
      item.value = res.data.data;
      checkFav();
      fetchReviews();
      // 检查议价状态
      await checkBargainStatus();
    }
  } catch (e) { console.error(e); }
};

const fetchReviews = async () => {
  const t = Date.now(); 
  const res = await axios.get(`/api/v1/reviews/${itemId}?t=${t}`);
  if (res.data.success) reviews.value = res.data.data;
};

const checkFav = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return;
  const user = JSON.parse(userStr);
  const res = await axios.post('/api/v1/favorite/check', { userId: user.id, item_id: itemId });
  if (res.data.success) isFav.value = res.data.is_favorite;
};

const toggleFav = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  const user = JSON.parse(userStr);
  const res = await axios.post('/api/v1/favorite', { userId: user.id, item_id: itemId });
  if (res.data.success) {
    isFav.value = res.data.is_favorite;
    showSuccessToast(isFav.value ? '已收藏' : '取消收藏');
  }
};

const toAddReview = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  router.push(`/review/add/${itemId}`);
};

const toChat = () => {
  if (!item.value || !item.value.seller) return;
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  if (isMe.value) return;
  router.push({ path: `/chat/${item.value.seller.id}`, query: { name: item.value.seller.name } });
};

const handleBuy = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  if (isMe.value) return;
  router.push(`/order/${item.value.id}`);
};

const scrollToReviews = () => {
  const el = document.getElementById('review-section');
  if (el) el.scrollIntoView({ behavior: 'smooth' });
};

// 智能议价功能
const openSmartBargain = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    showFailToast('请先登录');
    return;
  }
  
  // 检查是否有进行中的议价
  if (hasActiveBargain.value && activeBargainInfo.value) {
    showToast({
      message: `您已有进行中的议价（¥${activeBargainInfo.value.offered_price}），请到聊天界面继续协商`,
      position: 'top',
      duration: 3000
    });
    return;
  }
  
  if (!item.value) {
    showFailToast('商品信息未加载，请稍后重试');
    return;
  }
  
  showSmartBargainDialog.value = true;
  loadingAdvice.value = true;
  smartAdvice.value = null;
  customPrice.value = '';
  
  try {
    const user = JSON.parse(userStr);
    const data = {
      user_id: user.id,
      item_id: itemId,
      item_listed_price: item.value.price,
      buyer_max_budget: item.value.price * 0.85, // 默认预算为标价的85%
      buyer_urgency: 3, // 默认紧迫度为3（中等）
      seller_id: item.value.seller?.id,
      item_category: item.value.category || '其他',
      item_condition: item.value.quality || '九成新'
    };
    
    const res = await axios.post('/api/agent/buyer-advice', data);
    
    if (res.data.code === 200 && res.data.data) {
      smartAdvice.value = res.data.data;
      customPrice.value = res.data.data.price;
    } else {
      showFailToast(res.data.message || '获取智能建议失败');
    }
  } catch (e) {
    console.error('获取智能议价建议失败:', e);
    showFailToast('网络错误，请稍后重试');
  } finally {
    loadingAdvice.value = false;
  }
};

const getStrategyTagType = (strategy) => {
  const map = {
    'AGGRESSIVE': 'danger',
    'MODERATE': 'warning',
    'SINCERE': 'success'
  };
  return map[strategy] || 'primary';
};

const getStrategyText = (strategy) => {
  const map = {
    'AGGRESSIVE': '🔥 激进策略',
    'MODERATE': '💼 温和策略',
    'SINCERE': '🤝 诚意策略'
  };
  return map[strategy] || '智能策略';
};

const adoptSmartAdvice = async () => {
  const finalPrice = customPrice.value || smartAdvice.value?.price;
  if (!finalPrice) {
    showFailToast('请输入价格');
    return;
  }
  
  const userStr = localStorage.getItem('user');
  const user = JSON.parse(userStr);
  
  try {
    const res = await axios.post('/api/v1/bargain/offer', {
      item_id: itemId, 
      buyer_id: user.id, 
      price: finalPrice
    });
    
    if (res.data.success) {
      showSuccessToast('智能议价申请已发送！');
      showSmartBargainDialog.value = false;
      // 重新检查议价状态
      await checkBargainStatus();
    } else {
      showFailToast(res.data.message);
    }
  } catch (e) {
    showFailToast('网络错误');
  }
};

const onSmartDialogClose = (action) => {
  if (action === 'cancel') {
    showSmartBargainDialog.value = false;
  }
  return true;
};

onMounted(() => {
  fetchDetail();
});

// 页面激活时重新检查议价状态（从聊天页面返回时）
onActivated(() => {
  fetchDetail();
});
// ...existing code...
</script>

<style scoped>
.detail-page { background: #f7f8fa; min-height: 100vh; padding-bottom: 60px; }
.img-container { width: 100%; height: 300px; background: #fff; position: relative; }
.img-container img { width: 100%; height: 100%; object-fit: contain; }

/* 下架遮罩样式 */
.status-mask {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
}
.status-mask span {
  color: #fff; font-size: 24px; font-weight: bold; border: 3px solid #fff;
  padding: 10px 20px; transform: rotate(-15deg); letter-spacing: 2px;
}

.info-card, .seller-card, .review-card { background: #fff; padding: 15px; margin-bottom: 10px; }
.price { color: #ff5000; font-size: 24px; font-weight: bold; }
.title { font-size: 18px; font-weight: bold; margin: 10px 0; line-height: 1.4; }
.meta { display: flex; align-items: center; font-size: 12px; margin-bottom: 10px; }
.time-row { font-size: 12px; color: #999; margin-bottom: 15px; }

.desc-box { background: #f9f9f9; padding: 10px; border-radius: 8px; }
.desc-box .label { font-weight: bold; margin-bottom: 5px; }
.desc-box .content { font-size: 14px; color: #666; line-height: 1.6; }

.seller-card { display: flex; align-items: center; justify-content: space-between; }
.seller-left { display: flex; align-items: center; }
.avatar { width: 40px; height: 40px; background: #1989fa; color: #fff; border-radius: 50%; text-align: center; line-height: 40px; font-size: 18px; margin-right: 10px; }
.name { font-weight: bold; }
.credit { font-size: 10px; color: #07c160; margin-top: 2px; }

.review-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-left: 8px; border-left: 4px solid #1989fa; }
.review-header .label { font-weight: bold; font-size: 16px; }

.review-item { display: flex; margin-bottom: 15px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
.r-avatar { width: 32px; height: 32px; background: #eee; border-radius: 50%; text-align: center; line-height: 32px; font-size: 12px; color: #666; margin-right: 10px; flex-shrink: 0; }
.r-content { flex: 1; }
.r-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
.r-name { color: #666; font-size: 12px; }
.r-right { display: flex; align-items: center; }
.r-time { color: #ccc; font-size: 12px; margin-right: 8px; }
.delete-btn { font-size: 16px; color: #999; cursor: pointer; }
.r-text { color: #333; font-size: 14px; line-height: 1.4; }
</style>