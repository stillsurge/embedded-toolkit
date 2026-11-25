#!/usr/bin/env python3
"""产品出厂测试方案：填入判定值，输出完整规范（Markdown）。

用法：
  python spec_gen.py --board "电机驱动板v1" --model "BLDC 24V 100W" \\
      --i-min 0.05 --i-max 0.8 --temp-max 75 --burn-hours 48 --burn-temp 45 \\
      --low-temp -20 --high-temp 70 --esd-kv 4 --profile 工程 -o spec.md

档位（对齐 SKILL 使用流程）：
  --profile 产线  只含 L1 功能全检 + L2 老化（发产线执行）
  --profile 工程  含全部四层 L1-L4（默认；设计验证用）
判定值来源三选一：设计规格书 / 评审纪要 / 试产实测——来源不明的不许填。
"""
import argparse
import datetime
import io

REC_FIELDS = """## 通用记录字段（每张测试记录必含）

```
产品型号：________  硬件版本：{hw_ver}  固件版本：{fw_ver}
测试日期：________  测试员：________  批次号：________
测试设备：________（设备编号/校准有效期）
环境温度：________℃  环境湿度：________%
供电电源：________V（实测）  电源设备编号：________
```

> **铁律**：固件版本必须记录——版本不可追溯的测试记录等于白测。
"""

TPL_HEAD = """# {board} 产线测试规范

硬件版本：{hw_ver}  固件版本：{fw_ver}  产品：{model}
规范版本：1.0  生成日期：{date}
档位：{profile_label}
判定值来源：{source}（设计规格书/评审纪要/试产实测——来源不明的判定值重定）

---

"""

TPL_L1 = """## L1 功能全检（100%，节拍 ≤{takt} 分钟/台）

| # | 测试项 | 操作 | 判定标准 | 不合格处置 |
|---|---|---|---|---|
| 1 | 上电电流 | 电源限流 {i_limit}A，上电读电流 | 在 [{i_min}, {i_max}] A 内，无限流保护动作 | 直接判不良，标记短路位号 |
| 2 | 电源电压 | 万用表逐轨测 | 各轨标称 ±3% | 判不良，记录实测值 |
| 3 | 时钟起振 | 示波器或读状态寄存器 | 频率标称 ±50ppm | 判不良，重点查晶振负载电容贴装 |
| 4 | 通信自检 | 上位机握手 | 超时时间内正确应答 | 判不良，区分"无回复/错回复" |
| 5 | 传感器通道 | 标准激励 | 读数精度范围内 | 判不良，记录偏差值 |
| 6 | 执行器 | 软件触发 | 动作正常 | 判不良 |
| 7 | 指示灯 | 目检 | 状态符合定义 | 判不良 |
| 8 | 按键 | 逐个按压 | 响应无连击 | 判不良，记录键号 |
| 9 | 版本核对 | 读固件版本 | 与当批一致 | **停线**——版本错误是批次性事故 |

**记录表**：每台一张 L1 记录，不合格项标红，随不良品流入返修区。

---

"""

TPL_L2 = """## L2 老化测试（{burn_sample}）

条件：{burn_hours} 小时 / {burn_temp}℃ / 供电 {burn_volt}% / {burn_load}

监控（每 30 分钟）：通信心跳无失联 | 电流漂移 <{drift}% | 温度 ≤{temp_max}℃ | 功能轮询全过 | 复位计数=0

老化后必复测 L1 全项——关键精度漂移 ≤{retest_drift}%。

---

"""

TPL_L3 = """## L3 温循与低温启动（{env_sample}）

温循：{low_temp}℃ ~ {high_temp}℃ × {cycles} 次，驻留 {dwell} 分钟
转换速率：≤{ramp} ℃/min（避免热冲击，除非特意做冷热冲击试验）
低温启动：{low_temp}℃ 静置 30min 后首次上电一次成功
温循后：精度漂移 ≤{retest_drift}%，BGA/QFN 焊点显微抽检无裂纹

---

"""

