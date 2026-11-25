# schematic-reader —— 原理图识别器（大模型的手和眼）

把原理图/网表文件解析成**引脚级结构化数据**，供大模型（AI 助手）做后续查询与判断。
本工具只输出**确定性解析事实**（解析器直读，非推理）；审查结论由大模型基于数据自行得出。

## 能吃什么（按档位）

| 给的文件 | 档位 | 得到什么 |
|---|---|---|
| Altium `.PrjPCB` + `.SchDoc` | L1 全量 | 引脚级网表：器件/网络/连通性/ERC/variant |
| Cadence OrCAD `.DSN` | L1 全量 | 同上（含 CIS variant） |
| Cadence `.dat` 三件套（pstxnet/pstxprt/pstchip） | L1-D | 引脚级网表+引脚功能名（纯 Python，无需 MCP） |
| KiCad `.kicad_pro`（旁边最好有导出的 `.net`） | L1 全量 | 同上 |
| Eagle `.sch`（EAGLE 6+ XML） | L1-E | 引脚级网表（纯 Python） |
| `.netlist.json`（本工具导出的通用格式） | L1-J | 全套查询，纯 Python 毫秒级 |
| 立创EDA `.eprj3` / `.esch2` / `.epcb2` | L1.5 | 器件/网名/导线拓扑（PCB 侧 pad→net 引脚级） |
| 矢量 PDF（EDA 导出，有文本层） | L2 预读 | refdes 清单/页结构定位（**无连通性**） |
| 扫描版 PDF / 图片 / EAGLE≤5 二进制 / LTspice .asc | L3 拒识 | 不硬猜，给补文件话术 |

## 快速上手

```bash
# 1. 认识一块板子（第一步永远是它）
python scripts/un_mcp.py overview <design文件>

# 2. 常用查询
python scripts/un_mcp.py comp <design> U6        # 单器件全引脚
python scripts/un_mcp.py xnet <design> --net H1  # 追连通链（穿透 0Ω）
python scripts/un_mcp.py search <design> --nets --pattern "^SWD"
python scripts/un_mcp.py erc <design> --triage   # ERC 三分法降噪

# 3. 大工程批量查（先导一次，之后本地毫秒级）
python scripts/un_mcp.py export <design> out.netlist.json
python scripts/netlist_json.py overview out.netlist.json

# 纯 Python 格式（.dat 三件套 / Eagle / .netlist.json）不依赖 MCP/Node
python scripts/cadence_dat_parse.py <目录> overview
python scripts/eagle_parse.py <板.sch> overview
```

多 variant 设计（报错会提示）加 `--variant <名字>`。

## 安装与依赖

- 解压上架包，把根目录放到 `~/.workbuddy/skills/schematic-reader/`（或任何 AI 助手的技能目录）；开发副本请只拷贝 `skill/`，`testdata/`、`vendor/` 不要带入
- L1 主链路依赖 [universal-netlist](https://github.com/IntelligentElectron/universal-netlist)（Apache-2.0）：装 native 二进制（免 Node）或 Node 20+ 走 npx——脚本自动选，全失败会给安装指引；也可用 `UNIVERSAL_NETLIST_EXE` 指定 native 路径
- 纯 Python 通道（.dat / Eagle / .netlist.json）零依赖；PDF 需要 `pip install pymupdf`（或加 `--install-pymupdf` 让脚本安装）
- 加密 OrCAD .DSN：设 `UNIVERSAL_NETLIST_DSN_PASSWORD_FILE`（每行一个密码的文件）或 `UNIVERSAL_NETLIST_DSN_PASSWORD` 环境变量

## 边界（诚实清单）

- PDF 只有文本标签，**连通性不可恢复**——引脚级查询必须给原格式工程
- .dat 三件套不含 variant/DNS 装配信息（那在 .DSN 里）；export CLI 导出的 .netlist.json 也不含 DNS 标记——**不贴装结论只能走 MCP 查询通道**
- 扫描版/图片不 OCR 硬猜
- 不做审查结论/评分/Go-No-Go——那是大模型拿到数据后的职责

## 详细文档

命令全集、审查场景打法、排错表、实测记录见 [SKILL.md](SKILL.md)。
回归自检：`python scripts/run_regression.py`（35 项，改完任何脚本先跑它）。

---
license: MIT | author: fangcun
