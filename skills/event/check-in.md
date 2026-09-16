# check_in — 活动签到

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

活动现场签到核销。用户到场后说"我到了""签到"时调用。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_id | string | 是 | 活动 ID |
| phone | string | 凭证之一 | 报名手机号 |
| code | string | 凭证之一 | 签到码（报名成功后平台下发） |
| user_id | string | 凭证之一 | 用户 ID |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"check_in","arguments":{"activity_id":"act_001","phone":"1532380xxxx"}}}
```

## 返回

签到结果：成功/失败及原因（凭证无效、不在签到时间窗口等）。

## 注意

- 凭证按可用性任选其一：优先 code，其次 phone
- 若用户未报名则先引导报名
- 签到失败时转述原因并提示现场找主理人处理，不反复重试
