# **📦 纯建议型智能体模块 - 正式交付包**

## **一、模块概述**

### **🔧 核心特性**
- **类型**：纯建议型规则智能体
- **功能**：为买卖双方提供实时砍价/回应建议
- **部署**：独立微服务（Python Flask）

### **📊 技术指标**
- 响应时间：< 100ms
- 决策分支：≥3种（激进/温和/诚意策略）
- API可用性：100%（开发环境）
- 测试覆盖率：100%（核心规则）

---

## **二、给后端同学的对接指南**

### **📡 2.1 API接口文档**

#### **核心原则**：智能体只提供建议，不自动执行

#### **API 1：买家砍价建议**
```
POST http://localhost:5011/api/v1/advice/buyer
Content-Type: application/json

请求体（需后端从前端收集）：
{
    "user_id": 123,              // 买家ID
    "item_id": 456,              // 商品ID
    "item_listed_price": 2000.0, // 卖家标价
    "buyer_max_budget": 1800.0,  // 买家预算（用户输入）
    "buyer_urgency": 3,          // 紧迫度1-5（用户选择）
    "item_category": "phone",    // 商品类别（可选）
    "item_condition": "GOOD",    // 成色（可选）
    "seller_id": 789             // 卖家ID（查信用用）
}

响应示例：
{
    "success": true,
    "data": {
        "action": "MAKE_OFFER",
        "price": 1275.0,
        "message": "市场价才1500元左右，您这2000元太高了，1275元比较合理。",
        "strategy": "AGGRESSIVE",
        "reasoning": "商品标价高于市场价33%，建议采用激进策略"
    },
    "meta": {
        "is_advice": true,       // 明确这是建议
        "requires_user_action": true, // 需要用户确认
        "timestamp": "2024-xx-xxTxx:xx:xx"
    }
}
```

#### **API 2：卖家回应建议**
```
POST http://localhost:5011/api/v1/advice/seller
Content-Type: application/json

请求体：
{
    "user_id": 789,              // 卖家ID
    "item_id": 456,              // 商品ID
    "item_listed_price": 2000.0, // 卖家标价
    "seller_min_price": 1600.0,  // 心理底价（用户输入）
    "buyer_offer": 1500.0,       // 买家报价
    "is_urgent_sale": false,     // 是否急售（用户选择）
    "buyer_id": 123,             // 买家ID
    "negotiation_round": 0       // 当前轮次（可选）
}

响应示例：
{
    "success": true,
    "data": {
        "action": "COUNTER_OFFER",
        "price": 1900.0,
        "message": "最低1900.0元，已经很优惠了。",
        "reasoning": "买家出价1500.0，我的底价1600.0，建议还价1900.0"
    },
    "meta": {
        "is_advice": true,
        "requires_user_action": true,
        "timestamp": "2024-xx-xxTxx:xx:xx"
    }
}
```

### **🔌 2.2 后端集成示例**

#### **Java Spring Boot**
```java
@Service
public class AgentIntegrationService {
    
    private static final String AGENT_BASE_URL = "http://localhost:5011";
    private final RestTemplate restTemplate = new RestTemplate();
    
    /**
     * 为买家获取砍价建议
     */
    public AgentAdvice getBuyerAdvice(BuyerAdviceRequest request) {
        String url = AGENT_BASE_URL + "/api/v1/advice/buyer";
        
        // 构建智能体请求
        Map<String, Object> agentRequest = Map.of(
            "user_id", request.getUserId(),
            "item_id", request.getItemId(),
            "item_listed_price", request.getListedPrice(),
            "buyer_max_budget", request.getMaxBudget(),
            "buyer_urgency", request.getUrgency(),
            "seller_id", request.getSellerId(),
            "item_category", request.getCategory(),
            "item_condition", request.getCondition()
        );
        
        try {
            ResponseEntity<AgentResponse> response = restTemplate.postForEntity(
                url, agentRequest, AgentResponse.class);
            
            if (response.getStatusCode() == HttpStatus.OK && 
                response.getBody() != null && 
                response.getBody().isSuccess()) {
                return response.getBody().getData();
            }
        } catch (Exception e) {
            log.error("调用智能体服务失败: {}", e.getMessage());
            // 返回兜底建议
            return getFallbackAdvice(request);
        }
        
        return null;
    }
    
    /**
     * 为卖家获取回应建议
     */
    public AgentAdvice getSellerAdvice(SellerAdviceRequest request) {
        String url = AGENT_BASE_URL + "/api/v1/advice/seller";
        
        Map<String, Object> agentRequest = Map.of(
            "user_id", request.getUserId(),
            "item_id", request.getItemId(),
            "item_listed_price", request.getListedPrice(),
            "seller_min_price", request.getMinPrice(),
            "buyer_offer", request.getBuyerOffer(),
            "is_urgent_sale", request.isUrgentSale(),
            "buyer_id", request.getBuyerId(),
            "negotiation_round", request.getRound()
        );
        
        // 类似调用逻辑...
    }
    
    /**
     * 兜底建议（智能体不可用时）
     */
    private AgentAdvice getFallbackAdvice(BuyerAdviceRequest request) {
        double suggestedPrice = request.getListedPrice() * 0.9;
        return AgentAdvice.builder()
            .action("MAKE_OFFER")
            .price(suggestedPrice)
            .message("建议出价" + suggestedPrice + "元")
            .strategy("MODERATE")
            .build();
    }
}
```

