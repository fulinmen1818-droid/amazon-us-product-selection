# 数据采集与口径

## 数据源分层

| 层级 | 来源 | 用途 | 可信度 |
|---|---|---|---|
| A 级 | 亚马逊官方费率表、FBA 计算器、ABA 品牌分析、商机探测器、评论原文、证书/专利文件 | 成本、需求、权利状态 | 已核实 |
| B 级 | 第三方工具（卖家精灵、Helium 10、Jungle Scout、Keepa、Sorftime）、类目洞察 MCP | 销量估算、流量结构、CPC、竞争密度 | 工具估算 |
| C 级 | 未取得的数据 | — | 显式标"待补证" |

**原始资料真实，不代表据此作出的判断已经证实。** 官方费表可信，但选错包装档位测算仍会错；证书可查，不代表覆盖你的材料、工厂和使用方式。

## 工具映射

数据源为类目洞察类 MCP（如西柚找词 xiyou-insight）。未接入时可用店铺页抓取 + 亚马逊前台数据替代，但销量与流量只能标 B 级。

| 采集内容 | 工具 | 关键参数 |
|---|---|---|
| 类目确认 | `search_market_insight_categories` | 关键词或节点 |
| 市场规模/趋势 | `get_category_market_size_trends` | categoryId、时间窗 |
| 淡旺季 | `get_category_seasonality` | 返回全 0 表示无季节性数据，不要写成"无季节性" |
| 头部竞品 | `get_category_sales_ranking` | categoryId + **query 按标题词筛选** + reportPeriod |
| 新品机会 | `get_category_new_release_opportunity_trends` | — |
| 价格带竞争 | `get_category_price_segment_trends` | — |
| 品牌集中度 | `get_category_brand_market_size` | — |
| 评论/星级分布 | `get_category_review_analysis` | — |
| 竞品基础信息 | `get_asin_info` | 批量 ASIN（单次建议不超过 25 个） |
| 近 30 天销量 | `get_asin_orders_last_30_days` | 批次最多 100 个 ASIN |
| 流量结构 | `get_asin_traffic`、`get_asin_traffic_trends` | 自然位/广告位分开 |
| 关键词反查 | `get_asin_keywords`、`get_asin_keywords_monthly` | — |
| 关键词竞争格局 | `get_keyword_asin_analysis` | — |
| 关键词指标 | `get_keyword_info` | 批量关键词，返回周搜索量/难度/CPC/CVR |
| 关键词机会 | `find_keyword_opportunities` | — |
| ABA 趋势 | `get_keyword_aba_trends` | — |
| 变体结构 | `get_asin_variations`、`get_primary_asin_children` | 父体下钻 |
| 广告结构 | `get_parent_asin_ad_overview`、`get_parent_asin_ad_keywords` | 头部广告依赖度 |
| 类目洞察资源 | `generate_category_insight_resource` | 返回 resourceId，**同一任务内复用，不要重复生成（每次消耗额度）** |

## 关键参数经验

- **categoryId 与 resourceId 必须配对复用**。类目洞察类接口通常要求先 `generate_category_insight_resource` 生成 resourceId，同一次调研内所有类目查询复用同一个；重复生成会重复扣额度。
- **`get_category_sales_ranking` 的 query 参数是最有用的功能**。它按标题词筛选，能直接回答"某个主题在类目内有多少在售 ASIN、头部多少销量"，是类目扫描与主题筛选的核心手段。
- **`reportPeriod` 选 `last30days`**，与关键词周数据对齐时注意窗口差异（销量 30 天，关键词 1 周）。

## 返回体处理（重要）

类目榜单接口单次返回常有 100K–300K 字符，直接读会超限。处理方式：

1. 把结果落盘为文件（工具结果目录下会保留原始文件）
2. 用 Python 读取 JSON，只提取需要的字段
3. 不要试图在对话里浏览原始返回

解析模板：

```python
import json
d = json.load(open(path, encoding='utf-8'))['data']
L, total = d['list'], d['total']
f = lambda x: float(x) if x not in (None, '') else 0.0

sales  = [it['metrics']['sales']['value'] or 0 for it in L]
price  = [f(it['asinInfo']['priceDistribution'].get('value')) for it in L]
rating = [it['asinInfo'].get('ratings') or 0 for it in L]
days   = [it['asinInfo'].get('listedDays') or 99999 for it in L]
brand  = [it['asinInfo'].get('brand') for it in L]
```

## 字段陷阱

| 陷阱 | 说明 | 正确做法 |
|---|---|---|
| **店铺页价格是当地币种** | 抓取卖家店铺页时，价格可能按汇率显示为 CNY（如 `CNY 106.67`），不是美元 | 价格一律从 `get_asin_info` 取；抓取页只用于拿 ASIN 清单与标题 |
| **`size.package` / `weight.package` 可能是字符串** | 不是 dict，`.get()` 会报 AttributeError | 直接 `str(sz.get('package'))` 打印 |
| **销量是档位化的** | 返回 700 / 600 / 300 / 200 / 100 / 50 / 0 这类档位，不是精确值 | 报告中标"估算"，不要写成精确销量 |
| **评分归属** | 变体共享评分，子体评分数可能属于父体 | 记录评分口径，变体单独成表 |
| **`listedDays` 为 None** | 老品可能无上架天数 | 按 99999 处理，不要当成新品 |
| **`trafficScore.summary` 是流量结构** | 自然位/广告位占比只说明流量来源 | 不能直接推断销量来源 |
| **搜索量为 0** | 可能是无数据，不是无需求 | 标"无 ABA 数据"，与"需求为零"区分 |

## 口径规则

**销量与流量必须分开记录。** 排名、流量估算、销量估算分别记录，不能互相替代。自然位占比高说明流量结构健康，不代表卖得好；转化才是销量的直接前提。

**父子变体不平摊。** 父体销量不能平均分配给子体，各子体需分别估销。同一父体下多个颜色不能当作多个独立品牌来统计集中度。

**关键词按购买意图聚类。** 同一购买意图的词归为一组，不能把多个词的搜索量直接相加当作独立买家数——同一买家会用多个词，相加会重复计算需求。

**ABA 排名不是搜索量。** 排名是相对位置，不能当绝对需求量用。

**Google Trends 只说明趋势不说明销量。** "bow cake" 的热度不能直接当作某款缎带插牌的销量依据；区分"广泛审美趋势"与"具体购买需求"。

**主题大词与品类精准词是两回事。** 主题派对词（如 `dinosaur birthday decorations`）通常是主题插牌词的 5–10 倍。主题派对词流量大但竞争激烈、CPC 高；精准词流量小但转化高、CPC 低 30–50%。判断进入策略时必须两个都取。

## 店铺页抓取（无 MCP 时的替代）

卖家店铺页可直接抓取 ASIN 清单，用于反向拆解某个卖家的产品线：

```bash
curl -sL --compressed \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  -H "Accept-Language: en-US,en;q=0.9" \
  "https://www.amazon.com/s?me=<SELLER_ID>&marketplaceID=ATVPDKIKX0DER" \
  -o seller.html --max-time 45
```

要点：必须带浏览器 UA 与 `--compressed`；需分页或用 `&page=2` 取全量。通用网页抓取工具常被 Amazon 拦截（503），curl 直取成功率更高。

抓到后提取 `data-asin` 与标题，再用 `get_asin_info` 补齐真实价格、FBA 费、尺寸重量、上架时间。
