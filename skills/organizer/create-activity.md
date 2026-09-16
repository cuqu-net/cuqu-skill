# create_activity — 发布活动（主理人）

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

帮主理人在粗趣平台发布新的组局活动。**写操作，执行前必须确认全部字段。**

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 活动标题 |
| activity_type | string | 是 | 活动类型（标准词同 query_activities） |
| date | string | 是 | 日期，如 2026-09-19 |
| time | string | 是 | 时间段，如 14:00-18:00 |
| location | string | 是 | 活动地点 |
| max_participants | number | 否 | 人数上限 |
| price | number | 否 | 费用（元，免费填 0） |
| description | string | 否 | 活动介绍、规则说明 |
| organizer | string | 否 | 主办方名称 |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"create_activity","arguments":{"title":"周六狼人杀新手局","activity_type":"桌游聚会","date":"2026-09-19","time":"14:00-18:00","location":"深圳 南山 科兴科学园桌游吧","max_participants":12,"price":58,"description":"新手友好，含教学，提供饮品"}}}
```

## 返回

发布结果：活动 ID、状态（审核中/已发布）、分享路径。

## 注意

- 发布前把全部字段列给用户确认，缺的字段（尤其是日期、时间、地点、价格）主动追问补齐
- 发布成功后建议用户用 `generate_urllink` 生成分享链接发朋友圈/群
- 主理人资质类错误（如未开通发活动权限）原样转述提示
