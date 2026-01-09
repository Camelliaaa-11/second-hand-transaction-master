"""
智能体上下文数据结构
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class SharedContext:
    """公共上下文"""
    item_id: int
    item_category: str
    item_condition: str  # 'NEW', 'GOOD', 'FAIR', 'USED'
    item_listed_price: float
    market_avg_price: float = 0.0
    negotiation_round: int = 0
    history_offers: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_offer(self, price: float):
        """添加报价到历史"""
        self.history_offers.append(price)
        self.negotiation_round += 1


@dataclass
class BuyerContext(SharedContext):
    """买家上下文"""
    user_id: int = 0
    buyer_max_budget: float = 0.0
    buyer_urgency: int = 3  # 1-5
    seller_credit_score: int = 80
    preferred_tone: str = "POLITE"  # POLITE, DATA_DRIVEN, TOUGH
    buyer_credit_score: int = 80


@dataclass
class SellerContext(SharedContext):
    """卖家上下文"""
    user_id: int = 0
    seller_min_price: float = 0.0  # 心理底价
    is_urgent_sale: bool = False
    buyer_credit_score: int = 80
    seller_stubbornness: int = 3  # 1-5
    seller_credit_score: int = 80