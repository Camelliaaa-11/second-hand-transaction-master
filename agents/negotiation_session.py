"""
谈判会话管理器
"""
import time
from .context import BuyerContext, SellerContext
from .buyer_agent import BuyerAgent
from .seller_agent import SellerAgent


class NegotiationSession:
    """谈判会话管理器"""

    def __init__(self):
        self.buyer_agent = BuyerAgent()
        self.seller_agent = SellerAgent()
        self.max_rounds = 5

    class NegotiationAssistant:
        """谈判助手（仅提供建议）"""

        def __init__(self):
            self.buyer_agent = BuyerAgent()
            self.seller_agent = SellerAgent()

        def advise_buyer(self, buyer_data: dict) -> dict:
            """
            为买家提供砍价建议
            返回：建议价格、话术、策略
            """
            # 创建上下文
            ctx = BuyerContext(
                user_id=buyer_data.get('user_id', 0),
                item_id=buyer_data['item_id'],
                item_category=buyer_data.get('item_category', 'phone'),
                item_condition=buyer_data.get('item_condition', 'GOOD'),
                item_listed_price=float(buyer_data['item_listed_price']),
                market_avg_price=buyer_data.get('market_avg_price', 1500.0),
                buyer_max_budget=float(buyer_data.get('buyer_max_budget', 0)),
                buyer_urgency=int(buyer_data.get('buyer_urgency', 3)),
                seller_credit_score=int(buyer_data.get('seller_credit_score', 80))
            )

            # 获取建议
            advice = self.buyer_agent.generate_first_offer(ctx)

            return {
                'type': 'buyer_advice',
                'advice': advice,
                'timestamp': '2024',
                'note': '这是一个建议，请用户决定是否采纳'
            }

        def advise_seller(self, seller_data: dict, buyer_offer: float) -> dict:
            """
            为卖家提供回应建议
            返回：建议动作、价格、话术
            """
            # 创建上下文
            ctx = SellerContext(
                user_id=seller_data.get('user_id', 0),
                item_id=seller_data['item_id'],
                item_category=seller_data.get('item_category', 'phone'),
                item_condition=seller_data.get('item_condition', 'GOOD'),
                item_listed_price=float(seller_data['item_listed_price']),
                market_avg_price=seller_data.get('market_avg_price', 1500.0),
                seller_min_price=float(seller_data.get('seller_min_price', 0)),
                is_urgent_sale=bool(seller_data.get('is_urgent_sale', False)),
                buyer_credit_score=int(seller_data.get('buyer_credit_score', 80)),
                negotiation_round=int(seller_data.get('negotiation_round', 0))
            )

            # 获取建议
            advice = self.seller_agent.respond_to_offer(ctx, buyer_offer)

            return {
                'type': 'seller_response',
                'advice': advice,
                'timestamp': '2024',
                'note': '这是一个建议，请卖家决定是否采纳'
            }

    def _format_result(self, status, final_price, rounds, history):
        """格式化结果"""
        return {
            'status': status,
            'final_price': final_price,
            'total_rounds': rounds,
            'history': history,
            'timestamp': time.time()
        }