import { createRouter, createWebHistory } from 'vue-router'

// 引入页面组件
import Home from '../views/Home.vue'
import Publish from '../views/Publish.vue'
import Detail from '../views/Detail.vue'
import Mine from '../views/Mine.vue'
import MessageList from '../views/MessageList.vue'
import Chat from '../views/Chat.vue'
import Settings from '../views/Settings.vue'
import UserList from '../views/UserList.vue'
import Login from '../views/Login.vue'    
import Register from '../views/Register.vue'
import Order from '../views/Order.vue'
import AddReview from '../views/AddReview.vue'
import PaySuccess from '../views/PaySuccess.vue'

const routes = [
  { path: '/', redirect: '/home' },

  { path: '/login', component: Login, meta: { title: '用户登录' } },
  { path: '/register', component: Register, meta: { title: '注册账号' } },

  { path: '/home', component: Home, meta: { title: '闲置平台' } },
 { 
  path: '/publish', 
  component: Publish, 
  meta: { 
    title: '发布闲置',
    keepAlive: true  // 👈 加上这句！表示这个页面要“活着”
  } 
},
  
  // ✅ 修复1：个人中心改回 /mine (配合底部导航栏)
  { path: '/mine', component: Mine, meta: { title: '个人中心' } },

  // ✅ 修复2：消息列表改回 /chat (配合底部导航栏)
  // 同时给它加个别名 /message，这样 Mine.vue 里的链接也能用
  { 
    path: '/chat', 
    alias: '/message', 
    component: MessageList, 
    meta: { title: '消息列表' } 
  },

  { path: '/chat/:id', component: Chat, meta: { title: '聊天详情' } },

  { path: '/detail/:id', component: Detail, meta: { title: '商品详情' } },
  { path: '/settings', component: Settings, meta: { title: '账号设置' } },
  { path: '/user/list', component: UserList, meta: { title: '我的列表' } },
  
  { path: '/order/:id', name: 'Order', component: Order },
  
  { path: '/review/add/:id', name: 'AddReview', component: AddReview },
  
  { path: '/pay/success', name: 'PaySuccess', component: PaySuccess },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router