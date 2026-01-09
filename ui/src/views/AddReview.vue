<template>
  <div class="add-review-page">
    <van-nav-bar 
      title="写留言" 
      left-text="取消"
      left-arrow 
      @click-left="$router.back()" 
    />

    <div class="content">
      <div class="tip">对商品有什么疑问？问问卖家吧：</div>
      
      <van-field
        v-model="content"
        rows="5"
        autosize
        type="textarea"
        placeholder="请输入你想说的话..."
        show-word-limit
        maxlength="200"
        class="input-area"
      />

      <div style="height: 30px;"></div>

      <van-button 
        round 
        block 
        type="primary" 
        :loading="submitting" 
        loading-text="发送中..."
        @click="onSubmit"
      >
        发送留言
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
// ⭐ 改动1：引入具体的 showToast 函数，兼容性更强
import { showSuccessToast, showFailToast, showToast } from 'vant';
// ⭐ 改动2：引入样式，防止因为没样式而弹不出来
import 'vant/es/toast/style'; 

const route = useRoute();
const router = useRouter();
const itemId = route.params.id;
const content = ref('');
const submitting = ref(false);

const onSubmit = async () => {
  if (!content.value.trim()) {
    showToast('写点什么吧');
    return;
  }
  
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    showFailToast('请先登录');
    return;
  }
  const user = JSON.parse(userStr);

  submitting.value = true;

  try {
    const res = await axios.post('/api/v1/reviews', {
      item_id: itemId,
      userId: user.id,
      content: content.value
    });

    // 只要后端返回 success: true
    if (res.data.success) {
      // ⭐ 改动3：使用 showSuccessToast
      showSuccessToast('发送成功！');
      content.value = ''; 
      
      // 延迟 1秒 返回
      setTimeout(() => {
        router.back(); 
      }, 1000);

    } else {
      showFailToast(res.data.message || '发送失败');
    }
  } catch (e) {
    console.error('留言报错:', e);
    showFailToast('网络错误');
  } finally {
    // 无论如何停止转圈
    submitting.value = false;
  }
};
</script>

<style scoped>
.add-review-page { min-height: 100vh; background: #f7f8fa; }
.content { padding: 20px; }
.tip { margin-bottom: 15px; color: #666; font-size: 14px; }
.input-area { border-radius: 8px; padding: 15px; background: #fff; }
</style>