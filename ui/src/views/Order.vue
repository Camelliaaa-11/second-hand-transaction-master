<template>
  <div class="order-page">
    <van-nav-bar title="确认订单" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="address-card">
      <div class="left-icon">
        <van-icon name="location-o" size="20" />
      </div>
      <div class="info">
        <div class="user-info">
          <span class="name">李同学</span>
          <span class="phone">138****0000</span>
        </div>
        <div class="addr-text">深圳技术大学 宿舍区 (默认地址)</div>
      </div>
      <van-icon name="arrow" color="#999" />
    </div>

    <div class="item-card" v-if="item">
      <div class="thumb">
        <img :src="item.img" alt="" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">
      </div>
      <div class="info">
        <div class="title">{{ item.title }}</div>
        <div class="price">¥ {{ item.price }}</div>
        <div class="desc">{{ item.desc }}</div>
      </div>
    </div>

    <div style="margin: 20px 15px;">
      <van-button type="primary" block round @click="onSubmit">
        备用支付按钮
      </van-button>
    </div>

    <div class="fixed-bottom-bar">
      <div class="price-box">
        合计：<span class="total-price">¥{{ item ? item.price : '0.00' }}</span>
      </div>
      <van-button 
        type="danger" 
        round 
        @click="onSubmit"
        :loading="submitting"
        style="width: 120px;"
      >
        立即支付
      </van-button>
    </div>

    <div style="height: 80px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast } from 'vant';
import 'vant/es/toast/style';

const route = useRoute();
const router = useRouter();
const itemId = route.params.id;
const item = ref(null);
const submitting = ref(false);

const fetchItem = async () => {
  try {
    const res = await axios.get(`/api/v1/items/${itemId}`);
    if (res.data.success) {
      item.value = res.data.data;
    } else {
      showFailToast('商品信息获取失败');
    }
  } catch (e) {
    showFailToast('网络错误');
  }
};

const onSubmit = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  const user = JSON.parse(userStr);

  submitting.value = true;

  try {
    await new Promise(resolve => setTimeout(resolve, 800)); // 模拟支付

    const res = await axios.post('/api/v1/orders/create', {
      item_id: itemId,
      buyer_id: user.id,
      address: '深圳技术大学 宿舍区'
    });

    // ui/src/views/Order.vue 中的 onSubmit 函数

    if (res.data.success) {
      showSuccessToast('支付成功！');
      
      // ⭐⭐⭐ 核心修改：跳到支付成功页 ⭐⭐⭐
      setTimeout(() => {
        router.replace('/pay/success'); 
      }, 500);

    } else {
      showFailToast(res.data.message || '支付失败');
    }
  } catch (e) {
    console.error(e);
    showFailToast('支付出错');
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchItem();
});
</script>

<style scoped>
.order-page { min-height: 100vh; background: #f7f8fa; }

.address-card {
  background: #fff; margin: 10px; padding: 15px; border-radius: 8px;
  display: flex; align-items: center;
}
.left-icon {
  width: 30px; height: 30px; background: #1989fa; border-radius: 50%;
  color: #fff; display: flex; justify-content: center; align-items: center; margin-right: 10px;
}
.info { flex: 1; }
.user-info { font-weight: bold; margin-bottom: 5px; }
.addr-text { font-size: 13px; color: #666; }

.item-card {
  background: #fff; margin: 10px; padding: 15px; border-radius: 8px;
  display: flex;
}
.thumb { width: 80px; height: 80px; background: #eee; border-radius: 4px; margin-right: 10px; }
.info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.title { font-weight: bold; font-size: 16px; }
.price { color: #ff5000; font-size: 18px; font-weight: bold; margin: 5px 0; }
.desc { font-size: 12px; color: #999; }

/* 强制固定底部栏 */
.fixed-bottom-bar {
  position: fixed; left: 0; bottom: 0; width: 100%; height: 60px;
  background: #fff; border-top: 1px solid #eee;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 15px; box-sizing: border-box; z-index: 9999;
}
.price-box { font-size: 14px; }
.total-price { color: #ff5000; font-size: 20px; font-weight: bold; }
</style>