#!/usr/bin/env python3
"""schematic-reader 一键回归 harness：改完任何脚本先跑这个，全绿再说话。

覆盖：
  A. netlist_json.py 本地链路（.netlist.json：overview/comp/nc/xnet/erc）
  B. un_mcp.py MCP 链路（Altium/KiCad/Cadence 三格式 overview 计数 + erc）
  C. pdf_probe.py（L2 矢量 PDF / L3 扫描版判定 + 坏文件 exit 2）
  D. lceda_parse.py（eprj3 官方样例）
  E. 坏文件矩阵（un_mcp 预检 + netlist_json 坏 JSON，全部应 exit 2）
  F. P0 静默吞错防线（缺 .net 的 KiCad 必须 exit 2 且输出含 "No netlist"）

用法：
  python run_regression.py            # 全量
  python run_regression.py --quick    # 只跑 A/E/F（不依赖 MCP，秒级）

输出：绿/红表 + 汇总，任一红 exit 1。
"""
import argparse
import os
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
TESTDATA = os.path.normpath(os.path.join(HERE, "..", "..", "testdata"))
PY = sys.executable

RESULTS = []


def run(name, cmd, expect_exit=0, must_contain=None, must_not_contain=None,
        env=None):
    """跑一条命令并断言 exit code 与输出内容。"""
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=600, env=full_env)
        out = (r.stdout or "") + (r.stderr or "")
        ok = (r.returncode == expect_exit)
        if ok and must_contain:
            for s in must_contain:
                if s not in out:
                    ok = False
                    out += f"\n[断言失败] 输出缺少: {s!r}"
                    break
        if ok and must_not_contain:
            for s in must_not_contain:
                if s in out:
                    ok = False
                    out += f"\n[断言失败] 输出不应含: {s!r}"
                    break
        RESULTS.append((name, ok, out.strip()[:300]))
    except subprocess.TimeoutExpired:
        RESULTS.append((name, False, "TIMEOUT 600s"))
    return RESULTS[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="只跑免 MCP 的快测")
    args = ap.parse_args()

    nets_json = os.path.join(TESTDATA, "pca10056.netlist.json")
    pdf_l2 = os.path.join(TESTDATA, "PCA10056_schematic.pdf")
    pdf_l3 = os.path.join(TESTDATA, "scanned_like.pdf")
    eprj3 = os.path.join(TESTDATA, "eprj3-format", "example", "eprj3-example",
                         "eprj3-example.eprj3")
    altium = os.path.join(TESTDATA, "pca10056", "pca10056.PrjPCB")
    kicad = os.path.join(TESTDATA, "kicad_cm5", "CM5_MINIMA_3.kicad_pro")
    cadence = os.path.join(TESTDATA, "cadence_multio", "MULTIO.DSN")

    if not os.path.isdir(TESTDATA):
        print(f"ERROR: 找不到 testdata: {TESTDATA}")
        sys.exit(1)

    # ---- A. netlist_json 本地链路 ----
    nj = os.path.join(HERE, "netlist_json.py")
    run("A1 netlist_json overview(PCA10056)", [PY, nj, "overview", nets_json],
        must_contain=["器件总数: 344", "236"])
    run("A2 netlist_json comp U1", [PY, nj, "comp", nets_json, "U1"],
        must_contain=["U1"])
    run("A3 netlist_json nc", [PY, nj, "nc", nets_json],
        must_contain=["75"])
    run("A4 netlist_json xnet", [PY, nj, "xnet", nets_json, "--pin", "U1.A8"],
        expect_exit=0)

    # ---- E. 坏文件矩阵（免 MCP，先跑）----
    bad = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
    bad.write('{"foo": 1}')
    bad.close()
    run("E1 netlist_json 坏JSON exit2", [PY, nj, "nets", bad.name],
        expect_exit=2)
    run("E2 netlist_json 缺文件 exit2", [PY, nj, "nets", "/tmp/definitely_missing.json"],
        expect_exit=2)
    run("E3 un_mcp 缺design exit2", [PY, os.path.join(HERE, "un_mcp.py"),
                                     "nets", "/tmp/definitely_missing.PrjPCB"],
        expect_exit=2)
    run("E4 un_mcp 单SchDoc exit2", [PY, os.path.join(HERE, "un_mcp.py"), "nets",
                                     os.path.join(TESTDATA, "pca10056",
                                                  "pca10056_sheet2_nrf52840_mcu.SchDoc")],
        expect_exit=2, must_contain=[".PrjPcb"])
    run("E5 pdf_probe 缺文件 exit2", [PY, os.path.join(HERE, "pdf_probe.py"),
                                      "/tmp/definitely_missing.pdf"],
        expect_exit=2)
    fake_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="w")
    fake_pdf.write("this is not a pdf")
    fake_pdf.close()
    # pymupdf 可能在隔离 venv（开发机）——pdf_probe 自身有自愈链，直接用当前解释器
    run("E6 pdf_probe 假PDF exit2", [PY, os.path.join(HERE, "pdf_probe.py"),
                                     fake_pdf.name],
        expect_exit=2)

    # ---- F. P0 静默吞错防线 ----
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(TESTDATA, "kicad_cm5", "CM5_MINIMA_3.kicad_pro")
        dst = os.path.join(td, "CM5_MINIMA_3.kicad_pro")
        with open(src, "rb") as fi, open(dst, "wb") as fo:
            fo.write(fi.read())
        run("F1 P0: 缺.net 必须 exit2 且含 No netlist",
            [PY, os.path.join(HERE, "un_mcp.py"), "overview", dst],
            expect_exit=2, must_contain=["No netlist"])

    # ---- I. 使用流程动线（v0.5.1）----
    um = os.path.join(HERE, "un_mcp.py")
    run("I1 目录输入→扫出工程清单 exit2",
        [PY, um, "overview", os.path.join(TESTDATA, "pca10056")],
        expect_exit=2, must_contain=["pca10056.PrjPCB", "designs"])
    kicad_net = os.path.join(TESTDATA, "kicad_cm5", "CM5_MINIMA_3.net")
    if os.path.exists(kicad_net):
        run("I2 裸 .net→拒识+kicad_pro 线索 exit2", [PY, um, "nets", kicad_net],
            expect_exit=2, must_contain=[".kicad_pro"])
    else:
        RESULTS.append(("I2 裸 .net", None, "样例缺失，跳过"))

    # ---- C. pdf_probe 档位判定 ----
    if os.path.exists(pdf_l2):
        run("C1 pdf_probe L2 矢量PDF", [PY, os.path.join(HERE, "pdf_probe.py"), pdf_l2],
            must_contain=["L2"])
    else:
        RESULTS.append(("C1 pdf_probe L2 矢量PDF", None, "样例缺失，跳过"))
    if os.path.exists(pdf_l3):
        run("C2 pdf_probe L3 扫描版", [PY, os.path.join(HERE, "pdf_probe.py"), pdf_l3],
            must_contain=["L3"])
    else:
        RESULTS.append(("C2 pdf_probe L3 扫描版", None, "样例缺失，跳过"))

    # ---- D. lceda eprj3 ----
    if os.path.exists(eprj3):
        run("D1 lceda_parse eprj3", [PY, os.path.join(HERE, "lceda_parse.py"), eprj3],
            expect_exit=0)
    else:
        RESULTS.append(("D1 lceda_parse eprj3", None, "样例缺失，跳过"))

    # ---- G. cadence_dat_parse（BeagleBone 三件套）----
    dat_dir = os.path.join(TESTDATA, "cadence_dat")
    cdp = os.path.join(HERE, "cadence_dat_parse.py")
    if os.path.exists(os.path.join(dat_dir, "pstxnet.dat")):
        run("G1 dat overview(312网/385器件)", [PY, cdp, dat_dir],
            must_contain=["网络总数: 312", "385"])
        run("G2 dat comp U5(AM3358)", [PY, cdp, dat_dir, "comp", "U5"],
            must_contain=["AM3358BZCZ100", "324"])
        run("G3 dat xnet VBUS", [PY, cdp, dat_dir, "xnet", "--net", "VBUS"],
            must_contain=["FB7", "P3"])
        run("G4 dat 坏目录 exit2", [PY, cdp, "/tmp/definitely_no_dat_here"],
            expect_exit=2)
    else:
        RESULTS.append(("G1-G4 cadence_dat", None, "样例缺失，跳过"))

    # ---- H. eagle_parse（Pi_Wedge XML）----
    eagle = os.path.join(TESTDATA, "eagle_sample", "Pi_Wedge.sch")
    ep = os.path.join(HERE, "eagle_parse.py")
    if os.path.exists(eagle):
        run("H1 eagle overview(28器件/20网)", [PY, ep, eagle],
            must_contain=["器件总数: 28", "20"])
        run("H2 eagle xnet SDA", [PY, ep, eagle, "xnet", "--net", "SDA"],
            must_contain=["JP3", "JP8"])
        fake_sch = tempfile.NamedTemporaryFile(suffix=".sch", delete=False, mode="w")
        fake_sch.write("LTspice not eagle\n")
        fake_sch.close()
        run("H3 eagle 非Eagle文件 exit2", [PY, ep, fake_sch.name],
            expect_exit=2, must_contain=["EAGLE"])
    else:
        RESULTS.append(("H1-H3 eagle_parse", None, "样例缺失，跳过"))

    # ---- B. MCP 三格式（--quick 跳过）----
    if not args.quick:
        um = os.path.join(HERE, "un_mcp.py")
        run("B1 MCP Altium overview(344)", [PY, um, "overview", altium],
            must_contain=["器件总数: 344"])
        run("B2 MCP KiCad overview(84)", [PY, um, "overview", kicad],
            must_contain=["器件总数: 84"])
        run("B3 MCP Cadence overview", [PY, um, "overview", cadence],
            must_contain=["器件总数:"])
        run("B4 MCP Altium erc --triage", [PY, um, "erc", altium, "--triage"],
            must_contain=["需人工确认"])

    # ---- J. 安装目录同步自检（工作副本 vs ~/.workbuddy/skills/）----
    import hashlib
    INST = os.path.expanduser("~/.workbuddy/skills/schematic-reader")
    files = [("SKILL.md", os.path.join(HERE, os.pardir, "SKILL.md"),
              os.path.join(INST, "SKILL.md"))]
    for s in ("un_mcp.py", "pdf_probe.py", "netlist_json.py", "lceda_parse.py",
              "cadence_dat_parse.py", "eagle_parse.py", "run_regression.py"):
        files.append((s, os.path.join(HERE, s), os.path.join(INST, "scripts", s)))

    def md5(p):
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    for name, src, dst in files:
        src, dst = os.path.normpath(src), os.path.normpath(dst)
        if not os.path.exists(dst):
            RESULTS.append((f"J 同步 {name}", False, f"安装目录缺文件: {dst}"))
        elif md5(src) != md5(dst):
            RESULTS.append((f"J 同步 {name}", False,
                            f"工作副本与安装目录不一致\n  {src}\n  {dst}\n  → cp 后再发布"))
        else:
            RESULTS.append((f"J 同步 {name}", True, ""))

    # ---- 汇总 ----
    print("\n" + "=" * 62)
    print("schematic-reader 回归结果")
    print("=" * 62)
    n_ok = n_fail = n_skip = 0
    for name, ok, out in RESULTS:
        if ok is None:
            mark, n_skip = "SKIP", n_skip + 1
        elif ok:
            mark, n_ok = "PASS", n_ok + 1
        else:
            mark, n_fail = "FAIL", n_fail + 1
        print(f"  [{mark}] {name}")
        if ok is False:
            print(f"         {out[:200]}")
    print("-" * 62)
    print(f"  PASS {n_ok} / FAIL {n_fail} / SKIP {n_skip}")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
