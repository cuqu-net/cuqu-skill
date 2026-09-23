# 粗趣 skill

为 AI Agent 提供「粗趣（CUQU找搭子）」开放能力的 Skill 集合，支持活动检索、报名、支付、签到，以及主理人发活动、找场地、生成分享链接等能力。

> 粗趣是深圳本地青年线下兴趣社交平台（官网 https://cuqu.net），覆盖桌游/飞盘/徒步/羽毛球/二次元/钓鱼等 100+ 兴趣品类。本 Skill 通过 MCP 协议（Streamable HTTP）连接粗趣服务。

## 安装

```
npx skills add liqicuhk-ui/cuqu-skill -g
```

> 仓库路径以实际上线为准（GitHub `liqicuhk-ui/cuqu-skill`，或替换为光天科技组织名）。

### 一键安装提示词

把下面这段提示词发给任意支持 Skills 的 Agent（Claude Code、Codex、Cursor、WorkBuddy 等）即可完成安装：

```
请帮我安装粗趣 skill：
npx skills add liqicuhk-ui/cuqu-skill -g
```

## 配置

使用前需要配置两个环境变量：

```
export CUQU_MCP_HOST=https://agent.cuqu.net/mcp
export CUQU_API_KEY=cq-sk-xxxxxxxx
```

获取方式：

1. 打开粗趣开放平台（上线后地址见官网 cuqu.net 公告）
2. 使用微信扫码登录
3. 在首页「一键安装 Skill」复制提示词，其中已包含与你账号绑定的 Host 与 API Key；Key 泄露时可在同处点「刷新 Key」重新生成

> API Key 与你的粗趣账号（uid）绑定，报名、签到等用户身份操作自动关联，无需手动传 uid。真实 API Key 只保存在本地环境变量中，禁止写入仓库或提交远程。

## 使用

安装后直接用自然语言与 Agent 对话即可：

```
"这周末深圳有什么桌游局"
"帮我报名周六的飞盘活动"
"这个活动怎么签到"
"我是主理人，帮我发一个周日下午的羽毛球活动"
"找几个能容纳 20 人桌游的场地"
"生成这个活动的分享链接"
```

## 线上状态（2026-09-23）

- 网关 `https://agent.cuqu.net/mcp` 已上线，对接真实后台数据（非 mock）
- 官网 AI 可读活动页：https://cuqu.net/activities/list/ （静态 SSR + schema.org Event，每日自动更新）
- AI 助手导读：https://cuqu.net/llms.txt
- 实测：单次调用延迟约 1.2s（上游 dashscope MCP），单 Key 限流 60 req/min

## 功能

| 能力 | 说明 | 文档目录 |
|------|------|----------|
| 活动检索 | 按类型/城市/日期搜索活动 | [`skills/event/query-activities.md`](skills/event/query-activities.md) |
| 活动卡片 | 获取活动详情卡片（含小程序链接） | [`skills/event/get-activity-card.md`](skills/event/get-activity-card.md) |
| 活动报名 | 报名指定活动 | [`skills/event/register-event.md`](skills/event/register-event.md) |
| 支付 | 为报名订单创建支付 | [`skills/event/create-payment.md`](skills/event/create-payment.md) |
| 签到 | 活动现场签到核销 | [`skills/event/check-in.md`](skills/event/check-in.md) |
| 发布活动 | 主理人发布组局 | [`skills/organizer/create-activity.md`](skills/organizer/create-activity.md) |
| 场地查询 | 按城市/类型/人数找场地 | [`skills/organizer/query-venues.md`](skills/organizer/query-venues.md) |
| 分享链接 | 生成小程序 URL Link | [`skills/organizer/generate-urllink.md`](skills/organizer/generate-urllink.md) |

## 自检

配置完成后可运行连通性测试（需要 Python 3）：

```
python scripts/check-mcp.py
```

## 版本

当前版本：**0.1.0**

## 许可证

Apache-2.0 — Copyright © 2026 光天科技（深圳）有限公司