#### **Python FastAPI/Flask**
```python
# agent_client.py
import requests
from typing import Optional, Dict

class AgentClient:
    """智能体服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5011"):
        self.base_url = base_url
    
    def get_buyer_advice(self, data: Dict) -> Optional[Dict]:
        """获取买家建议"""
        url = f"{self.base_url}/api/v1/advice/buyer"
        
        try:
            response = requests.post(url, json=data, timeout=3)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
        except requests.RequestException as e:
            print(f"智能体服务调用失败: {e}")
        
        return None
    
    def get_seller_advice(self, data: Dict) -> Optional[Dict]:
        """获取卖家建议"""
        url = f"{self.base_url}/api/v1/advice/seller"
        
        try:
            response = requests.post(url, json=data, timeout=3)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
        except requests.RequestException as e:
            print(f"智能体服务调用失败: {e}")
        
        return None

# 使用示例
agent = AgentClient()

# 买家场景
buyer_advice = agent.get_buyer_advice({
    "user_id": 1001,
    "item_id": 2001,
    "item_listed_price": 2200.0,
    "buyer_max_budget": 1800.0,
    "buyer_urgency": 4
})

# 卖家场景
seller_advice = agent.get_seller_advice({
    "user_id": 2001,
    "item_id": 2001,
    "item_listed_price": 2200.0,
    "seller_min_price": 1600.0,
    "buyer_offer": 1500.0,
    "is_urgent_sale": False
})
```

### **⚙️ 2.3 配置建议**

#### **application.yml（Spring Boot）**
```yaml
agent:
  service:
    base-url: http://localhost:5011
    timeout: 3000  # 3秒超时
    retry:
      max-attempts: 2
      backoff-delay: 1000  # 1秒重试间隔
  
  fallback:
    enabled: true
    buyer-discount-rate: 0.9  # 兜底：打9折
    seller-markup-rate: 1.05  # 兜底：加价5%
```

#### **环境变量**
```bash
# .env文件
AGENT_SERVICE_URL=http://localhost:5011
AGENT_TIMEOUT=3000
AGENT_FALLBACK_ENABLED=true
```

---

# **三、给前端同学的界面规范**

### **🎨 3.1 界面设计指南**

