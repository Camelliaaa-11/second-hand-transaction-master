<template>
  <div class="login-container">
    <div class="logo-area">
      <div class="logo-box">二手</div>
      <h2>欢迎回来</h2>
    </div>

    <div class="form-area">
      <van-field
        v-model="username"
        placeholder="请输入用户名"
        label="用户名"
        left-icon="manager-o"
      />
      <van-field
        v-model="password"
        type="password"
        placeholder="请输入密码"
        label="密码"
        left-icon="lock"
      />
      
      <div class="btn-area">
        <van-button round block type="primary" @click="handleLogin" :loading="loading">
          登录
        </van-button>
        <div class="links">
          <span @click="$router.push('/register')">没有账号？去注册</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast } from 'vant';

const router = useRouter();
const username = ref('');
const password = ref('');
const loading = ref(false);

const handleLogin = async () => {
  if (!username.value || !password.value) {
    showFailToast('请输入用户名和密码');
    return;
  }

  loading.value = true;
  try {
    // 调用后端登录接口
    const res = await axios.post('/api/v1/login', {
      username: username.value,
      password: password.value
    });

    if (res.data.success) {
      showSuccessToast('登录成功');
      
      // ⭐【关键修改】这里必须把整个 data 存成一个叫 'user' 的 JSON 字符串
      // 这样 Mine.vue 才能读到它！
      localStorage.setItem('user', JSON.stringify(res.data.data));

      // 稍微延迟一下跳转，体验更好
      setTimeout(() => {
        router.push('/home'); // 登录完去首页
      }, 500);
    } else {
      showFailToast(res.data.message || '登录失败');
    }
  } catch (error) {
    console.error(error);
    showFailToast('连接服务器失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container { padding: 40px 20px; background: #fff; min-height: 100vh; }
.logo-area { text-align: center; margin-bottom: 40px; margin-top: 40px; }
.logo-box { width: 60px; height: 60px; background: #1989fa; border-radius: 12px; color: #fff; line-height: 60px; font-size: 24px; font-weight: bold; margin: 0 auto 15px; }
.form-area { margin-top: 20px; }
.btn-area { margin-top: 40px; padding: 0 10px; }
.links { margin-top: 15px; text-align: center; font-size: 14px; color: #1989fa; cursor: pointer; }
</style>