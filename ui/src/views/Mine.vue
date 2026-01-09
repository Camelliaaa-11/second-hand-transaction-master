<template>
  <div class="mine-page">
    <div class="user-card" @click="checkLogin">
      <div class="avatar-box">
        <div v-if="user" class="avatar">{{ user.username.charAt(0) }}</div>
        <div v-else class="avatar-placeholder">?</div>
      </div>
      <div class="info-box">
        <div v-if="user" class="name">
          {{ user.username }} 
          <van-tag type="primary" size="mini">信誉极好</van-tag>
        </div>
        <div v-else class="name-tip">点击登录/注册</div>
        <div v-if="user" class="uid">ID: {{ user.id }}</div>
      </div>
      <div class="setting-icon">
        <van-icon name="setting-o" size="20" />
        <span style="font-size: 12px; margin-left: 4px;">设置</span>
      </div>
    </div>

    <div class="stats-bar">
      <div class="stat-item" @click="goList('published')">
        <div class="num">{{ stats.published }}</div>
        <div class="label">我发布的</div>
      </div>
      <div class="stat-item" @click="goList('sold')">
        <div class="num">{{ stats.sold }}</div>
        <div class="label">我卖出的</div>
      </div>
      <div class="stat-item" @click="goList('bought')">
        <div class="num">{{ stats.bought }}</div>
        <div class="label">我买到的</div>
      </div>
      <div class="stat-item" @click="goList('favorites')">
        <div class="num">{{ stats.favorite }}</div>
        <div class="label">收藏</div>
      </div>
    </div>

    <div class="menu-group">
      <van-cell title="我的消息" icon="chat-o" is-link to="/message" />
      <van-cell title="收货地址" icon="location-o" is-link />
      <van-cell title="实名认证" icon="idcard" is-link value="已认证" />
      <van-cell title="帮助与反馈" icon="question-o" is-link />
    </div>
    
    <div v-if="user" style="margin: 20px 15px;">
      <van-button block type="default" @click="logout">退出登录</van-button>
    </div>

    <div style="height: 60px;"></div> <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated } from 'vue'; // ⭐ 引入 onActivated
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showToast, showConfirmDialog } from 'vant';
import TabBar from '../components/TabBar.vue';

const router = useRouter();
const user = ref(null);
const stats = ref({ published: 0, sold: 0, bought: 0, favorite: 0 });

// 从 localStorage 读取用户信息
const loadUser = () => {
  const s = localStorage.getItem('user');
  if (s) {
    user.value = JSON.parse(s);
    fetchStats(); // 有用户才去查统计
  } else {
    user.value = null;
    stats.value = { published: 0, sold: 0, bought: 0, favorite: 0 };
  }
};

// 向后端查询最新统计数据
const fetchStats = async () => {
  if (!user.value) return;
  try {
    // 加个时间戳 t 防止接口缓存
    const res = await axios.get(`/api/v1/user/stats/${user.value.id}?t=${Date.now()}`);
    if (res.data.success) {
      stats.value = res.data.data;
    }
  } catch (e) {
    console.error("统计获取失败", e);
  }
};

const checkLogin = () => {
  if (!user.value) router.push('/login');
};

const logout = () => {
  showConfirmDialog({ title: '提示', message: '确定要退出登录吗？' })
    .then(() => {
      localStorage.removeItem('user');
      user.value = null;
      stats.value = { published: 0, sold: 0, bought: 0, favorite: 0 };
      showToast('已退出');
      router.push('/login');
    })
    .catch(() => {});
};

const goList = (type) => {
  if (!user.value) return showToast('请先登录');
  // 跳转到列表页，这里假设你有这个路由，如果没有可以先不跳
  router.push(`/user/list?type=${type}`);
  // router.push(`/list?type=${type}`); // 以后可以做这个列表页
};

// ⭐⭐⭐ 核心修复：双重保险 ⭐⭐⭐
// 1. 第一次加载时运行
onMounted(() => {
  loadUser();
});

// 2. 每次页面重新显示时也运行 (专门解决从其他页面跳回来不刷新的问题)
onActivated(() => {
  loadUser();
});
</script>

<style scoped>
.mine-page { min-height: 100vh; background: #f7f8fa; }

/* 头部个人卡片 */
.user-card {
  background: #fff; padding: 30px 20px;
  display: flex; align-items: center;
  position: relative;
  margin-bottom: 10px;
}
.avatar-box { margin-right: 15px; }
.avatar { width: 60px; height: 60px; background: #07c160; border-radius: 50%; color: #fff; font-size: 24px; text-align: center; line-height: 60px; }
.avatar-placeholder { width: 60px; height: 60px; background: #eee; border-radius: 50%; color: #999; font-size: 30px; text-align: center; line-height: 60px; }
.info-box { flex: 1; }
.name { font-size: 20px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; }
.name-tip { font-size: 18px; font-weight: bold; color: #333; }
.uid { font-size: 12px; color: #999; }
.setting-icon { position: absolute; top: 20px; right: 20px; color: #999; display: flex; align-items: center; }

/* 统计栏 */
.stats-bar {
  background: #fff; padding: 20px 0;
  display: flex; justify-content: space-around;
  margin-bottom: 10px;
}
.stat-item { text-align: center; flex: 1; }
.stat-item:active { background: #f5f5f5; }
.num { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px; }
.label { font-size: 12px; color: #666; }

.menu-group { margin-bottom: 20px; }
</style>