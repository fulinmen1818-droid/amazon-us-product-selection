#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""亚马逊美国站利润核算与价格下限计算器。

用法示例：
  # 单产品完整核算（含价格下限、降价压力、保本 ACOS）
  python margin_calc.py --price 12.99 --fba 4.36 --landed 1.80

  # 只反算最低可售价
  python margin_calc.py --fba 4.36 --landed 1.80 --floor-only

  # 多个价格点横向对比
  python margin_calc.py --price 9.99 11.99 12.99 14.99 --fba 4.36 --landed 1.80

  # 指定其他变动费用与目标毛利
  python margin_calc.py --price 12.99 --fba 4.36 --landed 1.80 --other 1.20 --target-margin 0.35
"""
import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

COMMISSION = 0.15
TARGET_MARGIN = 0.30


def floor_price(fba, landed, other, commission, target_margin):
    """维持目标毛利所需的最低可售价。"""
    variable = fba + landed + other
    denominator = 1.0 - commission - target_margin
    if denominator <= 0:
        raise ValueError("佣金 + 目标毛利必须小于 100%")
    return variable / denominator


def evaluate(price, fba, landed, other, commission, ad_cost):
    """返回单个价格点的核算结果。"""
    variable = fba + landed + other
    commission_fee = price * commission
    gross = price - variable - commission_fee
    margin = gross / price if price else 0.0
    return {
        "price": price,
        "commission_fee": commission_fee,
        "variable": variable,
        "gross": gross,
        "margin": margin,
        "after_ad": gross - ad_cost,
        "breakeven_acos": margin,
    }


def fmt_money(v):
    return f"-${abs(v):.2f}" if v < 0 else f"${v:.2f}"


def main():
    p = argparse.ArgumentParser(
        description="亚马逊美国站广告前毛利、价格下限、保本 ACOS 计算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--price", type=float, nargs="+", default=None,
                   help="售价（可传多个做横向对比）")
    p.add_argument("--fba", type=float, required=True, help="FBA 配送费")
    p.add_argument("--landed", type=float, required=True,
                   help="落地成本（采购 + 包装 + 头程及关税）")
    p.add_argument("--other", type=float, default=1.20,
                   help="其他变动费用（仓储、退货损耗等），默认 1.20")
    p.add_argument("--commission", type=float, default=COMMISSION,
                   help="销售佣金比例，默认 0.15")
    p.add_argument("--target-margin", type=float, default=TARGET_MARGIN,
                   help="目标毛利率（硬门槛），默认 0.30")
    p.add_argument("--ad-cost", type=float, default=0.0,
                   help="单件广告花费，用于算广告后贡献利润")
    p.add_argument("--floor-only", action="store_true",
                   help="只输出最低可售价")
    args = p.parse_args()

    floor = floor_price(args.fba, args.landed, args.other,
                        args.commission, args.target_margin)

    if args.floor_only or not args.price:
        print("=" * 56)
        print("最低可售价（价格下限）")
        print("=" * 56)
        print(f"  FBA 配送费        ${args.fba:.2f}")
        print(f"  落地成本          ${args.landed:.2f}")
        print(f"  其他变动          ${args.other:.2f}")
        print(f"  变动成本合计      ${args.fba + args.landed + args.other:.2f}")
        print(f"  佣金比例          {args.commission:.0%}")
        print(f"  目标毛利率        {args.target_margin:.0%}")
        print("-" * 56)
        print(f"  最低可售价        ${floor:.2f}")
        print()
        print(f"  验证：${floor:.2f} 时毛利 "
              f"${floor * (1 - args.commission) - (args.fba + args.landed + args.other):.2f}"
              f" / {args.target_margin:.0%}")
        print()
        print("  判断规则：若类目销量加权成交价低于此值，该价格带结构性亏损。")
        return

    print("=" * 78)
    print(f"{'售价':>7} {'佣金':>7} {'变动成本':>9} {'广告前毛利':>11} {'毛利率':>8} "
          f"{'降价10%后':>10} {'广告后':>9}")
    print("=" * 78)
    rows = []
    for price in args.price:
        r = evaluate(price, args.fba, args.landed, args.other,
                     args.commission, args.ad_cost)
        rows.append(r)
        drop = price * 0.9
        r_drop = evaluate(drop, args.fba, args.landed, args.other,
                          args.commission, args.ad_cost)
        flag = "" if r["margin"] >= args.target_margin else "  << 未达门槛"
        print(f"{fmt_money(price):>7} {fmt_money(r['commission_fee']):>7} "
              f"{fmt_money(r['variable']):>9} {fmt_money(r['gross']):>11} "
              f"{r['margin']:>7.1%} {r_drop['margin']:>10.1%} "
              f"{fmt_money(r['after_ad']):>9}{flag}")

    print("=" * 78)
    print(f"最低可售价（{args.target_margin:.0%} 毛利）：${floor:.2f}")
    if args.ad_cost:
        print(f"单件广告花费：${args.ad_cost:.2f}")

    print()
    print("保本 ACOS（广告订单刚好不亏的上限）")
    for r in rows:
        if r["margin"] > 0:
            print(f"  ${r['price']:.2f} -> {r['breakeven_acos']:.1%}"
                  f"   （目标 ACOS 应显著低于此值）")
        else:
            print(f"  ${r['price']:.2f} -> 毛利为负，无保本 ACOS")

    print()
    bad = [r for r in rows if r["margin"] < args.target_margin]
    if bad:
        print(f"未达 {args.target_margin:.0%} 门槛的有 {len(bad)} 个价格点："
              + "、".join(f"${r['price']:.2f}" for r in bad))
        print(f"需要提价到 ${floor:.2f} 才能过线，"
              f"或把变动成本压到 ${floor * (1 - args.commission - args.target_margin):.2f} 以下")
    else:
        print(f"全部价格点均达到 {args.target_margin:.0%} 硬门槛。")


if __name__ == "__main__":
    main()
