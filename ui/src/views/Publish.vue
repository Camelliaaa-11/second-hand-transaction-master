<template>
  <div class="publish-page">
    <van-nav-bar title="发布闲置" />
    
    <div class="form-box">
      <div class="upload-area">
        <van-uploader v-model="fileList" :max-count="1" :after-read="afterRead" />
        <div class="upload-tip" v-if="fileList.length === 0">
          <van-icon name="photograph" size="24" color="#ccc" />
          <span>上传照片</span>
        </div>
      </div>

      <div class="ai-toolbar" v-if="fileList.length > 0">
        <van-button 
          type="primary" 
          size="small" 
          color="linear-gradient(to right, #ff6034, #ee0a24)"
          icon="magic-stick"
          round
          block
          :loading="aiLoading"
          loading-text="AI 正在观察..."
          @click="askAI"
        >
          ✨ AI 帮我写标题和描述
        </van-button>
        <div class="ai-tip">上传图片后，让 AI 帮你自动填写信息</div>
      </div>

      <van-cell-group inset style="margin-top: 10px;">
        <van-field
          v-model="title"
          label="标题"
          placeholder="品牌型号 / 关键信息"
          :rules="[{ required: true }]"
        />
        <van-field
          v-model="price"
          type="number"
          label="价格"
          placeholder="想卖多少钱"
          left-icon="gold-coin-o"
        />
        <van-field
          v-model="category"
          is-link
          readonly
          label="分类"
          placeholder="选择分类"
          @click="showPicker = true"
        />
        <van-popup v-model:show="showPicker" round position="bottom">
          <van-picker
            :columns="columns"
            @confirm="onConfirmCategory"
            @cancel="showPicker = false"
          />
        </van-popup>
        
        <van-field
          v-model="desc"
          rows="4"
          autosize
          label="描述"
          type="textarea"
          placeholder="描述一下宝贝的成色、入手渠道、转手原因..."
          show-word-limit
        />
        
        <van-cell center title="急售商品">
          <template #right-icon>
            <van-switch v-model="isUrgent" size="20" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="submit-btn">
        <van-button round block type="primary" @click="onSubmit" :loading="submitting">
          立即发布
        </van-button>
        
        <div style="height: 15px;"></div> <van-button round block plain type="default" @click="resetForm" icon="replay">
          重置 / 清空内容
        </van-button>
      </div>
    </div>
    
    <div style="height: 60px;"></div>
    <tab-bar />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
// ⭐ 引入 showConfirmDialog
import { showSuccessToast, showFailToast, showConfirmDialog } from 'vant';
import TabBar from '../components/TabBar.vue';

const router = useRouter();
const fileList = ref([]);
const title = ref('');
const price = ref('');
const desc = ref('');
const category = ref('');
const isUrgent = ref(false);
const submitting = ref(false);
const aiLoading = ref(false);

const showPicker = ref(false);
// 完整的 10 个分类
const columns = [
  { text: '电子数码', value: '电子数码' },
  { text: '书籍资料', value: '书籍资料' },
  { text: '生活用品', value: '生活用品' },
  { text: '服饰鞋包', value: '服饰鞋包' },
  { text: '美妆护肤', value: '美妆护肤' },
  { text: '运动器材', value: '运动器材' },
  { text: '乐器文玩', value: '乐器文玩' },
  { text: '代步工具', value: '代步工具' },
  { text: '虚拟商品', value: '虚拟商品' },
  { text: '其他', value: '其他' },
];

const onConfirmCategory = ({ selectedOptions }) => {
  category.value = selectedOptions[0].text;
  showPicker.value = false;
};

const afterRead = (file) => {
  console.log('图片已就绪');
};

const askAI = async () => {
  if (fileList.value.length === 0) return showFailToast('请先上传图片');
  
  aiLoading.value = true;
  try {
    const res = await axios.post('/api/v1/ai/generate', {
      image: fileList.value[0].content 
    });
    
    if (res.data.success) {
      const data = res.data.data;
      title.value = data.title;
      desc.value = data.desc;
      price.value = data.price;
      category.value = data.category;
      showSuccessToast('AI 填写完成！✨');
    } else {
      showFailToast(res.data.message);
    }
  } catch (e) {
    showFailToast('AI 请求失败');
  } finally {
    aiLoading.value = false;
  }
};

// ⭐⭐⭐ 新增：重置表单函数 ⭐⭐⭐
const resetForm = () => {
  showConfirmDialog({
    title: '确认重置',
    message: '确定要清空当前填写的所有内容吗？',
  })
    .then(() => {
      // 确认后清空所有变量
      title.value = '';
      price.value = '';
      desc.value = '';
      category.value = '';
      fileList.value = [];
      isUrgent.value = false;
      showSuccessToast('已清空');
    })
    .catch(() => {
      // 取消，什么都不做
    });
};

const onSubmit = async () => {
  if (!title.value || !price.value || !category.value) {
    return showFailToast('请填写完整信息');
  }
  if (fileList.value.length === 0) {
    return showFailToast('请上传一张图片');
  }

  const userStr = localStorage.getItem('user');
  if (!userStr) return showFailToast('请先登录');
  const user = JSON.parse(userStr);

  submitting.value = true;
  try {
    const res = await axios.post('/api/v1/items', {
      seller_id: user.id,
      title: title.value,
      price: price.value,
      category: category.value,
      description: desc.value,
      is_urgent_sale: isUrgent.value,
      image: fileList.value[0].content 
    });

    if (res.data.success) {
      showSuccessToast('发布成功！');
      
      // 发布成功后自动清空
      title.value = '';
      price.value = '';
      desc.value = '';
      category.value = '';
      fileList.value = [];
      
      setTimeout(() => router.push('/home'), 1000);
    } else {
      showFailToast(res.data.message);
    }
  } catch (e) {
    showFailToast('发布失败');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.publish-page { min-height: 100vh; background: #f7f8fa; padding-bottom: 20px; }
.form-box { padding: 15px; }
.upload-area { background: #fff; border-radius: 8px; padding: 20px; display: flex; justify-content: center; align-items: center; flex-direction: column; margin-bottom: 15px; border: 1px dashed #ddd; }
.upload-tip { display: flex; flex-direction: column; align-items: center; margin-top: 10px; color: #999; font-size: 12px; }

.ai-toolbar { margin-bottom: 15px; padding: 0 10px; text-align: center; }
.ai-tip { font-size: 10px; color: #999; margin-top: 5px; }

.submit-btn { margin-top: 30px; padding: 0 10px; }
</style>