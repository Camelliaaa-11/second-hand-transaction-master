<template>
  <div class="message-page">
    <van-nav-bar title="消息" fixed placeholder :border="false" />
    
    <van-list>
      <van-empty v-if="list.length === 0" description="暂无消息" />
      
      <div 
        class="chat-item" 
        v-for="item in list" 
        :key="item.id"
        @click="toChat(item)"
      >
        <div class="avatar">
          <img v-if="item.avatar" :src="item.avatar" />
          <div v-else class="avatar-text">{{ item.name.charAt(0) }}</div>
        </div>
        
        <div class="content">
          <div class="top-row">
            <span class="name">{{ item.name }}</span>
            <span class="time">{{ item.time }}</span>
          </div>
          <div class="msg-text">{{ item.last_msg }}</div>
        </div>
      </div>
    </van-list>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import TabBar from '../components/TabBar.vue';

const router = useRouter();
const list = ref([]);

// 获取消息列表
const fetchMessages = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return; 
  const user = JSON.parse(userStr);

  try {
    const res = await axios.get(`/api/v1/my/messages?userId=${user.id}`);
    if (res.data.success) {
      list.value = res.data.data;
    }
  } catch (e) {
    console.error("获取消息失败", e);
  }
};

// ⭐⭐ 核心修复：点击跳转到聊天页 ⭐⭐
const toChat = (friend) => {
  console.log("准备跳转到聊天:", friend.name);
  router.push({
    path: `/chat/${friend.id}`,
    query: { name: friend.name }
  });
};

onMounted(() => {
  fetchMessages();
});
</script>

<style scoped>
.message-page { background: #fff; min-height: 100vh; padding-bottom: 50px; }
.chat-item { display: flex; padding: 15px; border-bottom: 1px solid #f5f5f5; cursor: pointer; }
.chat-item:active { background: #f9f9f9; }
.avatar { width: 50px; height: 50px; margin-right: 15px; position: relative; }
.avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
.avatar-text { width: 100%; height: 100%; background: #1989fa; color: #fff; border-radius: 50%; text-align: center; line-height: 50px; font-size: 20px; }
.content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.top-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.name { font-weight: bold; font-size: 16px; color: #333; }
.time { font-size: 12px; color: #999; }
.msg-text { font-size: 14px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 260px; }
</style>