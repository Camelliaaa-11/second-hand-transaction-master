"""
市场数据服务（连接数据库）
"""
import json
from typing import Dict, Optional


class MarketDataService:
    """市场数据服务"""

    # 模拟数据库连接
    _cache: Dict = {}

    @classmethod
    def get_historical_average_price(cls, category: str, condition: str) -> float:
        """获取历史成交均价"""
        key = f"{category}_{condition}"

        # 模拟数据
        prices = {
            'phone_NEW': 3000.0,
            'phone_GOOD': 1500.0,
            'phone_FAIR': 1000.0,
            'laptop_NEW': 5000.0,
            'laptop_GOOD': 2500.0,
            'book_NEW': 50.0,
            'book_GOOD': 30.0,
        }

        return prices.get(key, 1000.0)

    @classmethod
    def get_user_credit_score(cls, user_id: int) -> int:
        """获取用户信用分"""
        # 模拟：根据用户ID生成信用分
        return 80 + (user_id % 20)  # 80-99分

    @classmethod
    def get_item_market_data(cls, item_id: int) -> dict:
        """获取商品市场数据"""
        # 模拟数据
        return {
            'avg_price': 1500.0,
            'min_price': 1200.0,
            'max_price': 1800.0,
            'transaction_count': 15,
            'last_month_sales': 8
        }