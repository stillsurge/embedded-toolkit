#!/usr/bin/env python3
"""发布前体检：过不了这条不能打 tag。

质量门（check_repo）管的是「内容对不对」，本脚本管的是「现在该不该发版」：
1. 质量门 + 单元测试全绿
2. 发布白名单里没有未对齐平台的技能（有就必须 --ack-pending 显式确认）
3. 相对上一个 tag，技能内容变了就必须升版本号（改了内容不改版本，用户拿到的
   zip 名和版本号会对不上，回滚也没法定位）
4. 索引与工作树干净：没有 __pycache__、.pytest_cache、*.pyc 被提交
5. 无本机绝对路径 / 用户名 / 令牌泄露（公开仓库，泄露一次就是永久）
6. 打包预演：报告文件数与体积，确认没有把测试夹具或评测转录打进去
7. 文档同步：每个技能在 docs/skills/ 有一页

用法：
    python tools/check_release.py                 # 完整体检
    python tools/check_release.py --since v1.4.1   # 指定比对基线
    python tools/check_release.py --ack-pending    # 明知还有待对齐项，仍要发版
    python tools/check_release.py --skip-tests     # 只查结构（本地快速迭代用）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import check_repo  # noqa: E402

SKIP_EXT = {".pyc", ".pyo"}
MAX_BUNDLE_MB = 5.0
FORBIDDEN_IN_INDEX = (".pytest_cache/", "__pycache__/", "/.benchmarks/")

# 本机路径与凭据的特征串。命中即失败：公开仓库里出现一次就会被缓存、被 fork。
LEAK_PATTERNS = [
    (re.compile(r"[A-Za-z]:\\\\?Users\\\\?[A-Za-z0-9_.-]+"), "Windows 用户目录绝对路径"),
    (re.compile(r"[A-Za-z]:\\\\?work\\\\"), "本机开发目录绝对路径"),
    (re.compile(r"/home/[a-z0-9_-]+/"), "Linux 用户目录绝对路径"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "GitHub 令牌"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "API Key"),
]


def sh(args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def tracked_files():
    out = sh(["git", "ls-files"])
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line.strip()]


def last_tag():
    out = sh(["git", "describe", "--tags", "--abbrev=0"])
    return out.stdout.strip() if out.returncode == 0 else ""


def version_of(skill_dir):
    md = os.path.join(ROOT, skill_dir, "SKILL.md")
    if not os.path.isfile(md):
        return None
    with open(md, encoding="utf-8") as fh:
        meta, _ = check_repo.parse_frontmatter(fh.read())
    return (meta.get("metadata") or {}).get("version")


def changed_skills(since):
    """返回相对 since 有内容变更的技能目录名。

    要同时看工作树与未跟踪文件：发布前最后一批改动往往还没 commit，只看
    `since..HEAD` 会漏掉它们，等于放行「改了内容没升版本」。
    """
    if not since:
        return []
    names = set()

    def add(path):
        path = path.strip().replace("\\", "/")
        if " -> " in path:            # 重命名：取新路径
            path = path.split(" -> ")[-1]
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "skills":
            names.add(parts[1])

    diff = sh(["git", "diff", "--name-only", since, "--", "skills/"])
    if diff.returncode == 0:
        for line in diff.stdout.splitlines():
            add(line)

    status = sh(["git", "status", "--porcelain", "--", "skills/"])
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            add(line[3:] if len(line) > 3 else "")
    return sorted(n for n in names if n)


def check_tests():
    issues = []
    out = sh([sys.executable, "-m", "pytest", "-q"])
    tail = (out.stdout or "").strip().splitlines()
    if out.returncode != 0:
        detail = tail[-3:] if tail else [""]
        issues.append("pytest 未通过：%s" % " | ".join(detail))
    return issues


def check_pending(ack):
    issues = []
    pending = check_repo.pending_sync()
    if pending and not ack:
        issues.append("还有 %d 个技能未与平台对齐，确认要发版请加 --ack-pending：%s"
                      % (len(pending), ", ".join(n for n, _, _ in pending)))
    return issues


def check_version_bump(since):
    issues = []
    if not since:
        issues.append("找不到上一个 tag，无法判断版本是否递增（首次发版请显式传 --since）")
        return issues
    for name in changed_skills(since):
        # git 只认正斜杠：Windows 下 os.path.join 产生的反斜杠会让
        # `git show tag:path` 返回 128，检查静默失效（曾因此漏掉整轮未升版本）。
        skill_dir = "skills/" + name
        if not os.path.isdir(os.path.join(ROOT, skill_dir)):
            continue  # 已移除的技能不用管版本
        old = sh(["git", "show", "%s:%s/SKILL.md" % (since, skill_dir)])
        old_ver = None
        if old.returncode == 0:
            try:
                meta, _ = check_repo.parse_frontmatter(old.stdout)
                old_ver = (meta.get("metadata") or {}).get("version")
            except ValueError:
                old_ver = None
        new_ver = version_of(skill_dir)
        if old_ver and new_ver and old_ver == new_ver:
            issues.append("%s：内容有改动但版本仍是 %s，升版本后再发版" % (name, new_ver))
    return issues


def check_index_hygiene():
    issues = []
    for path in tracked_files():
        if any(bad in "/" + path for bad in FORBIDDEN_IN_INDEX):
            issues.append("索引里混入了缓存文件：%s" % path)
        if os.path.splitext(path)[1] in SKIP_EXT:
            issues.append("索引里混入了字节码：%s" % path)
    return issues


def check_leaks():
    issues = []
    for path in tracked_files():
        if os.path.splitext(path)[1].lower() in {".zip", ".png", ".jpg", ".gif", ".svd", ".pdf"}:
            continue
        full = os.path.join(ROOT, path)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern, label in LEAK_PATTERNS:
                if pattern.search(line):
                    issues.append("%s:%d 疑似%s泄露" % (path, line_no, label))
    return issues


def check_docs():
    issues = []
    base = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(base)):
        if not os.path.isdir(os.path.join(base, name)):
            continue
        page = os.path.join(ROOT, "docs", "skills", "%s.md" % name)
        if not os.path.isfile(page):
            issues.append("docs/skills/%s.md 缺失（每个技能要有一页，写清作用/命令/实测记录/边界）" % name)
    issues += check_readme_versions()
    return issues


def check_readme_versions():
    """README 技能表的版本列必须与 SKILL.md 的 metadata.version 一致。

    这张表是用户判断"我装的是不是最新"的唯一依据，手工维护必然漂移——
    升了技能忘了改表，用户就会以为仓库是旧版。
    """
    issues = []
    readme = os.path.join(ROOT, "README.md")
    if not os.path.isfile(readme):
        return ["README.md 不存在"]
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()
    rows = re.findall(r"`([a-z0-9][a-z0-9-]*)`[^\n|]*\|[^\n|]*\|\s*(\d+\.\d+\.\d+)\s*\|", text)
    for name, ver in rows:
        md = os.path.join(ROOT, "skills", name, "SKILL.md")
        if not os.path.isfile(md):
            continue
        with open(md, encoding="utf-8") as fh:
            try:
                meta, _ = check_repo.parse_frontmatter(fh.read())
            except ValueError:
                continue
        real = (meta.get("metadata") or {}).get("version")
        if real and real != ver:
            issues.append("README.md 技能表里 %s 写的是 %s，SKILL.md 是 %s" % (name, ver, real))
    return issues


def bundle_preview():
    """打包预演：只看 skills/，报告文件数与体积，避免把不该发的东西打进去。"""
    total = 0
    size = 0
    biggest = []
    base = os.path.join(ROOT, "skills")
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache"}]
        for f in files:
            if os.path.splitext(f)[1] in SKIP_EXT:
                continue
            p = os.path.join(root, f)
            total += 1
            sz = os.path.getsize(p)
            size += sz
            biggest.append((sz, os.path.relpath(p, ROOT)))
    biggest.sort(reverse=True)
    return total, size / 1024 / 1024, biggest[:5]


def check_metadata():
    """聚合版本与 CHANGELOG、tag 的一致性由 release.yml 兜底，这里先看本地是否自洽。"""
    issues = []
    plugin = os.path.join(ROOT, ".claude-plugin", "plugin.json")
    version = ""
    if os.path.isfile(plugin):
        with open(plugin, encoding="utf-8") as fh:
            version = json.load(fh).get("version", "")
    if not version:
        return ["读不到 .claude-plugin/plugin.json 的 version"]
    changelog = os.path.join(ROOT, "CHANGELOG.md")
    if os.path.isfile(changelog):
        with open(changelog, encoding="utf-8") as fh:
            if "## [%s]" % version not in fh.read():
                issues.append("CHANGELOG.md 里没有 [%s] 段，发版前补一条" % version)
    return issues


def main():
    parser = argparse.ArgumentParser(description="发布前体检")
    parser.add_argument("--since", default="", help="比对基线的 tag，默认取最近一个 tag")
    parser.add_argument("--ack-pending", action="store_true", help="确认仍有未对齐平台的技能")
    parser.add_argument("--skip-tests", action="store_true", help="跳过 pytest")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    since = args.since or last_tag()

    issues = []
    issues += check_repo.run_all()
    if not args.skip_tests:
        issues += check_tests()
    issues += check_pending(args.ack_pending)
    issues += check_version_bump(since)
    issues += check_index_hygiene()
    issues += check_leaks()
    issues += check_docs()
    issues += check_metadata()

    count, mb, biggest = bundle_preview()
    print("== 打包预演 ==")
    print("基线 tag：%s" % (since or "（无）"))
    print("skills/ 共 %d 个文件，%.2f MB" % (count, mb))
    for sz, rel in biggest:
        print("  %6.1f KB  %s" % (sz / 1024, rel))

    pending = check_repo.pending_sync()
    if pending:
        print("\n== 待对齐平台的技能（%d） ==" % len(pending))
        for name, state, plan in pending:
            print("  %-30s [%s] %s" % (name, state, plan))

    if mb > MAX_BUNDLE_MB:
        issues.append("skills/ 体积 %.2f MB 超过 %.1f MB，检查是否混入大文件" % (mb, MAX_BUNDLE_MB))

    print()
    if issues:
        for item in issues:
            print("问题：" + item)
        print("发布体检未通过：%d 个问题。" % len(issues))
        return 1

    version = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))["version"]
    tagged = sh(["git", "rev-parse", "-q", "--verify", "refs/tags/v%s" % version]).returncode == 0
    print("发布体检通过。")
    if tagged:
        print("注意：v%s 这个 tag 已经存在，本次改动没有对应的新版本。技能内容有变更时请把 "
              "plugin.json 升一个 minor 并补 CHANGELOG 段，再打新 tag。" % version)
    else:
        print("可以打 tag：git tag -a v%s -m \"v%s\" && git push origin v%s" % (version, version, version))
    if "## [Unreleased]" in open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read():
        print("提示：CHANGELOG 里还有 [Unreleased] 段，说明有内容尚未归入任何版本。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
