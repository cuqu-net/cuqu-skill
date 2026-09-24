#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUQU找搭子 MCP stdio bridge
============================
把托管网关 https://agent.cuqu.net/mcp (Streamable HTTP) 桥接成 stdio MCP server，
用于 glama.ai 等目录站检测、以及需要 stdio 接入的 MCP 客户端。

- initialize / tools/list：本地直接应答（静态 schema，无需 Key，目录站 introspection 可过）
- tools/call：转发到托管网关，需在环境变量 CUQU_API_KEY 中配置 cq-sk- 开头的用户 Key
  （Key 申领：按 https://cuqu.net/llms.txt 指引扫码签发）

协议：JSON-RPC 2.0 over stdio（每行一个 JSON 对象）
零依赖，Python 3.9+ 可跑。
"""
import json
import os
import sys
import urllib.request

GATEWAY = os.environ.get("CUQU_MCP_URL", "https://agent.cuqu.net/mcp")
API_KEY = os.environ.get("CUQU_API_KEY", "")

TOOLS = [
    {"name": "query_activities",
     "description": "查询CUQU找搭子平台上的线下活动（桌游/飞盘/徒步/羽毛球/二次元/钓鱼等100+品类，覆盖深圳等10+城市）。支持按类型、城市、日期筛选。",
     "inputSchema": {"type": "object", "properties": {
         "activity_type": {"type": "string", "description": "活动类型"},
         "city": {"type": "string", "description": "城市，如 深圳"},
         "date": {"type": "string", "description": "日期 YYYY-MM-DD"}}}},
    {"name": "get_activity_card",
     "description": "获取指定活动的详情卡片（时间地点、费用、报名情况、主理人信息）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}}, "required": ["activity_id"]}},
    {"name": "create_activity",
     "description": "主理人发布新活动（需全字段确认后提交）。",
     "inputSchema": {"type": "object", "properties": {
         "title": {"type": "string"}, "activity_type": {"type": "string"},
         "date": {"type": "string"}, "time": {"type": "string"},
         "location": {"type": "string"}, "max_participants": {"type": "number"},
         "price": {"type": "number"}, "description": {"type": "string"}},
         "required": ["title", "activity_type", "date", "time", "location"]}},
    {"name": "register_event",
     "description": "为用户报名指定活动。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}, "user_id": {"type": "string"}},
         "required": ["activity_id"]}},
    {"name": "create_payment",
     "description": "为报名订单创建支付（微信支付）。",
     "inputSchema": {"type": "object", "properties": {
         "order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "check_in",
     "description": "活动现场签到核销。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}, "code": {"type": "string"}},
         "required": ["activity_id"]}},
    {"name": "query_venues",
     "description": "查询合作场地（按城市和活动类型匹配容量/人均价）。",
     "inputSchema": {"type": "object", "properties": {
         "city": {"type": "string"}, "activity_type": {"type": "string"}},
         "required": ["city"]}},
    {"name": "generate_urllink",
     "description": "生成活动的小程序分享链接（可直接唤起微信）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}}, "required": ["activity_id"]}},
]


def reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def forward(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if API_KEY:
        headers["Authorization"] = "Bearer " + API_KEY
    req = urllib.request.Request(GATEWAY, data=body, headers=headers, method="POST")
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    # Streamable HTTP 可能回 SSE, 取 data: 行里的 JSON
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return json.loads(raw)


def handle(msg):
    method = msg.get("method")
    rid = msg.get("id")
    if method == "initialize":
        reply(rid, {"protocolVersion": msg.get("params", {}).get(
            "protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "cuqu-mcp-bridge", "version": "1.0.0"}})
    elif method in ("notifications/initialized", "notifications/cancelled"):
        pass  # 通知无需应答
    elif method == "ping":
        reply(rid, {})
    elif method == "tools/list":
        reply(rid, {"tools": TOOLS})
    elif method == "tools/call":
        if not API_KEY:
            reply(rid, {"content": [{"type": "text", "text":
                "未配置 CUQU_API_KEY。请按 https://cuqu.net/llms.txt 指引申领 cq-sk- 开头的 Key 后重试。"}],
                "isError": True})
            return
        try:
            r = forward("tools/call", msg.get("params") or {})
            reply(rid, r.get("result", r))
        except Exception as e:  # noqa: BLE001
            reply(rid, error={"code": -32000, "message": f"gateway error: {e}"})
    else:
        if rid is not None:
            reply(rid, error={"code": -32601, "message": "method not found"})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle(json.loads(line))
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"bad line: {e}\n")


if __name__ == "__main__":
    main()