TPL_L4 = """## L4 ESD 抽检（{esd_sample}）

接触 ±{esd_kv}kV / 空气 ±{esd_air}kV，每点正负各 10 次
判据 A：放电中后功能完全正常
判据 B：放电中可暂降、放电后自动恢复、数据无损坏
不合格：需重启恢复/元件损坏/数据丢失 → 整改

---

"""

TPL_REJECT = """## 不合格品处置

红标签+不良描述 → 隔离区 → 返修 → 重走 L1 全检
批次不良率 >{batch_limit}% → 停线查批次性原因
"""


def main():
    ap = argparse.ArgumentParser(description="产品出厂测试方案")
    ap.add_argument("--board", required=True, help="板名")
    ap.add_argument("--model", default="", help="产品型号")
    ap.add_argument("--hw-ver", default="V1.0")
    ap.add_argument("--fw-ver", default="V1.0")
    ap.add_argument("--i-min", type=float, required=True, help="L1 正常电流下限 A")
    ap.add_argument("--i-max", type=float, required=True, help="L1 正常电流上限 A")
    ap.add_argument("--i-limit", type=float, help="电源限流值 A（默认 i_max×1.5）")
    ap.add_argument("--takt", type=float, default=2.0, help="L1 节拍上限 分钟/台")
    ap.add_argument("--temp-max", type=float, required=True, help="允许最高温度 ℃")
    ap.add_argument("--burn-hours", type=int, default=48)
    ap.add_argument("--burn-temp", type=float, default=45)
    ap.add_argument("--burn-volt", type=int, default=100, help="老化供电百分比")
    ap.add_argument("--burn-load", default="满载轮换")
    ap.add_argument("--burn-sample", default="100%")
    ap.add_argument("--drift", type=float, default=5.0, help="老化电流漂移上限 %%")
    ap.add_argument("--retest-drift", type=float, default=2.0, help="复测精度漂移上限 %%")
    ap.add_argument("--low-temp", type=float, required=True)
    ap.add_argument("--high-temp", type=float, required=True)
    ap.add_argument("--cycles", type=int, default=24)
    ap.add_argument("--dwell", type=int, default=30)
    ap.add_argument("--ramp", type=float, default=5.0, help="温循转换速率上限 ℃/min")
    ap.add_argument("--env-sample", default="抽 3 台")
    ap.add_argument("--esd-kv", type=int, default=4, help="接触放电 kV")
    ap.add_argument("--esd-air", type=int, default=8, help="空气放电 kV")
    ap.add_argument("--esd-sample", default="每 100 台抽 1 台")
    ap.add_argument("--batch-limit", type=float, default=5.0, help="批次停线不良率 %%")
    ap.add_argument("--source", default="设计规格书", help="判定值来源")
    ap.add_argument("--profile", default="工程", choices=["产线", "工程"],
                    help="产线版=只含 L1/L2（发产线执行）；工程版=含全部四层 L1-L4")
    ap.add_argument("-o", default="spec.md")
    a = ap.parse_args()
    if a.i_limit is None:
        a.i_limit = round(a.i_max * 1.5, 2)
    a.profile_label = ("产线版（只含 L1/L2，发产线执行）" if a.profile == "产线"
                       else "工程版（含全部四层 L1-L4）")
    body = [TPL_HEAD.format(date=datetime.date.today().isoformat(), **vars(a)),
            REC_FIELDS.format(hw_ver=a.hw_ver, fw_ver=a.fw_ver), "\n---\n\n",
            TPL_L1.format(**vars(a)), TPL_L2.format(**vars(a))]
    if a.profile == "工程":
        body += [TPL_L3.format(**vars(a)), TPL_L4.format(**vars(a))]
    body.append(TPL_REJECT.format(batch_limit=a.batch_limit))
    with io.open(a.o, "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(body))
    print(f"规范已生成: {a.o}（{a.profile_label}）")
    print("判定值来源核对:", a.source, "——来源不明的不许填")
    print("归档命名建议: spec_{}_{}_{}.md（板名_硬件版本_日期，规范升版可追溯）".format(
        a.board, a.hw_ver, datetime.date.today().strftime("%Y%m%d")))


if __name__ == "__main__":
    main()
