# 原理图识别器（schematic-reader）

**作用**：把原理图解析成引脚级网表，供后续查询器件、网络与连通性。它负责「看清」，判断留给模型。

当前版本 **1.0.3**。

## 支持格式

| 支持 | 说明 |
|---|---|
| Altium `.PrjPCB` + `.SchDoc` | 多页 / harness / 端口 / 总线连接 |
| Cadence OrCAD `.DSN` | 含 CIS variant、Do Not Stuff |
| Cadence `.dat` 三件套 | 自研解析器，实测 BeagleBone |
| KiCad `.kicad_pro` / `.kicad_sch` | `.net` 旁路，免 kicad-cli |
| Eagle 6+ `.sch` XML | 自研解析器，实测 Pi_Wedge |
| 立创EDA Pro `.eprj3/.esch2/.epcb2/.eprj2` | 自研解析器；PCB 侧 pad→net 引脚级实测 |
| `.netlist.json` 通用网表 | 纯 Python 本地查询，export round-trip 实测 |
| 矢量 PDF 文本层 | L2 预读 |
| ERC 电气规则检查 | 结果降噪后输出，判断留给模型 |

**不支持**：`.PcbDoc` / `.kicad_pcb` / Gerber / ODB++、LTspice / TINA / Qucs、EAGLE ≤5 二进制 `.sch`、扫描版 PDF 与图片（硬拒，不 OCR 硬猜）、加密 `.DSN`（密码须用户提供）、EMC/SI/热分析、BOM 成本分析。

## 工作流

1. 识别档位（拿到文件先做这个）
2. L1 全量解析：三通道自动选（native 二进制 → managed npx → PATH npx），也可经 MCP 连接器调用
3. L2 PDF 预读（矢量文本层）
4. 输出数据，交模型判断

```bash
python scripts/un_mcp.py overview <design>      # 器件统计 + 主控候选 + 电源网络
python scripts/un_mcp.py components <design>    # 器件全量清单
python scripts/un_mcp.py comp <design> U1       # 单器件全引脚 + MPN
python scripts/un_mcp.py xnet <design> --pin U1.H23   # 从引脚追连通链
```

## 依赖

原理图解析用技能自带纯 Python 解析器，零第三方依赖。仅 PDF 文本层需 `pymupdf`：默认只提示安装命令，显式加 `--install-pymupdf` 才安装。

## 边界

**只做确定性解析，不做审查判断**——原理图审查功能已评估定案不做（2026-10-21）。引脚级信息缺失时明确标注，不猜。
