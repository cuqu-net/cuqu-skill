#!/usr/bin/env python3
"""粗趣 MCP 连通性自检：验证环境变量与服务可用性。
用法: python scripts/check-mcp.py
需要环境变量 CUQU_API_KEY（CUQU_MCP_HOST 可选，默认为当前生产地址）。
"""
import json
import os
import sys
import urllib.request

HOST = os.environ.get(
    "CUQU_MCP_HOST",
    "https://dashscope.aliyuncs.com/api/v1/mcps/mcp-NjgwMTQ1ODAyODFj/mcp",
)
KEY = os.environ.get("CUQU_API_KEY", "")


def post(body, sid=None):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer " + KEY,
    }
    if sid:
        headers["Mcp-Session-Id"] = sid
    req = urllib.request.Request(HOST, data=json.dumps(body).encode(), headers=headers)
    return urllib.request.urlopen(req, timeout=30)


def parse(resp):
    text = resp.read().decode("utf-8", "ignore")
    for line in text.split("\n"):
        if line.startswith("data:"):
            try:
                return json.loads(line[5:])
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text[:300]}


def main():
    if not KEY:
        print("缺少 CUQU_API_KEY 环境变量，请到粗趣开放平台扫码获取")
        return 1
    print("1/4 initialize ...")
    r = post({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "cuqu-skill-check", "version": "0.1.0"},
        },
    })
    sid = r.headers.get("Mcp-Session-Id")
    info = parse(r).get("result", {}).get("serverInfo", {})
    print(f"   服务在线: {info.get('name')} v{info.get('version')}  session={sid}")

    print("2/4 initialized ...")
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid=sid)

    print("3/4 tools/list ...")
    tools = parse(post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, sid=sid))
    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    print(f"   工具({len(names)}): {', '.join(names)}")

    print("4/4 query_activities ...")
    result = parse(post({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "query_activities", "arguments": {"activity_type": "桌游聚会", "city": "深圳"}},
    }, sid=sid))
    content = result.get("result", {}).get("content", [])
    preview = content[0].get("text", "")[:200] if content else json.dumps(result, ensure_ascii=False)[:200]
    print(f"   返回: {preview}")
    print("\n全部通过，粗趣 skill 可正常使用")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("401 未授权：CUQU_API_KEY 无效或已刷新作废，请到开放平台重新获取")
        else:
            print(f"HTTP {e.code}: {e.read(300).decode('utf-8', 'ignore')}")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"失败: {e}")
        sys.exit(1)
