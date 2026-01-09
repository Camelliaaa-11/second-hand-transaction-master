<template>
  <div class="home-page">
    <div class="search-header">
      <van-search 
        v-model="searchText" 
        shape="round" 
        background="#fff" 
        placeholder="搜iPhone / 教材 / 鼠标" 
        show-action
      >
        <template #action>
          <div @click="onSearch" class="search-btn">搜索</div>
        </template>
      </van-search>
    </div>

    <van-tabs v-model:active="activeTab" sticky @click-tab="onClickTab">
  <van-tab 
    v-for="item in categories" 
    :key="item.type" 
    :title="item.name"
  >
    </van-tab>
</van-tabs>

    <div class="goods-list-container">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        
        <van-empty 
          v-if="filteredItems.length === 0" 
          :description="searchText ? '没找到呀，换个词试试？' : '这里空空如也'" 
          image="search" 
        />

        <div class="goods-grid">
          <div 
            class="goods-card" 
            v-for="item in filteredItems" 
            :key="item.id"
            @click="goToDetail(item.id)"
          >
            <div class="img-box">
              <img :src="item.img || 'https://fastly.jsdelivr.net/npm/@vant/assets/apple-1.jpeg'" alt="商品图片" />
              <div class="view-tag" v-if="item.isUrgent">急售</div>
            </div>
            
            <div class="info-box">
              <div class="title" v-html="highlightTitle(item.title)"></div>
              
              <div class="tags-row">
                <van-tag plain round color="#1989fa">{{ item.category }}</van-tag>
                <span class="views">{{ item.view || 0 }}人看过</span>
              </div>
              
              <div class="bottom-row">
                <div class="price-box">
                  <span class="symbol">¥</span>
                  <span class="price">{{ item.price }}</span>
                </div>
                <div class="seller-box">
                  <van-icon name="manager-o" />
                  <span class="seller-name">{{ item.seller || '未知' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </van-pull-refresh>
    </div>

    <div style="height: 60px;"></div>

    <TabBar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import TabBar from '../components/TabBar.vue';

// ⭐⭐ 关键修复：显式引入 Vant 组件，防止不显示！ ⭐⭐
import { Search, Tab, Tabs, PullRefresh, Empty, Tag, Icon } from 'vant';

const router = useRouter();
const searchText = ref('');
const activeTab = ref(0); 
const refreshing = ref(false);
const items = ref([]); 

const categories = [
  { name: '全部', type: 'all' },
  { name: '电子数码', type: '电子数码' },
  { name: '书籍资料', type: '书籍资料' },
  { name: '生活用品', type: '生活用品' },
  { name: '服饰鞋包', type: '服饰鞋包' }, // ✅ 新增
  { name: '美妆护肤', type: '美妆护肤' },
  { name: '运动器材', type: '运动器材' },
  { name: '乐器文玩', type: '乐器文玩' }, // ✅ 新增
  { name: '代步工具', type: '代步工具' }, // ✅ 新增
  { name: '虚拟商品', type: '虚拟商品' },
  { name: '其他', type: '其他' },
];

// 过滤逻辑
// ui/src/views/Home.vue

const filteredItems = computed(() => {
  let res = items.value;
  // 1. 分类筛选
  if (activeTab.value !== 0) {
    const targetCat = categories[activeTab.value];
    
    // 👇👇👇 核心修改在这里 👇👇👇
    // 原来是: item.category === targetCat
    // 改成: targetCat.name
    res = res.filter(item => item.category === targetCat.name);
  }
  // 2. 搜索筛选
  if (searchText.value) {
    const key = searchText.value.toLowerCase();
    res = res.filter(item => item.title.toLowerCase().includes(key));
  }
  return res;
});

const fetchData = async () => {
  try {
    const res = await axios.get('/api/v1/items');
    if (res.data.success) {
      items.value = res.data.data;
    }
  } catch (error) { console.error(error); } 
  finally { refreshing.value = false; }
};

const onSearch = () => {
  console.log("点击了搜索:", searchText.value);
};

// 标题高亮逻辑
const highlightTitle = (title) => {
  if (!searchText.value) return title;
  const key = searchText.value;
  return title.replace(new RegExp(key, 'gi'), `<span style="color: #ff5000; font-weight:bold;">$&</span>`);
};

const onRefresh = () => fetchData();
const goToDetail = (id) => router.push(`/detail/${id}`);

onMounted(() => fetchData());
</script>

<style scoped>
.home-page { background: #f2f4f7; min-height: 100vh; }
/* 给头部加个白色背景和层级，确保它不会被遮住 */
.search-header { 
  position: sticky; 
  top: 0; 
  z-index: 100; 
  background: #fff; 
  box-shadow: 0 1px 4px rgba(0,0,0,0.05); 
}

.search-btn {
  color: #1989fa;
  font-weight: bold;
  padding: 0 10px;
  cursor: pointer;
}
.search-btn:active { opacity: 0.7; }

.goods-list-container { padding: 10px; }

.goods-grid { 
  display: grid; 
  grid-template-columns: repeat(2, 1fr); 
  gap: 10px; 
  width: 100%; 
}

/* ui/src/views/Home.vue */

/* ... 前面的样式不变 ... */

.goods-card { 
  background: #fff; 
  border-radius: 12px; 
  overflow: hidden; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); 
  display: flex; 
  flex-direction: column; 
  width: 100%; 
}

/* 👇👇👇 重点改这里 👇👇👇 */
.img-box { 
  width: 100%; 
  height: 170px; 
  position: relative; 
  background: #fff; /* 改成白色背景，这样图片留白时最好看 */
  display: flex;    /* 加上 flex 布局 */
  align-items: center; /* 让图片垂直居中 */
  justify-content: center; /* 让图片水平居中 */
}

.img-box img { 
  width: 100%; 
  height: 100%; 
  object-fit: contain; /* ⭐ 核心修改：从 cover 改成 contain，确保图片完整显示 */
  display: block;
}
/* 👆👆👆 改动结束 👆👆👆 */

.view-tag { position: absolute; top: 0; left: 0; background: linear-gradient(135deg, #ff5000, #ff8c00); color: #fff; font-size: 10px; padding: 4px 8px; border-radius: 12px 0 12px 0; }

/* ... 后面的样式不变 ... */

.info-box { padding: 10px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

.tags-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.views { font-size: 11px; color: #999; }

.bottom-row { display: flex; align-items: flex-end; justify-content: space-between; }
.price-box { color: #ff5000; font-weight: bold; }
.symbol { font-size: 12px; }
.price { font-size: 18px; }
.seller-box { font-size: 11px; color: #bbb; display: flex; align-items: center; }
.seller-name { max-width: 60px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; margin-left: 2px; }
</style>