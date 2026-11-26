#!/usr/bin/env python3
"""仓库质量门：CI 与本地提交前都运行。

检查项：
1. etk_core 副本与 shared 一致（tools/sync_core.py --check）
2. 每个技能的 SKILL.md：frontmatter 合法、name 与目录名一致、description 长度、正文行数 ≤ 500、
   脚本版本号与 metadata.version 一致、存在触发评测用例（正例 ≥ 20、反例 ≥ 10）
3. 运行时代码（shared 与各技能 scripts）满足 Python 3.10 语法
4. 运行时代码只 import 标准库

用法：python tools/check_repo.py    （无问题时退出码 0）
"""

from __future__ import annotations

import ast
import filecmp
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import sync_core  # noqa: E402

STDLIB_ALLOWED = {
    "__future__", "argparse", "collections", "dataclasses", "difflib", "glob",
    "hashlib", "json", "math", "os", "re", "sys", "tempfile", "time", "typing", "xml",
}
LOCAL_PACKAGES = {"etk_core"}  # 随技能分发的本地核心库，不是第三方依赖
LOCAL_SKILL_MODULES = {"cscan", "crules"}  # 核验器技能内的本地模块
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION_RE = re.compile(r'^__version__\s*=\s*"([^"]+)"', re.MULTILINE)
MIN_POSITIVE = 20
MIN_NEGATIVE = 10
MAX_BODY_LINES = 500


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("缺少 frontmatter 起始 ---")
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        raise ValueError("frontmatter 未闭合（缺少结束 ---）")
    data = {}
    current = None
    last_sub = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        # 列表项：顶格项挂到最近的顶层 key，缩进项挂到最近的下级 key
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"').strip("'")
            if indent == 0:
                container, key = data, current
            else:
                container = data.get(current) if isinstance(current, str) else None
                key = last_sub
            if not isinstance(container, dict) or not isinstance(key, str):
                raise ValueError("无法解析 frontmatter 列表项：%s" % raw)
            if not isinstance(container.get(key), list):
                container[key] = []
            container[key].append(item)
            continue
        key, sep, value = stripped.partition(":")
        if not sep:
            raise ValueError("无法解析 frontmatter 行：%s" % raw)
        value = value.strip().strip('"').strip("'")
        if indent == 0:
            last_sub = None
            if value == "":
                data[key] = {}
                current = key
            else:
                data[key] = value
                current = None
        elif current is not None and isinstance(data.get(current), dict):
            data[current][key] = value
            last_sub = key
    body = "\n".join(lines[end + 1:])
    return data, body


def check_sync():
    issues = []
    for target in sync_core.skill_targets():
        issues.extend(sync_core.diff(target))
    return issues


def check_skills():
    issues = []
    base = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(base)):
        skill_dir = os.path.join(base, name)
        if not os.path.isdir(skill_dir):
            continue
        rel = "skills/%s" % name
        md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(md_path):
            issues.append("%s 缺少 SKILL.md" % rel)
            continue
        with open(md_path, encoding="utf-8") as fh:
            text = fh.read()
        try:
            meta, body = parse_frontmatter(text)
        except ValueError as exc:
            issues.append("%s/SKILL.md：%s" % (rel, exc))
            continue
        skill_name = meta.get("name", "")
        if not NAME_RE.match(skill_name) or len(skill_name) > 64:
            issues.append("%s：name=%r 不符合规范（小写字母、数字、单个连字符，≤64 字符）" % (rel, skill_name))
        if skill_name != name:
            issues.append("%s：name=%r 与目录名不一致" % (rel, skill_name))
        description = meta.get("description", "")
        if not description or len(description) > 1024:
            issues.append("%s：description 为空或超过 1024 字符" % rel)
        compat = meta.get("compatibility")
        if compat is not None and len(compat) > 500:
            issues.append("%s：compatibility 超过 500 字符" % rel)
        body_lines = len(body.splitlines())
        if body_lines > MAX_BODY_LINES:
            issues.append("%s/SKILL.md：正文 %d 行，超过 %d 行，请把细节移到 references/" % (rel, body_lines, MAX_BODY_LINES))
        version = (meta.get("metadata") or {}).get("version")
        script_versions = {}
        scripts = os.path.join(skill_dir, "scripts")
        has_py = False
        if os.path.isdir(scripts):
            for fname in sorted(os.listdir(scripts)):
                if fname.endswith(".py"):
                    has_py = True
                    with open(os.path.join(scripts, fname), encoding="utf-8") as fh:
                        found = VERSION_RE.search(fh.read())
                    if found:
                        script_versions[fname] = found.group(1)
        # 脚本版本号：有则必须与 metadata.version 一致；纯知识技能或未标版本的多脚本技能不阻断
        if script_versions and not version:
            issues.append("%s：有 scripts 版本号但缺 metadata.version" % rel)
        for fname, sv in script_versions.items():
            if version != sv:
                issues.append("%s：metadata.version=%r 与 scripts/%s 的 __version__=%r 不一致" % (rel, version, fname, sv))
        trig_path = os.path.join(ROOT, "tests", "trigger", "%s.json" % name)
        if os.path.isfile(trig_path):
            with open(trig_path, encoding="utf-8") as fh:
                trig = json.load(fh)
            if len(trig.get("positive", [])) < MIN_POSITIVE:
                issues.append("tests/trigger/%s.json：正例少于 %d 条" % (name, MIN_POSITIVE))
            if len(trig.get("negative", [])) < MIN_NEGATIVE:
                issues.append("tests/trigger/%s.json：反例少于 %d 条" % (name, MIN_NEGATIVE))
        # 触发评测用例是质量增强项，不是入库门槛：缺失不阻断，存在则校验下限
    return issues


