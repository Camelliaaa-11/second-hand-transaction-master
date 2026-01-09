"""
规则引擎
"""
from .message_templates import MessageTemplates


class BuyerInitialOfferRule:
    """买家首轮出价规则"""

    def apply(self, ctx) -> dict:
        """
        返回: {'strategy': 'AGGRESSIVE'|'MODERATE'|'SINCERE', 'offer_price': float}
        """
        listed_price = ctx.item_listed_price
        market_avg = ctx.market_avg_price
        urgency = ctx.buyer_urgency
        seller_credit = ctx.seller_credit_score

        # 默认：温和砍价
        offer = listed_price * 0.9
        strategy = "MODERATE"

        # 规则1: 激进砍价 (价格远高于市场价)
        if listed_price > market_avg * 1.3:
            offer = market_avg * 0.85
            strategy = "AGGRESSIVE"

        # 规则2: 诚意出价 (紧迫度高且卖家信用好)
        if urgency >= 4 and seller_credit >= 90:
            offer = listed_price * 0.95
            strategy = "SINCERE"

        # 不能超过预算
        if hasattr(ctx, 'buyer_max_budget') and offer > ctx.buyer_max_budget:
            offer = ctx.buyer_max_budget * 0.95

        return {
            'strategy': strategy,
            'offer_price': round(offer, 2)
        }


class BuyerCounterOfferRule:
    """买家应对还价规则"""

    def apply(self, ctx, seller_last_price: float) -> dict:
        """
        根据卖家报价决定下一步
        返回: {'action': 'ACCEPT'|'COUNTER'|'HOLD'|'WALK_AWAY', 'price': float}
        """
        budget = ctx.buyer_max_budget
        urgency = ctx.buyer_urgency

        # 规则1: 直接接受 (价格可接受)
        if seller_last_price <= budget:
            return {'action': 'ACCEPT', 'price': seller_last_price}

        # 规则2: 紧迫时多出一点
        elif urgency >= 4 and seller_last_price <= budget * 1.1:
            return {'action': 'ACCEPT', 'price': seller_last_price}

        # 规则3: 提出折中价 (前3轮)
        elif ctx.negotiation_round < 3:
            last_buyer_price = ctx.history_offers[-1] if ctx.history_offers else 0
            if last_buyer_price > 0:
                counter_price = (last_buyer_price + seller_last_price) / 2
                counter_price = min(counter_price, budget)
                return {'action': 'COUNTER', 'price': counter_price}

        # 规则4: 坚持立场 (最后通牒)
        elif ctx.negotiation_round >= 3:
            last_buyer_price = ctx.history_offers[-1]
            return {'action': 'HOLD', 'price': last_buyer_price}

        # 规则5: 放弃
        return {'action': 'WALK_AWAY', 'price': 0}


class SellerFirstResponseRule:
    """卖家首轮回应规则"""

    def apply(self, ctx, buyer_offer: float) -> dict:
        """
        返回: {'action': 'REJECT'|'COUNTER_OFFER'|'ACCEPT', 'price': float, 'message': str}
        """
        min_price = ctx.seller_min_price
        listed_price = ctx.item_listed_price
        round_num = ctx.negotiation_round
        is_urgent = ctx.is_urgent_sale

        # 规则1: 直接拒绝 (出价太低)
        if buyer_offer < min_price * 0.7:
            message = MessageTemplates.get_seller_message(
                'REJECT',
                offer_price=buyer_offer,
                min_price=min_price
            )
            return {
                'action': 'REJECT',
                'price': min_price,
                'message': message
            }

        # 规则2: 接受 (出价不错)
        if buyer_offer >= min_price * 1.1 or (is_urgent and buyer_offer >= min_price):
            message = MessageTemplates.get_seller_message(
                'ACCEPT',
                offer_price=buyer_offer
            )
            return {
                'action': 'ACCEPT',
                'price': buyer_offer,
                'message': message
            }

        # 规则3: 还价 (阶梯式让步)
        if round_num == 0:
            # 第一轮：小幅让步
            counter_price = listed_price * 0.95
        elif round_num == 1:
            # 第二轮：多让一点
            counter_price = listed_price * 0.90
        elif round_num >= 2:
            # 后续轮次：根据急售情况
            if is_urgent:
                counter_price = max(listed_price * 0.85, min_price * 1.05)
            else:
                counter_price = max(listed_price * 0.88, min_price * 1.08)

        # 确保不低于底价
        counter_price = max(counter_price, min_price * 1.02)
        counter_price = round(counter_price, 2)

        message = MessageTemplates.get_seller_message(
            'COUNTER_OFFER',
            counter_price=counter_price
        )

        return {
            'action': 'COUNTER_OFFER',
            'price': counter_price,
            'message': message
        }