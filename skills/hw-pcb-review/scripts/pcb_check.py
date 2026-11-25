#!/usr/bin/env python3
"""PCB 布局自查打勾工具：逐项过清单，输出整改清单与通过率。

用法：
  python pcb_check.py run --board "我的板v2"   # 交互逐项检查（y/n/na），进度实时显示
  python pcb_check.py report --board "我的板v2" # 查看上次检查结果
  python pcb_check.py reset --board "我的板v2"  # 清空检查进度
  python pcb_check.py list                      # 列出全部条目

结果存 ~/.pcb_check/<board>.json（跨会话续查）。
"""
import argparse
import json
import os
import re
import sys
import io

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKLIST = os.path.join(os.path.dirname(HERE), "references", "pcb-checklist.md")
STORE = os.path.join(os.path.expanduser("~"), ".pcb_check")

SEV_ORDER = {"必改": 0, "待确认": 1, "提示": 2}


def load_items():
    """从 pcb-checklist.md 解析条目：编号/类别/级别/内容/事故。"""
    with io.open(CHECKLIST, encoding="utf-8") as f:
        t = f.read()
    items = []
    # [A-Z]：类别字母不作硬编码——清单将来加 J/K 类不会静默丢项
    for m in re.finditer(r"^\| ([A-Z]\d+) \| ([^|]+)\|([^|]+)\|([^|]+)\|", t, re.M):
        item_id, sev, content, story = (g.strip() for g in m.groups())
        # 清单里级别写作 **必改**——剥掉 Markdown 星号，否则排序键永远查不中
        sev = sev.replace("*", "").strip()
        cat = item_id[0]
        items.append({"id": item_id, "cat": cat, "sev": sev,
                      "content": content, "story": story})
    return items


