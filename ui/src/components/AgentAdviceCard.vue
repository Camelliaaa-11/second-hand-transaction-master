<template>
  <van-dialog 
    v-model:show="showDialog" 
    title="🤖 智能助手建议" 
    show-cancel-button 
    confirm-button-text="✅ 采纳建议"
    cancel-button-text="再想想"
    @confirm="handleConfirm"
  >
    <div class="advice-content">
      <div class="strategy-badge" :class="advice.strategy">
        {{ strategyMap[advice.strategy] || '智能分析中' }}
      </div>
      
      <div class="price-row">
        建议出价：<span class="price">¥{{ advice.price }}</span>
      </div>
      
      <div class="message-box">
        <strong>话术建议：</strong>
        <p>{{ advice.message }}</p>
      </div>
      
      <div class="reason-box">
        <small>💡 分析：{{ advice.reasoning }}</small>
      </div>
    </div>
  </van-dialog>
</template>

<script setup>
import { computed } from 'vue';

// 接收父组件传来的数据
const props = defineProps(['show', 'advice']);
const emit = defineEmits(['update:show', 'adopt']);

// 控制弹窗显示
const showDialog = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
});

// 策略翻译字典
const strategyMap = {
  'AGGRESSIVE': '🔥 激进策略',
  'MODERATE': '⚖️ 温和策略',
  'CONSERVATIVE': '🛡️ 保守策略'
};

// 点击“采纳”按钮
const handleConfirm = () => {
  emit('adopt', props.advice.price, props.advice.message);
};
</script>

<style scoped>
.advice-content { padding: 20px; }
.strategy-badge { 
  display: inline-block; 
  padding: 2px 8px; 
  border-radius: 4px; 
  font-size: 12px; 
  color: white; 
  background: #1989fa; 
  margin-bottom: 10px;
}
.strategy-badge.AGGRESSIVE { background: #ee0a24; } /* 激进变红 */
.strategy-badge.MODERATE { background: #07c160; }   /* 温和变绿 */
.price-row { font-size: 16px; margin-bottom: 10px; }
.price { color: #ee0a24; font-weight: bold; font-size: 20px; }
.message-box { 
  background: #f7f8fa; 
  padding: 10px; 
  border-radius: 8px; 
  margin-bottom: 10px; 
  color: #333; 
  font-size: 14px;
}
.reason-box { color: #999; font-size: 12px; }
</style>