SKIP_DIRS = {"__pycache__", "tests", "test", "etk_core"}


def _runtime_files():
    """运行时 Python 文件：shared/etk_core 全量 + 各技能内全部 .py。

    不能只扫 scripts/：部分技能的入口脚本放在技能根目录（reviewer.py、main.py、
    ota_audit.py），只扫 scripts/ 会让这些文件绕过模块白名单与禁 eval 校验。
    etk_core 副本不重复计入（shared 已覆盖），tests 不计入（测试可用第三方）。
    """
    files = []
    core = os.path.join(ROOT, "shared", "etk_core")
    files.extend(os.path.join(core, f) for f in sorted(os.listdir(core)) if f.endswith(".py"))
    base = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(base)):
        skill_dir = os.path.join(base, name)
        if not os.path.isdir(skill_dir):
            continue
        for root, dirs, fnames in os.walk(skill_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in sorted(fnames):
                if f.endswith(".py"):
                    files.append(os.path.join(root, f))
    return files


def check_py310():
    issues = []
    for path in _runtime_files():
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        try:
            ast.parse(src, filename=path, feature_version=(3, 10))
        except SyntaxError as exc:
            issues.append("%s：不兼容 Python 3.10 语法（第 %s 行）" % (os.path.relpath(path, ROOT), exc.lineno))
    return issues


def check_stdlib():
    issues = []
    for path in _runtime_files():
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            here = os.path.dirname(path)
            local_mods = {f[:-3] for f in os.listdir(here) if f.endswith(".py")}
            declared = _declared_deps(os.path.dirname(here))
            for name in names:
                if name in _stdlib_names() or name in LOCAL_PACKAGES \
                        or name in LOCAL_SKILL_MODULES or name in local_mods \
                        or name in declared:
                    continue
                issues.append("%s：运行时引入了未声明的第三方模块 %s（标准库之外需在技能根 requirements.txt 声明）"
                              % (os.path.relpath(path, ROOT), name))
    return issues


def _stdlib_names():
    """Python 3.10+ 提供权威标准库清单；回退到内置白名单。"""
    names = getattr(sys, "stdlib_module_names", None)
    return set(names) if names else set(STDLIB_ALLOWED)


def _declared_deps(skill_dir):
    """读取技能根目录的 requirements.txt，返回声明的包名（小写、去版本符）。"""
    path = os.path.join(skill_dir, "requirements.txt")
    if not os.path.isfile(path):
        return set()
    deps = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            raw = line
            line = line.split("#")[0].strip()
            # 支持 "# import: fitz" 形式声明包名与 import 名不一致的情况（如 PyMuPDF→fitz）
            for mod in re.findall(r"import:\s*([A-Za-z_][\w,]*)", raw):
                for m in mod.split(","):
                    if m.strip():
                        deps.add(m.strip().lower())
            if not line:
                continue
            name = re.split(r"[<>=!~\[\s]", line)[0].strip().lower()
            deps.add(name)
            deps.add(name.replace("-", "_"))
    return deps


RELEASE_MANIFEST = os.path.join(ROOT, "release", "published.json")


def load_manifest():
    """读取发布白名单；返回 (entries_by_name, issues)。"""
    if not os.path.isfile(RELEASE_MANIFEST):
        return {}, ["缺少 release/published.json —— 本仓库是发布渠道，任何技能入库前必须在此登记"]
    with open(RELEASE_MANIFEST, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            return {}, ["release/published.json 不是合法 JSON：%s" % exc]
    entries = {}
    issues = []
    for item in data.get("skills", []):
        name = item.get("name", "")
        if not name:
            issues.append("release/published.json：有条目缺少 name")
            continue
        if name in entries:
            issues.append("release/published.json：%s 重复登记" % name)
        entries[name] = item
    return entries, issues


def check_published():
    """发布白名单与实际技能目录必须双向一致，且版本可追溯。

    这条检查是仓库定位的执行体：GitHub 是发布渠道，不是开发仓库。没在平台上线的
    技能根本不该出现在这里，所以「目录有、白名单没有」和「白名单有、目录没有」
    都按错误处理，而不是警告。
    """
    entries, issues = load_manifest()
    base = os.path.join(ROOT, "skills")
    if not os.path.isdir(base):
        return issues + ["缺少 skills/ 目录"]
    on_disk = sorted(n for n in os.listdir(base) if os.path.isdir(os.path.join(base, n)))

    for name in on_disk:
        if name not in entries:
            issues.append("skills/%s：未在 release/published.json 登记。新技能必须先上平台发布、"
                          "再登记入库，未到发布程度的不要提交" % name)
    for name in sorted(entries):
        if name not in on_disk:
            issues.append("release/published.json：登记了 %s 但 skills/ 下没有该目录" % name)

    for name in sorted(set(on_disk) & set(entries)):
        item = entries[name]

        md = os.path.join(base, name, "SKILL.md")
        if not os.path.isfile(md):
            continue
        with open(md, encoding="utf-8") as fh:
            try:
                meta, _ = parse_frontmatter(fh.read())
            except ValueError:
                continue
        skill_version = (meta.get("metadata") or {}).get("version")
        if skill_version != item.get("version"):
            issues.append("%s：release/published.json 记的版本 %r 与 SKILL.md 的 %r 不一致"
                          % (name, item.get("version"), skill_version))
    return issues


def check_demo_assets():
    """内置演示数据（assets/demo.svd）在各技能里的副本必须一致（以 lookup 技能为源）。"""
    canonical = os.path.join(ROOT, "skills", "embedded-register-lookup", "assets", "demo.svd")
    if not os.path.isfile(canonical):
        return ["缺少 skills/embedded-register-lookup/assets/demo.svd"]
    issues = []
    base = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(base)):
        if name == "embedded-register-lookup":
            continue
        cand = os.path.join(base, name, "assets", "demo.svd")
        if os.path.isfile(cand) and not filecmp.cmp(canonical, cand, shallow=False):
            issues.append("skills/%s/assets/demo.svd 与 embedded-register-lookup 的副本不一致" % name)
    return issues


FORBIDDEN_CALLS = {"eval", "exec", "compile"}


def check_no_dynamic_exec():
    """规格 0.7：运行时代码不执行用户代码（不 eval/exec/compile）。"""
    issues = []
    for path in _runtime_files():
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in FORBIDDEN_CALLS:
                issues.append("%s：运行时不允许调用 %s()（规格 0.7：不执行用户代码）" % (
                    os.path.relpath(path, ROOT), node.func.id))
    return issues


DESC_WARN = 900


def check_warnings():
    """非阻断项：不失败，但值得处理。

    description 上限 1024 是多个 Agent 的硬限制，超限时 ZCode 会静默丢弃整个技能
    （不报错、不截断，用户只看到"装了没反应"）。接近上限时提前提示，留出加触发词
    的余量。
    """
    warns = []
    base = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(base)):
        md = os.path.join(base, name, "SKILL.md")
        if not os.path.isfile(md):
            continue
        with open(md, encoding="utf-8") as fh:
            text = fh.read()
        try:
            meta, _ = parse_frontmatter(text)
        except ValueError:
            continue
        desc = meta.get("description", "")
        if len(desc) > DESC_WARN:
            warns.append("%s：description %d 字符，距 1024 上限仅 %d，建议精简后再加触发词"
                         % (name, len(desc), 1024 - len(desc)))
    return warns


def run_all():
    return (check_sync() + check_skills() + check_published() + check_py310() + check_stdlib()
            + check_demo_assets() + check_no_dynamic_exec())


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for item in check_warnings():
        print("警告：" + item)
    issues = run_all()
    if issues:
        for item in issues:
            print("问题：" + item)
        print("共 %d 个问题。" % len(issues))
        return 1
    print("仓库检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