def load_state(board):
    os.makedirs(STORE, exist_ok=True)
    p = os.path.join(STORE, board + ".json")
    if os.path.isfile(p):
        with io.open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(board, state):
    os.makedirs(STORE, exist_ok=True)
    with io.open(os.path.join(STORE, board + ".json"), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def cmd_run(board):
    items = load_items()
    state = load_state(board)
    done = [i for i in items if state.get(i["id"], {}).get("result") in ("pass", "fail", "na")]
    print(f"板子: {board} | 已查 {len(done)}/{len(items)}，继续未完成项\n")
    for idx, it in enumerate(items):
        rec = state.get(it["id"], {})
        if rec.get("result") in ("pass", "fail", "na"):
            continue
        print(f"[{idx+1}/{len(items)}] {it['id']}（{it['sev']}）{it['content']}")
        if it["story"]:
            print(f"       典型事故: {it['story']}")
        while True:
            a = input("  过了?(y) 没过(n) 不适用(na) 跳过(s) 退出(q): ").strip().lower()
            if a in ("y", "n", "na", "s", "q"):
                break
        if a == "q":
            break
        if a == "s":
            continue
        rec = {"result": {"y": "pass", "n": "fail", "na": "na"}[a]}
        if a == "n":
            rec["note"] = input("  问题备注（回车跳过）: ").strip()
        state[it["id"]] = rec
        save_state(board, state)
    _summary(board, items, state)


def cmd_report(board, export=None):
    if not board:
        list_boards()
        return
    items = load_items()
    state = load_state(board)
    if export == "":
        export = board + "_report.md"   # --export 不带文件名时的默认命名
    _summary(board, items, state, verbose=True, export=export)


def list_boards():
    """不带 --board 的 report：列出已有检查存档。"""
    if not os.path.isdir(STORE):
        print("尚无检查存档（先跑: python pcb_check.py run --board \"板名\"）")
        return
    boards = sorted(f[:-5] for f in os.listdir(STORE) if f.endswith(".json"))
    if not boards:
        print("尚无检查存档（先跑: python pcb_check.py run --board \"板名\"）")
        return
    print("已有检查存档：")
    for b in boards:
        print(f"  {b}   （查看: python pcb_check.py report --board \"{b}\"）")


def _summary(board, items, state, verbose=False, export=None):
    total = len(items)
    passed = failed = na = unchecked = 0
    fails = []
    cats = {}
    for it in items:
        r = state.get(it["id"], {}).get("result")
        c = cats.setdefault(it["cat"], {"pass": 0, "fail": 0, "na": 0, "unchecked": 0, "total": 0})
        c["total"] += 1
        if r == "pass":
            passed += 1
            c["pass"] += 1
        elif r == "fail":
            failed += 1
            fails.append(it)
            c["fail"] += 1
        elif r == "na":
            na += 1
            c["na"] += 1
        else:
            unchecked += 1
            c["unchecked"] += 1
    print(f"\n===== {board} 布局自查报告 =====")
    print(f"通过 {passed} | 不合格 {failed} | 不适用 {na} | 未查 {unchecked} / 共 {total}")
    rate = passed * 100 // max(1, total - na)
    print(f"有效通过率: {rate}%")
    print("按类小计：")
    for c in sorted(cats):
        v = cats[c]
        print(f"  {c} 类: 过 {v['pass']} / 不合格 {v['fail']} / 不适用 {v['na']} / 未查 {v['unchecked']}（共 {v['total']}）")
    if fails:
        print(f"\n整改清单（{len(fails)} 项）：")
        for it in sorted(fails, key=lambda x: (SEV_ORDER.get(x["sev"], 9), x["id"])):
            note = state.get(it["id"], {}).get("note", "")
            print(f"  [{it['sev']}] {it['id']} {it['content']}" + (f" —— 备注: {note}" if note else ""))
    if unchecked:
        print(f"\n未查 {unchecked} 项——继续: python pcb_check.py run --board \"{board}\"")
    if failed == 0 and unchecked == 0:
        print("\n✅ 全部通过，可发板")
    if export:
        _export_md(board, items, state, cats, fails, passed, failed, na, unchecked,
                   total, rate, export)
        print(f"\n报告已导出: {export}")


def _export_md(board, items, state, cats, fails, passed, failed, na, unchecked,
               total, rate, path):
    lines = [f"# {board} PCB 布局自查报告", "",
             f"通过 {passed} | 不合格 {failed} | 不适用 {na} | 未查 {unchecked} / 共 {total}（有效通过率 {rate}%）",
             "", "## 按类小计", "",
             "| 类 | 过 | 不合格 | 不适用 | 未查 | 共 |",
             "|---|---|---|---|---|---|"]
    for c in sorted(cats):
        v = cats[c]
        lines.append(f"| {c} | {v['pass']} | {v['fail']} | {v['na']} | {v['unchecked']} | {v['total']} |")
    lines += ["", "## 整改清单（按严重级别排序）", ""]
    if fails:
        for it in sorted(fails, key=lambda x: (SEV_ORDER.get(x["sev"], 9), x["id"])):
            note = state.get(it["id"], {}).get("note", "")
            lines.append(f"- **[{it['sev']}]** {it['id']} {it['content']}"
                         + (f" —— {note}" if note else ""))
    else:
        lines.append("（无不合格项）")
    if unchecked:
        lines += ["", f"> 另有 {unchecked} 项未查——继续: python pcb_check.py run --board \"{board}\""]
        lines += ["", "## 未查项清单", ""]
        for it in items:
            if state.get(it["id"], {}).get("result") not in ("pass", "fail", "na"):
                lines.append(f"- {it['id']}（{it['sev']}）{it['content']}")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def cmd_reset(board):
    p = os.path.join(STORE, board + ".json")
    if os.path.isfile(p):
        os.remove(p)
        print(f"{board} 检查进度已清空")
    else:
        print("无进度记录")


def cmd_list():
    items = load_items()
    cur = None
    for it in items:
        if it["cat"] != cur:
            cur = it["cat"]
            print(f"\n-- 类 {cur} --")
        print(f"  {it['id']}（{it['sev']}）{it['content']}")


def main():
    ap = argparse.ArgumentParser(description="PCB 布局自查打勾工具")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r1 = sub.add_parser("run", help="交互逐项检查")
    r1.add_argument("--board", required=True)
    r2 = sub.add_parser("report", help="查看检查结果（--board 省略时列出已有存档）")
    r2.add_argument("--board", default=None)
    r2.add_argument("--export", nargs="?", const="", default=None, metavar="FILE",
                    help="整改清单导出 Markdown（不带文件名时默认 <板名>_report.md）")
    r3 = sub.add_parser("reset", help="清空进度")
    r3.add_argument("--board", required=True)
    sub.add_parser("list", help="列出全部条目")
    a = ap.parse_args()
    if a.cmd == "run":
        cmd_run(a.board)
    elif a.cmd == "report":
        cmd_report(a.board, getattr(a, "export", None))
    elif a.cmd == "reset":
        cmd_reset(a.board)
    elif a.cmd == "list":
        cmd_list()


if __name__ == "__main__":
    main()