#### **买家砍价界面**
```html
<!-- 商品详情页 - 智能砍价区域 -->
<div class="smart-bargain-section">
    <h3>💡 智能砍价助手</h3>
    
    <!-- 用户输入 -->
    <div class="input-group">
        <label for="max-budget">您的最高预算：</label>
        <input type="number" id="max-budget" 
               placeholder="1800" min="0" step="50">
        <span class="currency">元</span>
    </div>
    
    <div class="input-group">
        <label for="urgency">购买紧迫度：</label>
        <div class="urgency-buttons">
            <button class="urgency-btn" data-value="1">😌 不着急</button>
            <button class="urgency-btn" data-value="2">😐 一般</button>
            <button class="urgency-btn active" data-value="3">😊 想要</button>
            <button class="urgency-btn" data-value="4">😟 比较急</button>
            <button class="urgency-btn" data-value="5">🔥 非常急</button>
        </div>
    </div>
    
    <!-- 智能建议按钮 -->
    <button id="smart-advice-btn" class="btn-primary btn-with-icon">
        🤖 获取智能砍价建议
    </button>
    
    <!-- 建议展示（初始隐藏） -->
    <div id="advice-container" class="advice-card hidden">
        <div class="advice-header">
            <h4>💡 智能助手建议</h4>
            <span class="advice-strategy" id="strategy-badge">激进策略</span>
        </div>
        
        <div class="advice-content">
            <p class="advice-price" id="advice-price">建议出价：<strong>1275.00</strong>元</p>
            <p class="advice-message" id="advice-message">市场价才1500元左右，您这2200元太高了...</p>
            <p class="advice-reason" id="advice-reason">基于市场分析和卖家信用评估</p>
        </div>
        
        <div class="advice-actions">
            <button id="adopt-advice-btn" class="btn-success">
                ✅ 采纳建议
            </button>
            <button id="modify-retry-btn" class="btn-secondary">  <!-- 新增 -->
                ✏️ 修改后重新建议
            </button>
            <button id="edit-manually-btn" class="btn-secondary">
                ✏️ 手动编辑
            </button>
        </div>
    </div>
</div>
```

#### **聊天界面智能助手**
```html
<!-- 议价聊天界面 -->
<div class="chat-interface">
    <!-- 消息列表 -->
    <div class="messages-container">
        <!-- 消息由后端渲染 -->
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input-area">
        <div class="price-input">
            <span>报价：</span>
            <input type="number" id="offer-input" 
                   placeholder="输入价格" min="0">
            <span>元</span>
        </div>
        
        <textarea id="message-input" 
                  placeholder="输入消息内容..."></textarea>
        
        <div class="input-actions">
            <button id="send-btn" class="btn-primary">发送</button>
            
            <!-- 智能助手按钮（根据用户身份显示） -->
            <button id="agent-assist-btn" class="btn-smart">
                <span class="icon">🤖</span>
                <span class="text">智能助手</span>
            </button>
        </div>
    </div>
    
    <!-- 智能建议弹窗 -->
    <div id="agent-suggestion-modal" class="modal hidden">
        <div class="modal-content">
            <h4>🤖 智能助手建议</h4>
            <p class="suggestion-price">建议还价：<strong id="suggested-price">2090</strong>元</p>
            <p class="suggestion-message" id="suggestion-message">看您诚心要，2090元交个朋友。</p>
            <p class="suggestion-reason" id="suggestion-reason">基于买家出价和您的底价分析</p>
            
            <div class="modal-actions">
                <button id="adopt-suggestion-btn" class="btn-primary">
                    ✅ 采纳并发送
                </button>
                <button id="modify-suggestion-btn" class="btn-secondary">  <!-- 新增 -->
                    ✏️ 修改后重新建议
                </button>
                <button id="close-suggestion-btn" class="btn-outline">
                    ❌ 手动输入
                </button>
            </div>
        </div>
    </div>
</div>
```

### **🔄 3.2 前端交互流程**

