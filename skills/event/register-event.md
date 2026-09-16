# register_event — 报名活动

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

为当前用户报名指定活动。**写操作，执行前必须向用户确认。**

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_id | string | 是 | 活动 ID |
| user_name | string | 是 | 报名人姓名 |
| phone | string | 是 | 联系电话 |
| note | string | 否 | 备注（如人数、特殊需求） |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"register_event","arguments":{"activity_id":"act_001","user_name":"李小白","phone":"1532380xxxx"}}}
```

## 返回

报名结果：订单号、应付金额（0 元活动直接报名成功）、报名状态。

## 注意

- 执行前复述：活动名 + 时间 + 金额，用户说"确认/报名/可以"后再调用
- 报名成功后若有应付金额，追问是否现在支付（引导 `create_payment`）
- 重复报名、活动已满等业务错误，原样转述平台返回的提示，不自动重试
- 不要向用户展示订单号等内部标识，说"报名成功"即可
- 渠道标识（`channel: "ai-agent"`）为规划字段，当前 schema 暂无此参数，后端支持后按通用规则第 4 条执行
