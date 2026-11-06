# Amazon US Product Selection

**A decision framework for Amazon US product research.**
Turns "I think this could work" into "here is the evidence that it works, and here is what is still missing."

**English** | [中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Method](https://img.shields.io/badge/method-V2.1-2ea44f.svg)](#methodology-version)
[![Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-6f42c1.svg)](#install)

---

## The problem

Product research rarely fails because you picked the wrong category. It fails because **you calculated a good opportunity using the wrong cost structure**.

A real case: the category leader was selling 15,419 units/month, rated 4.7, holding 42.5% of category sales, ranked #1 in its BSR node. Every surface signal said "go." Then you plug in the actual numbers — $6.99 price, $3.51 FBA fee, 15% referral fee, plus landed cost — and the pre-ad gross margin is **11.5%**. It isn't profitable. It's running on volume and cash flow. A new entrant without its sourcing scale that matches its price is matching its losses.

The opposite happens just as often: the first page is wall-to-wall 5,000-review listings, so you walk away — without noticing those listings are buying rank at a loss, and the reviews are all complaining about the same defect you could design around.

**These situations don't call for more data. They call for a better method.**

---

## What it does

### 1. Judge whether a single product is viable

Give it a competitor ASIN. It returns one of four states — **Eliminate / Evidence Needed / Sample Testing Allowed / Scale Allowed** — with a line-by-line evidence trail. No "consider carefully." That isn't a decision.

### 2. Scan a category for alternative directions

When your original direction is dead, the answer isn't "pick another random product." It's **change the price structure**. Drill into sub-nodes, compute the price floor for each, validate against new-launch survival data, and find where margin actually holds.

### 3. Rank themes within a product line

Once the direction is set, compare candidate themes on six metrics that can be computed in bulk: demand volume, supply density, demand-to-supply ratio, review barrier, price feasibility, ad dependency.

---

## Three hard rules

These are the skeleton. Violate any one and the entire analysis is void.

**Hard gates before scoring.**
Safety, ≥30% pre-ad gross margin, IP clearance. Fail any of them and the product goes to Eliminate or Evidence Needed — it does not enter the ranking. The six-dimension score only answers "which of the viable candidates first." It can never lift an unviable product up.

**Missing data means unknown — not zero risk, and not zero demand.**
No data, mark it "evidence needed." And separate **critical gaps** (safety, core cost, packaging tier, IP status) from **secondary gaps** (5-year trend, precise unit count). Only critical gaps block sample testing.

**No amount of competitor data can trigger scale-up.**
Scale-up requires your own operating data: actual sell-through, actual margin, actual return rate. Competitor volume and tool estimates can support sample testing at most.

---

## What's inside

```
amazon-us-product-selection/
├── SKILL.md                    Core flow: 5-step decision, 4 states, execution SOP
├── references/
│   ├── methodology.md          Full method: 6-dimension framework, scoring, audit tables
│   ├── calculations.md         3-tier profit model, price floor, 7 measured FBA tiers
│   ├── data-sources.md         Data source options, field requirements, degradation rules
│   ├── compliance-us.md        Children's products, small parts, CPC, eFiling, IP
│   └── cases/
│       ├── case-competitor.md  Single-ASIN research (15 competitors compared)
│       ├── case-category.md    Category scan and alternative directions
│       └── case-theme.md       Theme prioritization (24 candidates)
├── scripts/
│   └── margin_calc.py          Margin, price floor, price-cut stress test, break-even ACOS
└── assets/
    └── report-template.md      Three report skeletons + testing parameter sheet
```

---

## Install

This is an AI Agent Skill (Claude Skill format), loadable by any agent that supports the format.

**WorkBuddy**
```bash
git clone https://github.com/fulinmen1818-droid/amazon-us-product-selection.git \
  ~/.workbuddy/skills/amazon-us-product-selection
```

**Claude Code**
```bash
git clone https://github.com/fulinmen1818-droid/amazon-us-product-selection.git \
  ~/.claude/skills/amazon-us-product-selection
```

Then just ask. The skill triggers automatically:

> Can this competitor B0XXXXXXXX work?
> I'm dropping this product — what else is in this category?
> Here's a seller's storefront. Which themes are worth doing?
> Selling at $12.99 with $4.36 FBA — is the margin enough?

---

## Use the calculator standalone

No agent required. There is really only one formula:

```
Price floor = (FBA fee + landed cost + other variable costs) ÷ 0.55
```

`0.55 = 1 − 15% referral fee − 30% target margin`

```bash
python scripts/margin_calc.py --price 9.99 11.99 12.99 14.99 --fba 4.36 --landed 1.80
```

```
     Price  Referral   Var. cost  Pre-ad GP   Margin   After -10%   After ads
     $9.99     $1.50       $7.36      $1.13    11.3%         3.1%       $1.13  << below gate
    $11.99     $1.80       $7.36      $2.83    23.6%        16.8%       $2.83  << below gate
    $12.99     $1.95       $7.36      $3.68    28.3%        22.0%       $3.68  << below gate
    $14.99     $2.25       $7.36      $5.38    35.9%        30.4%       $5.38

Price floor (30% margin): $13.38
```

**Why this formula matters most**: if the category's sales-weighted average selling price sits below this number, nobody in that price band is making money. That isn't "intense competition." That's structural loss.

---

## One counter-intuitive finding

At the same price point, **packaging thickness matters more than product design**.

| Product | Price | Box depth | FBA | FBA / price | Pre-ad margin |
|---|---|---|---|---|---|
| 48-pc flat paper cards | $7.99 | 0.5 cm | $2.71 | 34% | **31%** |
| 12-pc 3D candle set | $8.98 | 4.8 cm | $4.21 | 47% | **8%** |

$0.99 apart in price. $1.50 apart in fulfillment. 23 points apart in margin.

Design principles that follow: prefer stackable, nestable form factors under 1 cm deep. Ship "parts + assembly" rather than "finished goods" when you can. More pieces don't cost more to fulfill (FBA prices on dimensions and weight, not piece count) — but they do support a higher perceived price.

---

## Data sources

**This skill does not generate data. It generates judgment. Where your data comes from determines how far the conclusion can go.**

The field requirements, degradation rules, and three access routes are documented in [`references/data-sources.md`](references/data-sources.md). Short version:

| Route | What you get | Cost |
|---|---|---|
| **Category-insight MCP** (reference implementation: Xiyou Insight) | Near-complete field coverage: category rankings, ASIN detail with real FBA fees and packaging dimensions, sales estimates, traffic structure, keyword metrics | Paid, metered in Credits |
| **Existing tool subscriptions** (SellerSprite, Helium 10, Jungle Scout, Keepa) | Sales estimates, keywords, listing age. You still look up FBA fees in Amazon's official table | Already paid for |
| **Manual, zero cost** | Everything critical, just slowly. Official fee tables + product pages + reading reviews yourself | Free |

The reference implementation is **Xiyou Insight** — apply at **https://platform.xydc.com/**. It's listed because its fields map most cleanly onto this method, not because it's required, and not because there's any affiliation, referral, or partnership between this repo and that vendor. Tool names in this repo follow its `xiyou-insight` v1 interface; if the vendor changes the API, check the live `tools/list` rather than trusting the docs.

**Critical distinction**: missing cost fields (FBA fee, landed cost, referral fee) cap the conclusion at **Evidence Needed**. You cannot say "sample testing allowed" without real costs. Missing demand fields (sales, keyword volume, CPC) only reduce ranking precision. Don't conflate the two — that's how you produce a report that looks complete and concludes nothing.

**This repo contains no API keys.** Put your own credentials in local environment variables or your agent's MCP config, never in the repo.

---

## When to use / not use

**Use for**: competitor research, category opportunity scanning, theme selection, margin and price-floor analysis, US compliance review

**Not for**: pure keyword mining, listing copywriting, ad campaign optimization, supplier negotiation

---

## Methodology version

Current: **V2.1**. Key corrections over earlier versions:

- The six-dimension framework was demoted to a research outline and ranking tool — not a purchasing verdict machine
- Added a product safety hard gate (severe injury risk under intended use *and* reasonably foreseeable misuse)
- Unified profit into three tiers; hard gate moved to ≥30% pre-ad gross margin
- Dropped "one threshold for all categories" in favor of A/B/C product pools
- Separated critical data gaps from secondary ones
- Compliance rewritten from "certification checklist" to "product applicability review" (e.g. UL 4200A applies to coin/button-cell battery products, not to everything with a battery)
- Fixed the return-fee rule (referral fee is refunded, minus the lower of $5 or 20% of the referral fee)
- Sample testing changed from fixed KPIs to a fill-in-the-numbers parameter sheet

---

## License

MIT. Use it, modify it, sell with it.

The method comes from real sourcing decisions; all case data is from public platforms. Substitute your own cost structure when you use it — **the formula is universal, the costs are yours.**
