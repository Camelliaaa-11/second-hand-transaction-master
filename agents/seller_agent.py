"""
卖家智能体
"""
from .context import SellerContext
from .rules import SellerFirstResponseRule
from .message_templates import MessageTemplates


class SellerAgent:
    """卖家智能体"""

    def __init__(self):
        self.response_rule = SellerFirstResponseRule()

    def respond_to_offer(self, ctx: SellerContext, buyer_offer: float) -> dict:
        """回应买家出价"""
        result = self.response_rule.apply(ctx, buyer_offer)

        # 生成详细推理
        reasoning_parts = []
        if buyer_offer < ctx.seller_min_price * 0.7:
            reasoning_parts.append(f"出价低于底价70%")
        elif ctx.is_urgent_sale and buyer_offer >= ctx.seller_min_price:
            reasoning_parts.append(f"急售且出价达到底价")

        reasoning = f"买家出价{buyer_offer}，我的底价{ctx.seller_min_price}"
        if reasoning_parts:
            reasoning += f"，因为{', '.join(reasoning_parts)}"

        return {
            'action': result['action'],
            'price': result['price'],
            'message': result['message'],
            'reasoning': reasoning
        }