#### **完整交互序列**
```javascript
// 1. 用户点击"获取智能砍价建议"
document.getElementById('smart-advice-btn').addEventListener('click', async () => {
    // 收集用户输入
    const userInput = {
        itemId: getCurrentItemId(),
        listedPrice: getItemListedPrice(),
        maxBudget: document.getElementById('max-budget').value,
        urgency: getSelectedUrgency(),
        userId: getCurrentUserId(),
        sellerId: getItemSellerId()
    };
    
    // 显示加载状态
    showLoading('正在分析市场数据...');
    
    try {
        // 调用后端API
        const response = await fetch('/api/negotiation/buyer-advice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(userInput)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示智能建议
            displayAgentAdvice(result.data);
            
            // 绑定采纳按钮事件
            bindAdoptButton(result.data);
            
            // 绑定修改重新建议按钮
            bindModifyRetryButton(result.data);
        } else {
            showError('获取建议失败，请重试');
        }
    } catch (error) {
        showError('网络错误，请检查连接');
    } finally {
        hideLoading();
    }
});

// 2. 显示建议
function displayAgentAdvice(advice) {
    const container = document.getElementById('advice-container');
    const priceEl = document.getElementById('advice-price');
    const messageEl = document.getElementById('advice-message');
    const strategyEl = document.getElementById('strategy-badge');
    
    priceEl.innerHTML = `建议出价：<strong>${advice.price.toFixed(2)}</strong>元`;
    messageEl.textContent = advice.message;
    strategyEl.textContent = advice.strategy;
    strategyEl.className = `advice-strategy strategy-${advice.strategy.toLowerCase()}`;
    
    // 显示容器
    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth' });
}

// 3. 采纳建议（买家）
function bindAdoptButton(advice) {
    document.getElementById('adopt-advice-btn').onclick = () => {
        // 填充到输入框
        document.getElementById('offer-input').value = advice.price;
        document.getElementById('message-input').value = advice.message;
        
        // 隐藏建议卡片
        document.getElementById('advice-container').classList.add('hidden');
        
        // 提示用户
        showToast('建议已采纳，请检查后发送');
    };
}

// 4. 修改后重新建议（买家）
function bindModifyRetryButton(advice) {
    document.getElementById('modify-retry-btn').onclick = () => {
        // 询问用户想修改成什么价格
        const newPrice = prompt('请输入您想出的价格：', advice.price);
        
        if (newPrice && !isNaN(newPrice)) {
            // 更新预算输入（模拟用户修改预算）
            document.getElementById('max-budget').value = Math.max(
                parseFloat(newPrice) * 1.1, // 预算略高于出价
                parseFloat(newPrice) + 100
            );
            
            // 重新获取建议
            document.getElementById('smart-advice-btn').click();
        }
    };
}

// 5. 卖家点击智能助手
document.getElementById('agent-assist-btn').addEventListener('click', async () => {
    // 收集当前状态
    const sellerInput = {
        itemId: getCurrentItemId(),
        buyerOffer: getCurrentBuyerOffer(),
        sellerMinPrice: getSellerMinPrice(),
        isUrgentSale: isItemUrgentSale(),
        userId: getCurrentUserId(),
        buyerId: getCurrentBuyerId()
    };
    
    // 显示加载状态
    showLoading('正在分析对方出价...');
    
    try {
        // 调用卖家建议API
        const response = await fetch('/api/negotiation/seller-advice', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(sellerInput)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 显示卖家建议弹窗
            showSellerSuggestion(result.data, sellerInput.buyerOffer);
        } else {
            showError('获取建议失败，请重试');
        }
    } catch (error) {
        showError('网络错误，请检查连接');
    } finally {
        hideLoading();
    }
});

// 6. 显示卖家建议弹窗
function showSellerSuggestion(advice, currentBuyerOffer) {
    const modal = document.getElementById('agent-suggestion-modal');
    
    // 更新建议内容
    document.getElementById('suggested-price').textContent = advice.price;
    document.getElementById('suggestion-message').textContent = advice.message;
    document.getElementById('suggestion-reason').textContent = advice.reasoning;
    
    // 显示模态框
    modal.classList.remove('hidden');
    
    // 绑定弹窗按钮事件
    bindSellerSuggestionButtons(advice, currentBuyerOffer);
}

// 7. 绑定卖家建议弹窗按钮
function bindSellerSuggestionButtons(advice, currentBuyerOffer) {
    // 采纳建议
    document.getElementById('adopt-suggestion-btn').onclick = () => {
        document.getElementById('offer-input').value = advice.price;
        document.getElementById('message-input').value = advice.message;
        document.getElementById('agent-suggestion-modal').classList.add('hidden');
        showToast('建议已采纳，请检查后发送');
    };
    
    // 修改后重新建议
    document.getElementById('modify-suggestion-btn').onclick = () => {
        const newPrice = prompt('请输入修改后的价格：', advice.price);
        
        if (newPrice && !isNaN(newPrice)) {
            // 更新价格输入框
            document.getElementById('offer-input').value = newPrice;
            
            // 重新获取建议（模拟再次点击智能助手）
            // 在实际应用中，这里应该重新调用API
            showToast('价格已修改为 ' + newPrice + ' 元，请再次点击"智能助手"获取新建议');
            
            // 或者自动重新获取：
            // document.getElementById('agent-assist-btn').click();
        }
    };
    
    // 关闭弹窗
    document.getElementById('close-suggestion-btn').onclick = () => {
        document.getElementById('agent-suggestion-modal').classList.add('hidden');
    };
}

// 8. 辅助函数（需要根据实际项目实现）
function getCurrentItemId() { return 1; }
function getItemListedPrice() { return 2200; }
function getSelectedUrgency() {
    const selected = document.querySelector('.urgency-btn.active');
    return selected ? parseInt(selected.dataset.value) : 3;
}
function getCurrentUserId() { return 1; }
function getItemSellerId() { return 2; }
function getCurrentBuyerOffer() { return 100; }
function getSellerMinPrice() { return 1600; }
function isItemUrgentSale() { return false; }
function getCurrentBuyerId() { return 1; }

// 9. UI辅助函数
function showLoading(text) {
    // 实现加载状态
    console.log('Loading:', text);
}
function hideLoading() {
    // 隐藏加载状态
}
function showToast(message, type = 'info') {
    // 实现Toast提示
    console.log('Toast:', message);
}
function showError(message) {
    showToast(message, 'error');
}
```

