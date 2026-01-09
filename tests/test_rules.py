import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.context import BuyerContext, SellerContext
from agents.rules import BuyerInitialOfferRule, SellerFirstResponseRule


def test_buyer_initial_offer_rule():
    """测试买家首轮出价规则"""
    print("🧪 测试买家首轮出价规则")

    rule = BuyerInitialOfferRule()

    # 测试用例1：价格远高于市场价 -> 激进策略
    ctx1 = BuyerContext(
        item_id=1,
        item_category="phone",
        item_condition="GOOD",
        item_listed_price=3000.0,  # 远高于市场价
        market_avg_price=1500.0,
        buyer_max_budget=2000.0,
        buyer_urgency=3
    )

    result1 = rule.apply(ctx1)
    print(f"  用例1 - 高价商品:")
    print(f"    策略: {result1['strategy']}")
    print(f"    出价: {result1['offer_price']}")
    assert result1['strategy'] == "AGGRESSIVE"
    assert result1['offer_price'] < 1500  # 应该低于市场价

    # 测试用例2：正常价格 -> 温和策略
    ctx2 = BuyerContext(
        item_id=2,
        item_category="phone",
        item_condition="GOOD",
        item_listed_price=1800.0,  # 接近市场价
        market_avg_price=1500.0,
        buyer_max_budget=2000.0,
        buyer_urgency=3
    )

    result2 = rule.apply(ctx2)
    print(f"\n  用例2 - 正常价格:")
    print(f"    策略: {result2['strategy']}")
    print(f"    出价: {result2['offer_price']}")
    assert result2['strategy'] == "MODERATE"

    print("✅ 买家规则测试通过")


def test_seller_response_rule():
    """测试卖家回应规则"""
    print("\n🧪 测试卖家回应规则")

    rule = SellerFirstResponseRule()

    # 测试用例1：买家出价太低 -> 拒绝
    ctx1 = SellerContext(
        item_id=1,
        item_category="phone",
        item_condition="GOOD",
        item_listed_price=2000.0,
        market_avg_price=1500.0,
        seller_min_price=1600.0,
        is_urgent_sale=False
    )

    result1 = rule.apply(ctx1, 1000.0)  # 出价1000，远低于底价
    print(f"  用例1 - 低价出价:")
    print(f"    动作: {result1['action']}")
    print(f"    回应价: {result1['price']}")
    assert result1['action'] == "REJECT"

    # 测试用例2：合理出价 -> 还价
    result2 = rule.apply(ctx1, 1400.0)  # 合理出价
    print(f"\n  用例2 - 合理出价:")
    print(f"    动作: {result2['action']}")
    print(f"    回应价: {result2['price']}")
    assert result2['action'] == "COUNTER_OFFER"

    print("✅ 卖家规则测试通过")


if __name__ == "__main__":
    test_buyer_initial_offer_rule()
    test_seller_response_rule()
    print("\n🎉 所有规则测试通过！")