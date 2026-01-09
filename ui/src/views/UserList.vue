<template>
  <div class="user-list-page">
    <van-nav-bar :title="pageTitle" left-arrow @click-left="$router.back()" fixed placeholder />

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div v-if="listType === 'published' || listType === 'favorites'" class="list-box">
          <div 
            v-for="item in list" 
            :key="item.id" 
            class="item-card"
            @click="router.push(`/detail/${item.id}`)"
          >
            <div class="img-box">
              <img :src="item.img_data" />
            </div>
            <div class="info-box">
              <div class="title">{{ item.title }}</div>
              <div class="price">¥ {{ item.price }}</div>
              
              <div class="status-tag">
                <van-tag v-if="item.status === '上架'" type="success">出售中</van-tag>
                <van-tag v-else-if="item.status === '下架'" type="warning">已下架</van-tag>
                <van-tag v-else type="danger">{{ item.status }}</van-tag>
              </div>

              <div class="action-btns" v-if="listType === 'published'">
                <van-button 
                  v-if="item.status === '上架'" 
                  size="mini" 
                  type="warning" 
                  round 
                  plain
                  @click.stop="toggleStatus(item, '下架')"
                >
                  下架
                </van-button>

                <van-button 
                  v-if="item.status === '下架'" 
                  size="mini" 
                  type="primary" 
                  round 
                  plain
                  @click.stop="toggleStatus(item, '上架')"
                >
                  上架
                </van-button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="list-box">
          <div v-for="order in list" :key="order.id" class="order-card">
            <div class="order-header">
              <span class="time">{{ order.time }}</span>
              <span class="status">{{ order.status }}</span>
            </div>
            <div class="order-body" @click="router.push(`/detail/${order.item_id}`)">
              <div class="o-img"><img :src="order.item_img" /></div>
              <div class="o-info">
                <div class="o-title">{{ order.item_title }}</div>
                <div class="o-price">成交价: ¥{{ order.price }}</div>
              </div>
            </div>
          </div>
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { showFailToast, showSuccessToast, showConfirmDialog } from 'vant';

const route = useRoute();
const router = useRouter();
const listType = route.query.type; 

const list = ref([]);
const loading = ref(false);
const finished = ref(false);
const refreshing = ref(false);

const pageTitle = computed(() => {
  const map = {
    published: '我发布的',
    sold: '我卖出的',
    bought: '我买到的',
    favorites: '我的收藏'
  };
  return map[listType] || '列表';
});

const onLoad = async () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return;
  const user = JSON.parse(userStr);

  try {
    const res = await axios.post('/api/v1/user/common_list', {
      user_id: user.id,
      type: listType
    });

    if (res.data.success) {
      if (refreshing.value) {
        list.value = [];
        refreshing.value = false;
      }
      list.value = res.data.data;
      finished.value = true;
    } else {
      showFailToast(res.data.message);
      finished.value = true;
    }
  } catch (e) {
    finished.value = true;
  } finally {
    loading.value = false;
  }
};

const onRefresh = () => {
  finished.value = false;
  loading.value = true;
  onLoad();
};

// ⭐⭐⭐ 新增：切换上下架状态 ⭐⭐⭐
const toggleStatus = (item, newStatus) => {
  const actionName = newStatus === '下架' ? '下架' : '重新上架';
  
  showConfirmDialog({
    title: '提示',
    message: `确定要${actionName}这个商品吗？\n${newStatus === '下架' ? '下架后首页将不再显示。' : '上架后将重新展示在首页。'}`
  }).then(async () => {
    try {
      const res = await axios.post('/api/v1/items/status', {
        item_id: item.id,
        status: newStatus
      });
      if (res.data.success) {
        showSuccessToast('操作成功');
        // 修改本地显示的状态，不用刷新页面
        item.status = newStatus;
      } else {
        showFailToast(res.data.message);
      }
    } catch (e) {
      showFailToast('网络错误');
    }
  }).catch(() => {});
};
</script>

<style scoped>
.user-list-page { min-height: 100vh; background: #f7f8fa; padding-top: 10px; }
.list-box { padding: 0 10px; }

/* 商品卡片样式 */
.item-card {
  background: #fff; border-radius: 8px; padding: 10px; margin-bottom: 10px;
  display: flex; position: relative;
}
.img-box { width: 90px; height: 90px; margin-right: 10px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.img-box img { width: 100%; height: 100%; object-fit: cover; }
.info-box { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.title { font-size: 15px; font-weight: bold; margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.price { color: #ff5000; font-size: 16px; font-weight: bold; }

/* 状态标签和按钮位置 */
.status-tag { margin-top: 5px; }
.action-btns { position: absolute; right: 10px; bottom: 10px; }

/* 订单卡片样式 */
.order-card { background: #fff; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
.order-header { display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
.status { color: #ff5000; }
.order-body { display: flex; }
.o-img { width: 70px; height: 70px; background: #f0f0f0; margin-right: 10px; border-radius: 4px; overflow: hidden; }
.o-img img { width: 100%; height: 100%; object-fit: cover; }
.o-info { flex: 1; }
.o-title { font-size: 14px; font-weight: bold; margin-bottom: 5px; }
.o-price { color: #333; font-size: 13px; }
</style>