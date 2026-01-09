"""
话术模板库
"""
import random


class MessageTemplates:
    """话术模板"""

    BUYER_TEMPLATES = {
        "AGGRESSIVE": [
            "市场价才{market_price}元左右，您这{listed_price}元太高了，{offer_price}元比较合理。",
            "同款别人都卖{market_price}元，您这价格没优势，{offer_price}元我要了。",
            "诚心要，但您这价格比市场贵了{percent_diff}%，{offer_price}元可以吗？"
        ],
        "MODERATE": [
            "您好，{offer_price}元可以出吗？预算有限。",
            "很喜欢您的商品，{offer_price}元可以的话我马上付款。",
            "{offer_price}元可以接受吗？诚心交易。"
        ],
        "SINCERE": [
            "看到您信用很好，相信商品质量，{offer_price}元可以吗？",
            "诚心想要，{offer_price}元可以接受，希望交个朋友。",
            "第一次在平台交易，给您{offer_price}元，相信您的信誉。"
        ]
    }

    SELLER_TEMPLATES = {
        "REJECT": [
            "这个价格太低了，最低{min_price}元。",
            "不好意思，{offer_price}元卖不了，我的底价是{min_price}元。",
            "您这出价有点低啊，{counter_price}元可以考虑。"
        ],
        "COUNTER_OFFER": [
            "最低{counter_price}元，已经很优惠了。",
            "这样吧，{counter_price}元给您包邮。",
            "看您诚心要，{counter_price}元交个朋友。"
        ],
        "ACCEPT": [
            "好吧，成交！",
            "行，就按您说的{offer_price}元。",
            "可以，{offer_price}元我修改价格了。"
        ]
    }

    @staticmethod
    def get_buyer_message(strategy: str, offer_price: float,
                          market_price: float = None, listed_price: float = None) -> str:
        """获取买家话术"""
        templates = MessageTemplates.BUYER_TEMPLATES.get(strategy, ["{offer_price}元可以吗？"])
        template = random.choice(templates)

        # 计算百分比差异
        percent_diff = 0
        if market_price and listed_price:
            percent_diff = int((listed_price - market_price) / market_price * 100)

        return template.format(
            offer_price=offer_price,
            market_price=market_price,
            listed_price=listed_price,
            percent_diff=percent_diff
        )

    @staticmethod
    def get_seller_message(action: str, offer_price: float = None,
                           counter_price: float = None, min_price: float = None) -> str:
        """获取卖家话术"""
        templates = MessageTemplates.SELLER_TEMPLATES.get(action, ["{}元"])
        template = random.choice(templates)

        return template.format(
            offer_price=offer_price,
            counter_price=counter_price,
            min_price=min_price
        )