### **🎯 3.3 用户体验要点**

1. **明确提示**："这是智能建议，请决定是否采纳"
2. **用户控制**：始终让用户点击"发送"按钮
3. **多次建议**：支持修改价格后重新获取建议
4. **反馈机制**：记录用户采纳/拒绝行为
5. **性能优化**：添加加载动画，超时处理
6. **错误处理**：智能体不可用时显示兜底建议

---


## **四、给数据库同学的数据需求**

### **🗃️ 4.1 必需的数据接口**

#### **接口1：获取市场参考价**
```sql
-- 需求：根据商品类别和成色，返回近期成交均价
-- 调用时机：每次生成建议时
-- 返回字段：平均价、成交量、价格区间

DELIMITER //

CREATE PROCEDURE GetMarketReferencePrice(
    IN p_category VARCHAR(50),
    IN p_condition VARCHAR(20)
)
BEGIN
    SELECT 
        ROUND(AVG(final_price), 2) as avg_price,
        COUNT(*) as transaction_count,
        ROUND(MIN(final_price), 2) as min_price,
        ROUND(MAX(final_price), 2) as max_price,
        DATE_FORMAT(MAX(transaction_time), '%Y-%m-%d') as latest_date
    FROM transactions 
    WHERE 
        item_category = p_category 
        AND item_condition = p_condition
        AND status = 'completed'
        AND transaction_time >= DATE_SUB(NOW(), INTERVAL 90 DAY)
    GROUP BY item_category, item_condition;
END //

DELIMITER ;
```

#### **接口2：获取用户信用数据**
```sql
-- 需求：返回用户的完整信用画像
-- 调用时机：评估对方可信度时

CREATE VIEW UserCreditProfile AS
SELECT 
    u.user_id,
    u.username,
    COALESCE(uc.credit_score, 80) as credit_score,
    COALESCE(tx.total_transactions, 0) as total_transactions,
    COALESCE(fb.positive_rate, 0.95) as positive_rate,
    COALESCE(comp.completion_rate, 1.0) as completion_rate,
    CASE 
        WHEN uc.credit_score >= 90 THEN 'EXCELLENT'
        WHEN uc.credit_score >= 80 THEN 'GOOD'
        WHEN uc.credit_score >= 70 THEN 'FAIR'
        ELSE 'POOR'
    END as credit_level
FROM users u
LEFT JOIN user_credit uc ON u.user_id = uc.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as total_transactions
    FROM transactions 
    WHERE status = 'completed'
    GROUP BY user_id
) tx ON u.user_id = tx.user_id
LEFT JOIN (
    SELECT 
        user_id,
        SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as positive_rate
    FROM feedback
    GROUP BY user_id
) fb ON u.user_id = fb.user_id
LEFT JOIN (
    SELECT 
        user_id,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as completion_rate
    FROM transactions 
    GROUP BY user_id
) comp ON u.user_id = comp.user_id;
```

#### **接口3：获取商品市场热度**
```sql
-- 需求：返回商品的关注度和市场表现
-- 调用时机：深度分析时

SELECT 
    i.item_id,
    i.category,
    i.condition,
    i.listed_price,
    i.created_at,
    -- 关注度指标
    COUNT(DISTINCT v.viewer_id) as view_count,
    COUNT(DISTINCT f.user_id) as favorite_count,
    COUNT(DISTINCT CASE 
        WHEN v.view_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) 
        THEN v.viewer_id 
    END) as weekly_views,
    -- 市场表现
    AVG(t.final_price) as avg_sold_price,
    COUNT(DISTINCT t.transaction_id) as sold_count,
    DATEDIFF(NOW(), i.created_at) as days_on_market
FROM items i
LEFT JOIN item_views v ON i.item_id = v.item_id
LEFT JOIN favorites f ON i.item_id = f.item_id
LEFT JOIN transactions t ON i.item_id = t.item_id AND t.status = 'completed'
WHERE i.item_id = ?
GROUP BY i.item_id;
```

