# query_venues — 查询场地

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

按地点、类型、容纳人数检索粗趣合作场地。主理人找场地、用户问"哪里能办活动"时调用。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| location | string | 否 | 地点/城市关键词，如 深圳、南山 |
| venue_type | string | 否 | 场地类型：桌游吧、运动场、户外、咖啡馆等 |
| min_capacity | number | 否 | 最少需容纳人数 |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_venues","arguments":{"location":"深圳","venue_type":"桌游吧","min_capacity":20}}}
```

## 返回

场地列表：名称、区域、容纳人数、人均费用、联系方式/预订方式。

## 注意

- 结合活动类型给建议（如 12 人狼人杀 → 推荐 min_capacity≥12 的桌游吧）
- 场地实际档期需联系场地方确认，向用户说明这一点
- 可以接着引导："要我帮你在意向场地发一个活动吗"
