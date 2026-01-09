<template>
  <div class="settings-page">
    <van-nav-bar title="账号设置" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="form-group">
      <div class="avatar-section">
        <input type="file" ref="hiddenInput" accept="image/*" style="display: none" @change="handleFileChange" />
        
        <div class="avatar-wrapper" @click="triggerUpload">
          <img :src="currentAvatar" class="avatar-img" />
          <div class="camera-icon"><van-icon name="photograph" /></div>
        </div>
        <div class="tip">点击头像更换</div>
      </div>

      <van-cell-group inset>
        <van-field 
          v-model="username" 
          label="昵称" 
          placeholder="请输入新昵称" 
          input-align="right" 
        />
        
        <van-field 
          v-model="phone" 
          label="手机号" 
          placeholder="请输入手机号"
          type="tel"
          input-align="right" 
        />
        
        <van-field 
          v-model="password" 
          label="新密码" 
          type="password" 
          placeholder="不改请留空" 
          input-align="right" 
        />
      </van-cell-group>
    </div>

    <div style="margin: 30px 16px;">
      <van-button round block type="primary" @click="onSave">保存修改</van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { showSuccessToast } from 'vant';
import { useRouter } from 'vue-router';

const router = useRouter();
const hiddenInput = ref(null);

// 默认值
const currentAvatar = ref('https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg');
const username = ref('李晨');
const phone = ref('17731882550'); // 默认手机号
const password = ref('');

// ⭐ 进页面时，读取所有保存的数据（包括手机号）
onMounted(() => {
  const savedName = localStorage.getItem('userName');
  const savedAvatar = localStorage.getItem('userAvatar');
  const savedPhone = localStorage.getItem('userPhone'); // 读取手机号
  
  if (savedName) username.value = savedName;
  if (savedAvatar) currentAvatar.value = savedAvatar;
  if (savedPhone) phone.value = savedPhone; // 覆盖默认手机号
});

// 上传头像逻辑
const triggerUpload = () => hiddenInput.value.click();
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (e) => currentAvatar.value = e.target.result;
  }
};

// ⭐ 保存逻辑：把手机号也存进去
const onSave = () => {
  localStorage.setItem('userName', username.value);
  localStorage.setItem('userAvatar', currentAvatar.value);
  localStorage.setItem('userPhone', phone.value); // 保存手机号
  
  showSuccessToast('保存成功！');
  setTimeout(() => router.back(), 1000);
};
</script>

<style scoped>
.settings-page { background: #f7f8fa; min-height: 100vh; }
.form-group { margin-top: 10px; }
.avatar-section { display: flex; flex-direction: column; align-items: center; background: #fff; padding: 30px 0; margin-bottom: 10px; }
.avatar-wrapper { position: relative; width: 80px; height: 80px; margin-bottom: 10px; cursor: pointer; }
.avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 2px solid #f2f3f5; }
.camera-icon { position: absolute; bottom: 0; right: 0; background: #1989fa; color: #fff; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #fff; }
.tip { font-size: 12px; color: #999; }
</style>