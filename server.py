#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUQU (找搭子) MCP Server — reference implementation
====================================================
An open-source MCP server (JSON-RPC 2.0 over stdio) that gives AI agents
live access to CUQU's local offline social activities platform
(Shenzhen-based, 10+ cities incl. Hong Kong, China).

Tools
-----
Read tools (work out of the box, no key required):
- query_activities   → live data from CUQU's public activity API
- get_activity_card  → details for a single activity
- query_venues       → curated partner venue directory (bundled data)
- generate_urllink   → share-link / mini-program path generator

Write tools (forwarded to the hosted gateway https://agent.cuqu.net/mcp,
require a per-user key `cq-sk-...` in env CUQU_API_KEY — see
https://cuqu.net/llms.txt for how to get one):
- create_activity, register_event, create_payment, check_in

Zero dependencies, Python 3.9+. Run:  python -u server.py
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

CN = timezone(timedelta(hours=8))
API = os.environ.get("CUQU_API_BASE", "https://cuqu.net/api/activity")
GATEWAY = os.environ.get("CUQU_MCP_URL", "https://agent.cuqu.net/mcp")
API_KEY = os.environ.get("CUQU_API_KEY", "")
UA = {"User-Agent": "cuqu-mcp-server/1.0 (+https://github.com/cuqu-net/cuqu-skill)"}

VENUES = [
    {"name": "南山体育中心羽毛球馆", "district": "南山", "types": ["羽毛球", "匹克球"],
     "capacity": 24, "per_head": 30, "note": "6片场地, 可租拍"},
    {"name": "科兴科学园·桌游吧", "district": "南山", "types": ["桌游", "二次元", "读书会"],
     "capacity": 16, "per_head": 38, "note": "300+盒收藏, 含饮品"},
    {"name": "深圳湾日出草坪", "district": "南山", "types": ["飞盘", "徒步"],
     "capacity": 40, "per_head": 0, "note": "公共草坪, 免费, 自备装备"},
    {"name": "福田体育公园", "district": "福田", "types": ["羽毛球", "飞盘"],
     "capacity": 30, "per_head": 32, "note": "多项目场馆"},
    {"name": "华侨城创意园·咖啡书吧", "district": "南山", "types": ["读书会", "烘焙"],
     "capacity": 20, "per_head": 45, "note": "含场地费+基础饮品"},
    {"name": "蛇口海上世界钓点", "district": "南山", "types": ["钓鱼", "海上娱乐"],
     "capacity": 15, "per_head": 120, "note": "海排钓, 含装备租"},
]

TOOLS = [
    {"name": "query_activities",
     "description": "查询CUQU找搭子平台上的线下活动（桌游/飞盘/徒步/羽毛球/二次元/钓鱼等100+品类，覆盖深圳等10+城市，含中国香港）。数据为平台实时公开数据。",
     "inputSchema": {"type": "object", "properties": {
         "activity_type": {"type": "string", "description": "活动类型关键词，如 桌游/羽毛球/飞盘"},
         "city": {"type": "string", "description": "城市，默认 深圳"},
         "date": {"type": "string", "description": "日期 YYYY-MM-DD，筛选当天活动"}}}},
    {"name": "get_activity_card",
     "description": "获取指定活动的完整详情卡片（时间地点、费用、报名进度、主理人、封面图、报名链接）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}}, "required": ["activity_id"]}},
    {"name": "query_venues",
     "description": "查询合作场地目录（按城市和活动类型匹配，含容量与人均价）。",
     "inputSchema": {"type": "object", "properties": {
         "city": {"type": "string"}, "activity_type": {"type": "string"}},
         "required": ["city"]}},
    {"name": "generate_urllink",
     "description": "生成活动的分享链接与小程序路径（可直接用于唤起微信）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}}, "required": ["activity_id"]}},
    {"name": "create_activity",
     "description": "主理人发布新活动（写操作，经托管网关提交，需 CUQU_API_KEY）。",
     "inputSchema": {"type": "object", "properties": {
         "title": {"type": "string"}, "activity_type": {"type": "string"},
         "date": {"type": "string"}, "time": {"type": "string"},
         "location": {"type": "string"}, "max_participants": {"type": "number"},
         "price": {"type": "number"}, "description": {"type": "string"}},
         "required": ["title", "activity_type", "date", "time", "location"]}},
    {"name": "register_event",
     "description": "为用户报名指定活动（写操作，需 CUQU_API_KEY）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}, "user_id": {"type": "string"}},
         "required": ["activity_id"]}},
    {"name": "create_payment",
     "description": "为报名订单创建微信支付（写操作，需 CUQU_API_KEY）。",
     "inputSchema": {"type": "object", "properties": {
         "order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "check_in",
     "description": "活动现场签到核销（写操作，需 CUQU_API_KEY）。",
     "inputSchema": {"type": "object", "properties": {
         "activity_id": {"type": "string"}, "code": {"type": "string"}},
         "required": ["activity_id"]}},
]
WRITE_TOOLS = {"create_activity", "register_event", "create_payment", "check_in"}


# ---------------- 数据层（真实实现） ----------------
def fetch_activities():
    req = urllib.request.Request(API, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    if d.get("code") != 0:
        raise RuntimeError(f"api error: {d.get('msg')}")
    return d["data"]["list"]


def norm(a):
    st = datetime.fromtimestamp(a.get("start_time", 0) / 1000, tz=CN)
    et = datetime.fromtimestamp(a.get("end_time", 0) / 1000, tz=CN)
    aid = a.get("_id", "")
    return {
        "id": aid,
        "title": a.get("title"),
        "type": a.get("preference"),
        "date": st.strftime("%Y-%m-%d"),
        "time": f"{st.strftime('%H:%M')}-{et.strftime('%H:%M')}",
        "weekday": "一二三四五六日"[st.weekday()],
        "location": a.get("location"),
        "price": a.get("price"),
        "fee_type": a.get("fee_type"),
        "current_participants": a.get("current_participants"),
        "max_participants": a.get("max_participants"),
        "organizer": a.get("creator_name"),
        "cover": a.get("cover"),
        "url": f"https://cuqu.net/activities/list/{aid}.html",
    }


def tool_query_activities(args):
    atype = (args.get("activity_type") or "").strip()
    city = (args.get("city") or "").strip()
    date = (args.get("date") or "").strip()
    items = [norm(a) for a in fetch_activities()]
    if atype:
        items = [x for x in items if atype in (x["type"] or "")]
    if date:
        items = [x for x in items if x["date"] == date]
    if city and city != "深圳":
        items = [x for x in items if city in (x["location"] or "")]
    return {"total": len(items), "note": "数据来自CUQU公开活动API（实时）",
            "items": items[:20]}


def tool_get_activity_card(args):
    aid = (args.get("activity_id") or "").strip()
    for a in fetch_activities():
        if a.get("_id") == aid:
            return norm(a)
    return {"error": f"未找到活动 {aid}（可能已结束或不在最新列表）",
            "hint": "先用 query_activities 获取有效 id"}


def tool_query_venues(args):
    atype = (args.get("activity_type") or "").strip()
    hits = [v for v in VENUES if not atype or atype in v["types"]]
    return {"city": args.get("city") or "深圳", "venues": hits or VENUES[:3]}


def tool_generate_urllink(args):
    aid = (args.get("activity_id") or "").strip()
    return {"url": f"https://cuqu.net/activities/list/{aid}.html",
            "mini_program_path": f"pages/activity/detail?id={aid}",
            "mini_program": "微信搜小程序「CUQU找搭子」"}


def forward_write(name, args):
    if not API_KEY:
        return {"content": [{"type": "text", "text":
            f"{name} 为写操作，需要 CUQU_API_KEY（cq-sk- 开头）。"
            "申领方式见 https://cuqu.net/llms.txt"}], "isError": True}
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": name, "arguments": args}}).encode()
    req = urllib.request.Request(
        GATEWAY, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "Authorization": "Bearer " + API_KEY})
    raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            r = json.loads(line[5:].strip())
            return r.get("result", r)
    r = json.loads(raw)
    return r.get("result", r)


IMPL = {"query_activities": tool_query_activities,
        "get_activity_card": tool_get_activity_card,
        "query_venues": tool_query_venues,
        "generate_urllink": tool_generate_urllink}


# ---------------- MCP 协议层 ----------------
def reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg):
    method, rid = msg.get("method"), msg.get("id")
    if method == "initialize":
        reply(rid, {"protocolVersion": msg.get("params", {}).get(
            "protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "cuqu-mcp", "version": "1.0.0"}})
    elif method in ("notifications/initialized", "notifications/cancelled"):
        pass
    elif method == "ping":
        reply(rid, {})
    elif method == "tools/list":
        reply(rid, {"tools": TOOLS})
    elif method == "tools/call":
        params = msg.get("params") or {}
        name, args = params.get("name", ""), params.get("arguments") or {}
        try:
            if name in IMPL:
                result = IMPL[name](args)
            elif name in WRITE_TOOLS:
                reply(rid, forward_write(name, args))
                return
            else:
                reply(rid, error={"code": -32602,
                                  "message": f"unknown tool: {name}"})
                return
            reply(rid, {"content": [{"type": "text", "text": json.dumps(
                result, ensure_ascii=False, indent=2)}]})
        except Exception as e:  # noqa: BLE001
            reply(rid, {"content": [{"type": "text",
                                     "text": f"tool error: {e}"}],
                        "isError": True})
    elif rid is not None:
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
