import axios from 'axios';
import { showToast } from 'vant';

// 创建 axios 实例
const agentRequest = axios.create({
  baseURL: '', // 直接请求主后端
  timeout: 5000
});

// 1. 获取买家砍价建议
export const getBuyerAdvice = async (data) => {
  try {
    // ⚠️ 修正点：之前是 /advice/buyer，现在改成后端显示的 /buyer/advice
    const response = await agentRequest.post('/api/v1/buyer/advice', data);
    if (response.data.success) {
      return response.data.data;
    }
    return null;
  } catch (error) {
    console.error('智能体请求失败:', error);
    showToast({ message: '智能体服务连接失败', position: 'bottom' });
    return null;
  }
};

// 2. 获取卖家回应建议
export const getSellerAdvice = async (data) => {
  try {
    // ⚠️ 修正点：改成 /seller/response
    const response = await agentRequest.post('/api/v1/seller/response', data);
    if (response.data.success) {
      return response.data.data;
    }
    return null;
  } catch (error) {
    showToast('智能体服务连接失败');
    return null;
  }
};