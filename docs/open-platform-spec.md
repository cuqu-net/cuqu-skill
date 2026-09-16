# 粗趣开放平台后端规格（P1）

> 目标：复刻照面 open.zm.bio 的「扫码拿 Key → Agent 装技能 → Agent 代报名」链路，服务粗趣 AI Native 报名。
> 本文档是给后端的对接规格，前端原型见 `cuqu-open-platform/index.html`（mock 已按此规格预留接口名）。

## 一、总体架构

```
用户 ──微信扫码──> 开放平台(open.cuqu.net) ──签发──> 个人 API Key(cq-sk-*)
用户 ──复制提示词──> AI Agent ──npx skills add──> GitHub cuqu/cuqu-skill
Agent ──Bearer cq-sk-xxx──> API 网关 ──uid 鉴权──> cuqu MCP / 业务后端
```

## 二、开放平台接口（/api/open/*）

统一响应格式 `{code:0, data:..., msg:''}`；登录态用 `Authorization: Bearer <session_token>`（会话 token，区别于 API Key）。

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/open/qr/create` | POST | 生成微信扫码登录二维码，返回 `qrId` |
| `/api/open/qr/status?qrId=` | GET | 前端 2.5s 轮询；返回 `{status:'waiting'\|'success', token?}` |
| `/api/open/apikey` | GET | 查询当前用户 API Key（首次访问自动签发） |
| `/api/open/apikey/refresh` | POST | 刷新：作废旧 Key、签发新 Key，返回新值 |

### 微信扫码登录实现选项

| 方案 | 说明 | 建议 |
|------|------|------|
| A. 微信开放平台网站应用扫码 | 需已认证的开放平台账号 + 回调域名 | 若已有资质，首选 |
| B. 公众号网页授权（中转页） | 用户长按/扫二维码进公众号授权页，后端轮询绑定状态 | 最快落地，1-2 天 |
| C. 小程序码中转 | 生成带 scene 的小程序码，用户小程序内确认 | 体验最好，依赖小程序改版 |

**Key 规范**：前缀 `cq-sk-` + 32 位随机 hex；**库里只存 SHA-256 哈希**，明文仅签发时返回一次；每用户同时只保留一把有效 Key；刷新即作废旧 Key。

## 三、Agent 调用链鉴权（核心改造点）

### 现状

cuqu MCP 部署在 dashscope 网关（百炼），当前那把 `sk-ws-` 是**平台级 Key**——它能操作全部用户的数据，**绝对不能**下发给 C 端用户。

### 方案对比

| 方案 | 做法 | 工作量 | 建议 |
|------|------|--------|------|
| A. 自建 Agent 网关（推荐） | 新建 `agent.cuqu.net`（Cloudflare Workers 即可）：接收 Bearer `cq-sk-` → 校验哈希 → 查出 uid → 以平台身份调用 dashscope MCP，把 uid 注入工具参数 | 2-3 天 | **首选**：不动现有 MCP，渠道统计、限流、审计都在自己手里 |
| B. MCP Server 直接支持个人 Key | cuqu 后端 MCP 实现 OAuth/token 鉴权，绕开 dashscope 直连 | 3-5 天 | 长期方向，但改动大 |
| C. dashscope 侧多 Key | 每用户建一个百炼 Key | 不可行 | 管理复杂、成本不可控 |

### 方案 A 网关细节

- 请求路径：`POST agent.cuqu.net/mcp`（透传 JSON-RPC）
- 鉴权：`Authorization: Bearer cq-sk-...` → SHA-256 查表 → uid
- 注入：调用下游 `register_event`/`check_in` 等用户身份工具时，网关在 arguments 里追加 `uid`（Skill 文档已注明"无需手动传 uid"）
- Skill 里的 `CUQU_MCP_HOST` 改为 `https://agent.cuqu.net/mcp`
- 限流建议：每 Key 60 次/分钟（对齐 5QPS 压测目标量级）
- 日志：记录 qps、工具名、uid、channel —— 这就是 P2 渠道看板的数据源

## 四、channel 渠道标识（P2）

- `register_event` / `create_activity` 的 arguments 增加可选 `channel` 字段
- Agent 报名固定上报 `channel:"ai-agent"`（已写进 SKILL.md 通用规则第 4 条）
- 后端报名表加 `channel varchar(32)` 列，默认 `miniapp`
- 数据用途：统计 Agent 渠道带来的报名量/GMV，衡量 skill 分发效果；后续可细分 `ai-agent/claude-code`、`ai-agent/workbuddy` 等（由 SKILL.md 按宿主填）

## 五、上线检查清单

- [ ] GitHub 建仓 `cuqu/cuqu-skill`，推送本包 `skills/` 内容
- [ ] `npx skills add cuqu/cuqu-skill -g` 实测安装（Claude Code / Codex 各测一次）
- [ ] 网关部署 + 全链路测试（扫码 → Key → Agent 装技能 → query_activities → register_event）
- [ ] 旧平台级 `sk-ws-` Key 作废轮换（已在 9-11 会话中暴露过）
- [ ] 开放平台域名建议 `open.cuqu.net`（Cloudflare Pages/Workers，与主站同账号）
- [ ] ICP 合规：域名在国内解析需备案；若走 Cloudflare 海外节点与主站一致，保持口径统一

## 六、里程碑建议

| 阶段 | 内容 | 验收标准 |
|------|------|----------|
| M1（本周） | 仓库 + 网关 + 扫码登录 | 内部用 Agent 完成一次真实报名 |
| M2（下周） | 开放平台页上线 + Key 刷新 | 3 个外部用户完成安装并报名 |
| M3（月底） | channel 看板 + 复盘 | 渠道数据进 CEO 简报 |
