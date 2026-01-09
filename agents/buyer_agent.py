"""
买家智能体
"""
from .context import BuyerContext
from .rules import BuyerInitialOfferRule, BuyerCounterOfferRule
from .message_templates import MessageTemplates


class BuyerAgent:
    """买家智能体"""

    def __init__(self):
        self.initial_rule = BuyerInitialOfferRule()
        self.counter_rule = BuyerCounterOfferRule()

    def generate_first_offer(self, ctx: BuyerContext) -> dict:
        """生成首轮出价建议"""
        # 1. 应用出价规则
        result = self.initial_rule.apply(ctx)

        # 2. 生成话术
        message = MessageTemplates.get_buyer_message(
            strategy=result['strategy'],
            offer_price=result['offer_price'],
            market_price=ctx.market_avg_price,
            listed_price=ctx.item_listed_price
        )

        return {
            'action': 'MAKE_OFFER',
            'price': result['offer_price'],
            'message': message,
            'strategy': result['strategy'],
            'reasoning': f"应用{result['strategy']}策略，基于市场价{ctx.market_avg_price}元"
        }

    def generate_counter_offer(self, ctx: BuyerContext, seller_price: float) -> dict:
        """生成应对还价建议"""
        # 1. 应用应对规则
        result = self.counter_rule.apply(ctx, seller_price)

        # 2. 生成话术
        if result['action'] == 'ACCEPT':
            message = f"好的，{result['price']}元成交！"
        elif result['action'] == 'COUNTER':
            message = f"那我让一步，{result['price']}元可以吗？"
        elif result['action'] == 'HOLD':
            message = f"这是我最后的价格了，{result['price']}元，不行就算了。"
        else:
            message = "不好意思，这个价格我接受不了，再看看别的吧。"

        return {
            'action': result['action'],
            'price': result['price'],
            'message': message,
            'reasoning': f"卖家报价{seller_price}，我的预算{ctx.buyer_max_budget}"
        }