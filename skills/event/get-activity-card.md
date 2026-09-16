# get_activity_card — 活动详情卡片

## 用途

获取单个活动的结构化详情卡片，含活动介绍、主办方信息和小程序直达链接。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_id | string | 是 | 活动 ID，来自 query_activities 的返回 |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_activity_card","arguments":{"activity_id":"act_123"}}}
```

## 返回

活动卡片：完整介绍、时间地点、价格、余位、小程序页面路径。

## 注意

- activity_id 是内部标识，调用需要时直接使用，但不要向用户解释"这是 activity_id"
- 卡片中的小程序链接可配合 `generate_urllink` 生成可分享的 URL Link
- 展示详情后追问是否报名，不自动报名
