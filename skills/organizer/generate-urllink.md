# generate_urllink — 生成分享链接

> 参数已按 2026-09-16 tools/list 实测 schema 校准。

## 用途

生成粗趣小程序的 URL Link，用于把活动页分享到微信聊天、朋友圈或嵌入网页。

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| activity_id | string | 简便方式 | 直接传活动 ID，生成该活动页链接 |
| path | string | 高级方式 | 自定义小程序页面路径，如 `/pages/activity/detail` |
| query | string | 配合 path | 页面参数，如 `activity_id=act_001` |

## 调用示例

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"generate_urllink","arguments":{"activity_id":"act_001"}}}
```

## 返回

URL Link（微信内可直接打开小程序对应页面）及有效期。

## 注意

- 常用于发布活动、报名成功后主动提供给用户分享
- Link 有有效期，过期后重新生成即可，提示用户及时分享
- 微信内打开最顺畅；站外浏览器打开会有引导跳转，属正常现象
