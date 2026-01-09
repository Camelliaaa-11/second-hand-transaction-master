import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'vant/lib/index.css' // 样式必须有

import { 
  Button, NavBar, Form, Field, CellGroup, Icon, Uploader, Popup, Picker, 
  Tab, Tabs, Card, Tag, Empty, PullRefresh, Loading, 
  ActionBar, ActionBarIcon, ActionBarButton, Dialog, 
  Rate, // ⭐ 你原来的星星
  Tabbar, TabbarItem,
  // 👇👇👇 必须补上这俩，否则搜索栏和列表页都会崩！
  Search, 
  List
} from 'vant';

const app = createApp(App)
app.use(router)

// 注册组件
app.use(Button).use(NavBar).use(Form).use(Field).use(CellGroup)
   .use(Icon).use(Uploader).use(Popup).use(Picker).use(Tab).use(Tabs)
   .use(Card).use(Tag).use(Empty).use(PullRefresh).use(Loading)
   .use(ActionBar).use(ActionBarIcon).use(ActionBarButton)
   .use(Dialog).use(Rate).use(Tabbar).use(TabbarItem)
   // 👇👇👇 关键：告诉 Vue 要用搜索框和列表
   .use(Search)
   .use(List)

app.mount('#app')