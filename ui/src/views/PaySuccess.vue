<template>
  <div class="success-page">
    <van-nav-bar title="支付结果" />
    
    <div class="content">
      <div class="icon-box">
        <van-icon name="checked" color="#07c160" size="80" />
      </div>
      <div class="title">支付成功</div>
      <div class="desc">卖家将尽快为您发货</div>

      <div class="btn-group">
        <van-button type="primary" block round @click="goMine">
          查看我的订单
        </van-button>
        
        <div style="height: 15px;"></div>
        
        <van-button plain block round @click="$router.push('/')">
          返回首页
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goMine = () => {
  // 这里跳转到 'My' 或者 'Mine'，确保跳到个人中心
  // 如果你的路由名是 Mine，这里会自动匹配
  router.replace('/mine'); 
};
</script>

<style scoped>
.success-page { min-height: 100vh; background: #fff; }
.content { padding-top: 50px; text-align: center; }
.icon-box { margin-bottom: 20px; }
.title { font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px; }
.desc { font-size: 14px; color: #999; margin-bottom: 50px; }
.btn-group { padding: 0 40px; }
</style>