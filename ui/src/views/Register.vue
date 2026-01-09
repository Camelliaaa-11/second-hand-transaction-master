<template>
  <div class="auth-page">
    <van-nav-bar title="注册新账号" left-arrow @click-left="$router.back()" />
    
    <div class="logo-area">
      <h3>创建账号</h3>
    </div>

    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="用户名"
          placeholder="起个好听的名字"
          :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
          v-model="phone"
          name="phone"
          label="手机号"
          placeholder="用于联系买家"
          :rules="[{ required: true, message: '请填写手机号' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="设置登录密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>
      <div style="margin: 30px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          立即注册
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showSuccessToast, showFailToast } from 'vant';
import axios from 'axios';

const router = useRouter();
const username = ref('');
const password = ref('');
const phone = ref('');
const loading = ref(false);

const onSubmit = async () => {
  loading.value = true;
  try {
    const res = await axios.post('http://localhost:5011/api/v1/register', {
      username: username.value,
      password: password.value,
      phone: phone.value
    });
    
    if (res.data.success) {
      showSuccessToast('注册成功，请登录');
      setTimeout(() => router.replace('/login'), 1000);
    } else {
      showFailToast(res.data.message);
    }
  } catch (error) {
    showFailToast('注册失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page { height: 100vh; background: #fff; }
.logo-area { text-align: center; padding: 30px 0; }
</style>