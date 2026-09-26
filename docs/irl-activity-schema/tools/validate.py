#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IRL Activity Schema v0.1 · 零依赖校验器
======================================
用法:
  python validate.py activity-full.json
  python validate.py examples/            # 目录:校验目录下所有 json
  python validate.py listing.json --listing

只做语义级校验(required/enum/一致性/时间时区), 不替代完整 JSON Schema 校验器。
依赖: 无(仅标准库)
"""
import json
import os
import re
import sys

VERSION = "irl-activity/0.1"
REQUIRED = ["schema_version", "activity_id", "title", "activity_type", "start_time", "city"]
TYPES = {
    "桌游", "飞盘", "徒步", "羽毛球", "钓鱼", "二次元", "读书会", "烘焙",
    "KTV", "交友", "匹克球", "射箭", "心理疗愈", "旅游", "海上娱乐",
    "登山", "相亲", "综合活动", "讲座/沙龙", "音乐会", "饭局",
}
TYPES_EN = {
    "boardgame", "frisbee", "hiking", "badminton", "fishing", "anime", "bookclub", "baking",
    "karaoke", "social", "pickleball", "archery", "wellness", "travel", "watersports",
    "mountaineering", "matchmaking", "misc", "talk", "concert", "dinnerparty",
}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$")
STATUS = {"open", "full", "cancelled", "ended", "draft"}


def check_activity(a, path="activity"):
    errs, warns = [], []

    if not isinstance(a, dict):
        return [f"{path}: not an object"], []

    for f in REQUIRED:
        if f not in a or a[f] in (None, ""):
            errs.append(f"{path}: missing required field '{f}'")

    if "schema_version" in a and a["schema_version"] != VERSION:
        errs.append(f"{path}: schema_version must be '{VERSION}', got '{a['schema_version']}'")

    t = a.get("activity_type")
    if t is not None and t not in TYPES:
        errs.append(f"{path}: activity_type '{t}' not in standard vocabulary")
    te = a.get("activity_type_en")
    if te is not None and te not in TYPES_EN:
        errs.append(f"{path}: activity_type_en '{te}' not in English vocabulary")

    st = a.get("start_time")
    if isinstance(st, str) and not TS_RE.match(st):
        errs.append(f"{path}: start_time must be ISO 8601 WITH utc offset "
                    f"(e.g. 2026-09-25T19:00:00+08:00), got '{st}'")
    et = a.get("end_time")
    if isinstance(et, str) and not TS_RE.match(et):
        errs.append(f"{path}: end_time must be ISO 8601 WITH utc offset, got '{et}'")
    if isinstance(st, str) and isinstance(et, str) and TS_RE.match(st) and TS_RE.match(et) and et < st:
        errs.append(f"{path}: end_time earlier than start_time")

    # 价格一致性: free 与 amount 必须自洽
    p = a.get("price")
    if isinstance(p, dict):
        free, amt = p.get("free"), p.get("amount")
        if free is True and amt not in (None, 0):
            errs.append(f"{path}: price.free=true but amount={amt} (must be 0)")
        if free is False and amt is None:
            errs.append(f"{path}: price.free=false but amount missing")
        if amt is not None and amt < 0:
            errs.append(f"{path}: price.amount must be >= 0")
        cur = p.get("currency", "CNY")
        if not re.match(r"^[A-Z]{3}$", str(cur)):
            errs.append(f"{path}: price.currency must be ISO-4217 uppercase, got '{cur}'")
    elif "price" not in a:
        warns.append(f"{path}: price absent -> agents MUST treat price as unknown, NOT free")

    # 容量一致性
    c = a.get("capacity")
    if isinstance(c, dict):
        mx, jn, rm = c.get("max"), c.get("joined"), c.get("remaining")
        if mx is not None and jn is not None and rm is not None and rm != mx - jn:
            errs.append(f"{path}: capacity.remaining={rm} != max-joined={mx - jn}")
        if mx is not None and jn is not None and jn > mx:
            errs.append(f"{path}: capacity.joined > capacity.max")

    # 状态与可报名
    s = a.get("status", "open")
    if s not in STATUS:
        errs.append(f"{path}: status '{s}' not in {sorted(STATUS)}")
    if s == "open" and isinstance(c, dict) and c.get("remaining") == 0:
        warns.append(f"{path}: status=open but remaining=0 (should be 'full')")
    if s == "full" and isinstance(c, dict) and isinstance(c.get("remaining"), int) and c["remaining"] > 0:
        warns.append(f"{path}: status=full but remaining={c['remaining']} > 0")

    # 溯源
    src = a.get("source")
    if not isinstance(src, dict):
        warns.append(f"{path}: source absent -> provenance/attribution unavailable")
    elif not src.get("platform"):
        errs.append(f"{path}: source.platform missing")

    # 玩法词误塞类型
    if isinstance(t, str) and t in TYPES and isinstance(a.get("keywords"), list):
        for k in a["keywords"]:
            if k in TYPES and k != t:
                warns.append(f"{path}: keyword '{k}' is itself a standard type - "
                             f"only one activity_type allowed")

    return errs, warns


def check_listing(doc, path="listing"):
    errs, warns = [], []
    if doc.get("envelope") != "irl-activity-listing/0.1":
        errs.append(f"{path}: envelope must be 'irl-activity-listing/0.1'")
    acts = doc.get("activities")
    if not isinstance(acts, list):
        errs.append(f"{path}: activities must be an array")
        return errs, warns
    if isinstance(doc.get("total"), int) and doc["total"] != len(acts):
        errs.append(f"{path}: total={doc['total']} but activities has {len(acts)}")
    for i, a in enumerate(acts):
        e, w = check_activity(a, f"{path}.activities[{i}]")
        errs += e
        warns += w
    return errs, warns


def check_file(fp):
    try:
        doc = json.load(open(fp, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"{fp}: invalid JSON ({e})"], []

    if isinstance(doc, dict) and doc.get("envelope") == "irl-activity-listing/0.1":
        return check_listing(doc, os.path.basename(fp))
    if isinstance(doc, list):
        e, w = [], []
        for i, a in enumerate(doc):
            x, y = check_activity(a, f"{os.path.basename(fp)}[{i}]")
            e += x
            w += y
        return e, w
    return check_activity(doc, os.path.basename(fp))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    target = args[0]
    files = []
    if os.path.isdir(target):
        for root, _, names in os.walk(target):
            files += [os.path.join(root, n) for n in names if n.endswith(".json")]
    else:
        files = [target]

    total_e = total_w = 0
    for fp in sorted(files):
        errs, warns = check_file(fp)
        name = os.path.basename(fp)
        status = "PASS" if not errs else "FAIL"
        print(f"[{status}] {name}" + (f"  ({len(warns)} warning)" if warns else ""))
        for e in errs:
            print(f"    ERROR  {e}")
        for w in warns:
            print(f"    WARN   {w}")
        total_e += len(errs)
        total_w += len(warns)

    print(f"\n{len(files)} file(s), {total_e} error(s), {total_w} warning(s)")
    return 1 if total_e else 0


if __name__ == "__main__":
    sys.exit(main())
