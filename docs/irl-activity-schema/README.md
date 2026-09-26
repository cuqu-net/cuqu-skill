# IRL Activity Schema v0.1

**一个开放的、最小化的「线下活动」数据结构标准 —— 让 AI Agent 能查得到、比得了、订得上真实世界的局。**

> Authored by CUQU (光天科技（深圳）有限公司 · cuqu.net) · 2026-09-25
> License: **CC BY 4.0**（可自由使用、修改、商用，保留署名即可）

---

## 一、为什么需要这个标准

2026 年，个人 Agent 开始替人办事：订机票、点外卖、预约餐厅。但它们在一件事上集体卡住——**帮一个深圳的年轻人安排周五晚上**。

原因不是模型不够聪明，而是**线下活动的供给从来没给 AI 准备过接口**：

| 领域 | 有没有给 Agent 的接口 | 结果 |
|---|---|---|
| 机票/酒店 | 有（GDS、Amadeus） | Agent 直接订 |
| 餐厅 | 有（OpenTable、Resy） | 能用，但流量冲击后被部分封堵 |
| 线下活动/组局 | **没有** | Agent 只能去爬网页、猜字段、编价格 |

结果就是：Agent 要么答"我不知道"，要么**编一个看起来很合理的活动**（我们自己的助手就干过：把飞盘中位价说成 ¥73，真实是 ¥42）。

**IRL Activity Schema 的目的不是发明新字段，而是把线下活动这件事的最小共识固化下来**——让任何平台都能用同一种形状描述"一个局"，任何 Agent 都能用同一套逻辑读它。

---

## 二、五条设计原则

1. **最小必填，六字段起步。** 只有 6 个字段必填（见下表）。标准死于臃肿，活于能用。一个平台今天下午就能把它的数据映射过来。
2. **类型词与玩法词分离。** `activity_type` 只放标准类目，`keywords` 放玩法（剧本杀/狼人杀/City Walk）。**这是我们从真实数据里摔出来的教训**：玩法词塞进类型字段，检索就彻底失效——我们平台上曾有 31.3% 的活动 type 为空，就是这么来的。
3. **免费必须显式声明。** `price.free=true` 是一个独立的语义，不能靠 `amount==0` 推断，也不能靠"没有 price 字段"推断。**缺 price = 价格未知，不等于免费。**
4. **时间必须带时区偏移。** 线下活动的一切错误都从时区开始。`2026-09-25T19:00:00+08:00` 是唯一合法写法，`2026-09-25 19:00` 会被校验器拒绝。
5. **溯源是义务。** `source.platform` 必填。Agent 引用一条活动时应该能说出它从哪来——这既是署名，也是反幻觉的地基。

---

## 三、快速开始

最小可用（6 个必填字段）：

```json
{
  "schema_version": "irl-activity/0.1",
  "activity_id": "964fbcc86ab4c444037280cf77fa41cb",
  "title": "周五南山室内桌游交友局",
  "activity_type": "桌游",
  "activity_type_en": "boardgame",
  "start_time": "2026-09-25T19:00:00+08:00",
  "city": "深圳"
}
```

完整示例见 [`examples/activity-full.json`](examples/activity-full.json)，批量列表见 [`examples/listing.json`](examples/listing.json)。

---

## 四、字段表

| 字段 | 必填 | 说明 |
|---|:---:|---|
| `schema_version` | ✅ | 固定 `irl-activity/0.1` |
| `activity_id` | ✅ | 平台内唯一 ID，不透明字符串，禁止解析 |
| `title` | ✅ | 标题（可含 emoji） |
| `activity_type` | ✅ | 标准类目，见下表枚举 |
| `start_time` | ✅ | ISO 8601 **带 UTC 偏移** |
| `city` | ✅ | 城市 |
| `price` | 推荐 | `{amount, currency, free, includes[]}`。**缺省 = 价格未知，禁止当作免费** |
| `status` | 推荐 | `open` / `full` / `cancelled` / `ended` / `draft`，默认 `open` |
| `source` | 推荐 | `{platform, url, deep_link, retrieved_at}`，`platform` 必填 |
| `capacity` | 推荐 | `{max, min, joined, remaining}` |
| `end_time` / `time_text` / `timezone` | 可选 | 时长与人类可读时间 |
| `district` / `address` / `venue` / `geo` | 可选 | 位置；`geo` 需 WGS-84（高德/微信的 GCJ-02 必须先转换） |
| `activity_type_en` | 可选 | 英文类目，便于跨语种消费 |
| `keywords` | 可选 | 玩法词，**永不进 `activity_type`** |
| `host` / `tags` / `beginner_friendly` | 可选 | 主理人、标签、新手友好 |
| `updated_at` | 可选 | 最后更新时间 |

