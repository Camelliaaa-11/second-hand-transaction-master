<template>
  <van-tabbar v-model="active" route fixed placeholder>
    <van-tabbar-item replace to="/home" icon="home-o">首页</van-tabbar-item>
    <van-tabbar-item replace to="/publish" icon="plus">发布</van-tabbar-item>
    
    <van-tabbar-item 
      replace 
      to="/chat" 
      icon="chat-o" 
      :badge="unreadCount > 0 ? unreadCount : null"
    >
      消息
    </van-tabbar-item>
    
    <van-tabbar-item replace to="/mine" icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const active = ref(0);
const unreadCount = ref(0);
let timer = null;

// 查询未读数量
const checkUnread = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    unreadCount.value = 0;
    return;
  }
  const user = JSON.parse(userStr);
  
  try {
    const res = await axios.get(`/api/v1/messages/unread_count?userId=${user.id}`);
    if (res.data.success) {
      unreadCount.value = res.data.count;
    }
  } catch (e) {
    console.error("获取红点失败", e);
  }
};

onMounted(() => {
  checkUnread();
  // ⭐ 每 3 秒轮询一次，保证红点及时更新
  timer = setInterval(checkUnread, 3000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>