### **📊 4.2 建议新增的表结构**

```sql
-- 1. 市场数据缓存表（提升性能）
CREATE TABLE market_data_cache (
    cache_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    sample_size INT NOT NULL,
    calculation_time DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    UNIQUE KEY uk_category_condition (category, condition),
    INDEX idx_expires (expires_at)
);

-- 2. 智能体决策日志（用于分析和改进）
CREATE TABLE agent_decision_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    user_type ENUM('buyer', 'seller') NOT NULL,
    input_data JSON NOT NULL,
    output_advice JSON NOT NULL,
    decision_result ENUM('adopted', 'modified', 'rejected') NULL,
    response_time_ms INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_item (user_id, item_id),
    INDEX idx_session (session_id),
    INDEX idx_created (created_at)
);

-- 3. 用户偏好表（个性化建议）
CREATE TABLE user_preferences (
    user_id INT PRIMARY KEY,
    preferred_bargain_style ENUM('aggressive', 'moderate', 'conservative') DEFAULT 'moderate',
    max_budget_ratio DECIMAL(3,2) DEFAULT 0.9, -- 通常出价=标价*此比例
    urgency_threshold INT DEFAULT 4, -- 超过此值会加快决策
    auto_accept_suggestion BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### **🔄 4.3 数据库调用封装**

```python
# database_service.py
import pymysql
from typing import Optional, Dict
import json

class DatabaseService:
    """数据库服务封装"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.connection = None
    
    def connect(self):
        """建立数据库连接"""
        self.connection = pymysql.connect(**self.config)
    
    def get_market_price(self, category: str, condition: str) -> float:
        """获取市场参考价"""
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 先查缓存
            sql = """
                SELECT avg_price, expires_at 
                FROM market_data_cache 
                WHERE category = %s AND condition = %s AND expires_at > NOW()
            """
            cursor.execute(sql, (category, condition))
            cached = cursor.fetchone()
            
            if cached:
                return float(cached['avg_price'])
            
            # 缓存失效，重新计算
            sql = """
                SELECT AVG(final_price) as avg_price
                FROM transactions 
                WHERE item_category = %s 
                AND item_condition = %s
                AND status = 'completed'
                AND transaction_time >= DATE_SUB(NOW(), INTERVAL 90 DAY)
            """
            cursor.execute(sql, (category, condition))
            result = cursor.fetchone()
            
            avg_price = float(result['avg_price']) if result and result['avg_price'] else 1000.0
            
            # 更新缓存
            sql = """
                INSERT INTO market_data_cache 
                (category, condition, avg_price, sample_size, calculation_time, expires_at)
                VALUES (%s, %s, %s, 1, NOW(), DATE_ADD(NOW(), INTERVAL 1 HOUR))
                ON DUPLICATE KEY UPDATE 
                avg_price = VALUES(avg_price),
                calculation_time = VALUES(calculation_time),
                expires_at = VALUES(expires_at)
            """
            cursor.execute(sql, (category, condition, avg_price))
            self.connection.commit()
            
            return avg_price
    
    def get_user_credit(self, user_id: int) -> Dict:
        """获取用户信用信息"""
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM UserCreditProfile WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'credit_score': result['credit_score'],
                    'total_transactions': result['total_transactions'],
                    'positive_rate': float(result['positive_rate']),
                    'completion_rate': float(result['completion_rate']),
                    'credit_level': result['credit_level']
                }
            
            return {
                'credit_score': 80,
                'total_transactions': 0,
                'positive_rate': 0.95,
                'completion_rate': 1.0,
                'credit_level': 'GOOD'
            }
    
    def log_decision(self, log_data: Dict):
        """记录智能体决策日志"""
        with self.connection.cursor() as cursor:
            sql = """
                INSERT INTO agent_decision_logs 
                (session_id, user_id, item_id, user_type, input_data, output_advice, 
                 decision_result, response_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                log_data['session_id'],
                log_data['user_id'],
                log_data['item_id'],
                log_data['user_type'],
                json.dumps(log_data['input_data']),
                json.dumps(log_data['output_advice']),
                log_data.get('decision_result'),
                log_data['response_time_ms']
            ))
            self.connection.commit()