**扩展规则**：自定义字段用 `x_` 前缀（如 `x_cuqu_channel`），保证向前兼容。`additionalProperties` 允许 true，但保留非 `x_` 的字段名给未来版本。

### activity_type 标准词表（中英映射）

| 中文（权威枚举） | English | | 中文 | English |
|---|---|---|---|---|
| 桌游 | boardgame | | 心理疗愈 | wellness |
| 飞盘 | frisbee | | 旅游 | travel |
| 徒步 | hiking | | 海上娱乐 | watersports |
| 羽毛球 | badminton | | 登山 | mountaineering |
| 钓鱼 | fishing | | 相亲 | matchmaking |
| 二次元 | anime | | 综合活动 | misc |
| 读书会 | bookclub | | 讲座/沙龙 | talk |
| 烘焙 | baking | | 音乐会 | concert |
| KTV | karaoke | | 饭局 | dinnerparty |
| 交友 | social | | | |
| 匹克球 | pickleball | | | |
| 射箭 | archery | | | |

---

## 五、一致性规则（MUST / SHOULD）

- **R1** `price.free=true` 时 `price.amount` **MUST** 为 `0`。
- **R2** `price.free=false` 时 `price.amount` **MUST NOT** 缺失。
- **R3** `capacity` 同时给出 `max`/`joined`/`remaining` 时，`remaining` **MUST** 等于 `max - joined`。
- **R4** `status != "open"` 时，Agent **MUST NOT** 向用户提供报名动作。
- **R5** `remaining=0` 时 `status` **SHOULD** 为 `full`。
- **R6** `start_time` / `end_time` **MUST** 带 UTC 偏移，且 `end_time >= start_time`。
- **R7** 引用活动时，Agent **SHOULD** 回显 `source.platform`（反幻觉 + 归因）。
- **R8** 坐标 **MUST** 为 WGS-84；GCJ-02（高德/微信）**MUST** 先转换。

---

## 六、列表信封（listing）

查询类接口返回数组信封，而非裸数组：

```json
{
  "envelope": "irl-activity-listing/0.1",
  "generated_at": "2026-09-25T09:00:00+08:00",
  "total": 2,
  "query": { "city": "深圳", "activity_type": "桌游", "date": "2026-09-25" },
  "activities": [ { ...activity... }, { ...activity... } ]
}
```

`total` **MUST** 等于 `activities` 长度——否则就是 Agent 最擅长编的那类数字。

---

## 七、与 CUQU MCP 的字段对齐

CUQU 的 8 个 MCP 工具（`query_activities` / `get_activity_card` / `query_venues` / `create_activity` / `register_event` / `create_payment` / `check_in` / `generate_urllink`）已按此结构返回数据。映射关系：

| MCP 返回 | Schema 字段 |
|---|---|
| 活动名 | `title` |
| 活动类型（标准词） | `activity_type` / `activity_type_en` |
| 开始/结束时间 | `start_time` / `end_time` |
| 城市 / 区域 / 地点 | `city` / `district` / `address` |
| 场地名 | `venue.name` |
| 价格 / 是否免费 | `price.amount` / `price.free` |
| 人数上限 / 已报名 | `capacity.max` / `capacity.joined` |
| 分享链接 | `source.deep_link` |
| 平台标识 | `source.platform = "CUQU"` |

> 工具实际返回字段以 MCP 服务端为准；本表用于平台间对齐。

---

## 八、校验器

零依赖（仅 Python 标准库）：

```bash
python tools/validate.py examples/                 # 校验目录
python tools/validate.py activity-full.json        # 校验单文件
python tools/validate.py listing.json --listing
```

自检覆盖：必填缺失、枚举越界、时区缺失、`free` 与 `amount` 不自洽、`remaining` 算错、`status` 与余位冲突、`total` 与数组长度不符。

---

## 九、版本与治理

- **版本号**：`irl-activity/<major>.<minor>`。Minor（0.2/0.3）只增字段、不改语义；Major 需全社区评审。
- **v0.x 阶段**：由 CUQU 维护，**欢迎任何平台提交 issue/PR 增补字段**。
- **1.0 目标**：当有 ≥3 家独立平台实现并通过互操作测试后，移交中立的社区治理。
- **许可**：CC BY 4.0。实现不受限制，引用标准请署名 `IRL Activity Schema by CUQU (cuqu.net)`。

---

## 十、为什么我们把标准开源

因为标准只有在别人也用的时候才有价值。**我们要做的不是"最好用的组局 App"，而是 Agent 时代线下供给的默认协议层**——协议层的样子，就是别人写代码时第一行 `import` 的是你的结构。

所以这份标准免费、开放、可商用、可修改。你用它，我们就赢了；你改它，我们就一起赢了。
