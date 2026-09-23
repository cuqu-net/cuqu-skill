# query_activities — 查询活动

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

按条件搜索粗趣平台的线下活动列表。用户问"有什么活动""周末玩什么""找搭子"时首先调用本工具。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_type | string | 建议必传 | 活动类型，**精确匹配**。标准词：桌游聚会、飞盘、徒步、羽毛球、钓鱼、二次元、读书会、烘焙 |
| date | string | 否 | 日期，如 2026-09-19 |
| location | string | 否 | 地点/城市关键词，如 深圳、南山 |
| keyword | string | 否 | 其他关键词，如 阿瓦隆、新手局 |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_activities","arguments":{"activity_type":"桌游聚会","location":"深圳"}}}
```

## 返回

`{success, count, activities: [...]}`，每项含：id、title、type、date、time、location、price、
max_participants、**current_participants**（已报名数）、organizer、description、tags、
**cover_url**（活动封面图 URL）、**h5_url**（官网活动 H5 页，可直接分享给用户）。

## 注意

- **匹配行为（2026-09-23 实测）**：activity_type 对 type 字段做子串包含匹配（大小写敏感），
  不匹配 title/tags。如 "飞盘" 可命中 type="飞盘/球类" 的活动；"狼人杀" 这类玩法词命中为 0，改用 keyword 参数
- **全量拉取**：不传 activity_type 返回当前全部活动（找局首选，再在结果里按用户条件筛选）
- 结果为空时先全量拉取确认后台是否有活动，再逐步放宽 location/date
- 展示时按时间排序，价格用 ¥ 前缀（0 元标"免费"），current_participants≥max_participants 标"已满员"
- 拿到列表后追问用户要不要看某个详情或直接报名，一次最多推荐两个选项