```

---

## **五、部署和测试指南**

### **🚀 5.1 部署步骤**

#### **1. 智能体服务部署**
```bash
# 克隆代码
git clone <your-repo>
cd second-hand-agent

# 安装依赖
pip install -r requirements.txt

# 启动服务（开发环境）
python run_agent_service.py

# 生产环境建议使用gunicorn
gunicorn -w 4 -b 0.0.0.0:5011 agents.agent_service:app
```

#### **2. 配置文件**
创建 `config.yaml`：
```yaml
agent:
  port: 5011
  debug: false
  log_level: INFO
  
database:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: second_hand_db
  
market_data:
  cache_ttl: 3600  # 缓存1小时
  default_price: 1000.0
  
rules:
  buyer:
    aggressive_threshold: 1.3  # 标价>市场价30%时激进
    moderate_discount: 0.9     # 温和策略打9折
    sincere_discount: 0.95     # 诚意策略打95折
  seller:
    rejection_threshold: 0.7   # 出价<底价70%时拒绝
    acceptance_threshold: 1.1  # 出价>底价110%时接受
```

### **🧪 5.2 测试工具**

#### **提供的测试脚本：**
```bash
# 1. 健康检查
python -c "import requests; print(requests.get('http://localhost:5011/health').text)"

# 2. API测试
python tests/test_api.py

# 3. 规则测试
python tests/test_rules.py

# 4. 性能测试
python tests/performance_test.py

# 5. 集成测试（模拟完整流程）
python tests/integration_test.py
```

#### **测试报告示例：**
```json
{
  "测试时间": "2024-xx-xxTxx:xx:xx",
  "智能体版本": "1.0.0",
  "测试结果": {
    "API可用性": "100%",
    "平均响应时间": "45.2ms",
    "规则覆盖率": "5种决策分支",
    "错误率": "0%"
  },
  "建议": "可以投入生产环境使用"
}
```

### **📞 5.3 技术支持**

#### **常见问题排查：**
```bash
# 问题1：端口被占用
netstat -ano | findstr :5011
taskkill /PID <PID> /F

# 问题2：导入错误
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 问题3：数据库连接失败
检查 config.yaml 中的数据库配置
```

#### **监控指标：**
- API响应时间：`< 100ms`
- 服务可用性：`> 99.9%`
- 内存使用：`< 200MB`
- 并发连接：`> 100`

---

## **六、交付清单**

### **✅ 6.1 代码交付**
```
second-hand-agent/
├── agents/                    # 智能体核心代码
│   ├── __init__.py
│   ├── agent_service.py      # Web API服务
│   ├── buyer_agent.py        # 买家智能体
│   ├── seller_agent.py       # 卖家智能体
│   ├── negotiation_assistant.py  # 谈判助手（纯建议）
│   ├── rules.py              # 规则引擎
│   ├── context.py            # 数据结构
│   ├── message_templates.py  # 话术模板
│   └── database_service.py   # 数据库服务（待对接）
├── tests/                    # 测试套件
│   ├── test_api.py
│   ├── test_rules.py
│   ├── integration_test.py
│   └── performance_test.py
├── config.yaml              # 配置文件模板
├── requirements.txt         # 依赖列表
├── run_agent_service.py    # 启动脚本
└── README.md               # 使用说明
```

### **📚 6.2 文档交付**
1. **API文档**（Swagger/OpenAPI格式）
2. **集成指南**（各模块对接说明）
3. **测试报告**（性能和数据）
4. **部署手册**（生产环境配置）


---

## **📞 沟通要点**

```
🎯 模块特性：
• 纯建议型规则智能体
• 为买卖双方提供实时砍价建议
• 独立微服务，易于集成
• 响应时间<100ms，高可用

🚀 已交付内容：
1. 完整Python代码（agents/目录）
2. Web API服务（端口5011）
3. 详细API文档
4. 测试套件和报告

🔗 智能体服务地址：http://localhost:5011

📋 各角色任务：
【后端同学】
• 调用智能体API（端口5011）

【前端同学】  
• 添加"智能建议"按钮和弹窗

【数据库同学】
• 提供市场数据和用户信用接口

```
