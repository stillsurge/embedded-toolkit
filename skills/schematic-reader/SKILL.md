---
name: schematic-reader
description: 原理图识别（大模型的手和眼）：把 .PrjPCB(Altium)/.DSN(Cadence)/.kicad_pro(KiCad)/.eprj3(立创EDA)/.netlist.json(通用网表)/.dat三件套(OrCAD网表)/.sch(EAGLE 6+ XML) 解析成引脚级网表，支持器件/网络/连通性查询与 ERC 枚举；矢量 PDF 提取文本层做预读；扫描版明确标注不可靠。只输出确定性解析事实，不做审查判断——判断交给大模型。按"文件类型→识别档位"分层降级，每档标注置信度，不硬猜。Use when 原理图识别、读原理图、查信号连接、网络表提取、schematic parsing、netlist extraction。关键词：原理图识别、网表、连通性、信号追踪、Altium、KiCad、Cadence、立创EDA、SchDoc、netlist.json、Eagle。不用于：审查结论/评分/Go-No-Go（大模型自己的职责）、PCB 布局文件（.PcbDoc/.kicad_pcb/Gerber）、EMC/SI 分析、BOM 成本核算、扫描图 OCR 逆向。
license: MIT
compatibility: 依赖 universal-netlist（四通道自动选：native 二进制 / PATH / managed npx / PATH npx，Node 20+ 仅 npx 通道需要；不装则用自研纯 Python 解析器覆盖 .dat 三件套 / Eagle XML / .netlist.json / 立创 eprj3-eprj2-esch2-epcb2）。PDF 文本层走纯 Python（缺 pymupdf 自动 pip --user 安装）。需要 Python 3.10+。扫描版/图片不支持。
metadata:
  author: fangcun
  version: "1.0.0"
  display_name: 原理图识别器
---

# 原理图识别器（schematic-reader）

> 实测基线：Altium PCA10056（344 器件/236 网络，复跑 SHA-256 一致）、KiCad CM5 载卡（U1 引脚级正确）、Cadence MULTIO（含器件 notes）、立创 EDA 官方样例；矢量 PDF 12 页解析出 381 个 refdes；MCP 工具面 11 个全部逐项实测。
> ERC 三分法校准：CM5 载卡 126 个 single_pin → 63 unconnected + 63 模块对侧 + 0 需人工；PCA10056 的 2 个为 DNS 去耦脚。③桶为 0 时直接报“无实质问题”。

把用户给的原理图文件按档位识别成结构化数据，供大模型做后续判断。核心纪律：**只出事实，不出结论；确定性优先，不确定就降级明说，不硬猜**。

## 第一步：识别档位（拿到文件先做这个）

| 档位 | 输入 | 能做到 | 置信度标注 |
|---|---|---|---|
| **L1 全量** | .PrjPCB / .DSN / .kicad_pro（或根 .kicad_sch） | 引脚级网表：器件、网络、连通性、ERC | 确定（解析器直读，非推理） |
| **L1-J 通用** | .netlist.json（universal-netlist 导出或任何工具产出） | 与 L1 同款查询，纯 Python 本地跑（无 MCP/Node） | 确定（schema 硬校验；哈希软校验） |
| **L1-D OrCAD 网表** | .dat 三件套（pstxnet/pstxprt/pstchip，同目录） | 引脚级网表+PART_VALUE+引脚功能名，纯 Python | 确定（文本直读；无 variant/DNS——那在 .DSN 里） |
| **L1-E Eagle** | .sch（EAGLE 6+ XML） | 引脚级网表（signal/pinref 显式连通性），纯 Python | 确定（XML 直读；≤5 二进制拒识引导重存） |
| **L2 预读** | EDA 导出的矢量 PDF（有文本层） | refdes 清单、net label、页结构、分页定位 | 部分确定（无连通性，须声明） |
| **L3 拒识** | 扫描版 PDF / 图片 / 无文本层 PDF / EAGLE≤5 二进制 .sch / LTspice .asc | 不硬猜 | 标注"不可靠"，要求补 L1/L2 文件 |

判断方法：
- 看扩展名 → L1 直接进第二步；`.netlist.json` → 走 netlist_json.py（本地，见下）；**给的是目录 → 预检会自动扫出里面的工程清单**（或主动 `python un_mcp.py designs <目录>`）
- **KiCad 单独给 .net 文件不行**（实测：上游只认工程入口）——改给 .kicad_pro，解析器自动用旁边的 .net
- PDF 用 `python scripts/pdf_probe.py <file.pdf>` 探测文本层：有 refdes/net label 结构 → L2；纯图片 → L3（pymupdf 装在专用 venv 时脚本自动切换，无需手动换解释器）
- L3 输出固定话术："这个文件无法做引脚级识别（扫描版/图片）。请在 EDA 里导出：Altium→Smart PDF 或原理图工程打包 .PrjPCB+SchDoc；KiCad→导出 PDF（File>Export>Schematic PDF）或给 .kicad_pro 工程。"

## 第二步：L1 全量解析（universal-netlist，三通道自动选）

**启动通道（脚本自己选，不用人管）**：native 二进制（`%LOCALAPPDATA%\universal-netlist\bin\universal-netlist-windows-x64.exe`，无 Node 依赖）→ managed npx → PATH npx。native 安装：PowerShell 跑 `irm https://raw.githubusercontent.com/IntelligentElectron/universal-netlist/main/install.ps1 | iex`。另外 WorkBuddy 若已启用 universal-netlist 连接器，也可以直接调 MCP 工具（同等能力）。

**stdio 客户端脚本命令面：**

```bash
python scripts/un_mcp.py tools                              # 列 11 个工具
python scripts/un_mcp.py designs <目录>                      # 发现工程
python scripts/un_mcp.py overview <design>                  # 工程速览：器件统计+主控候选+电源网络（认识一块板子的第一步）
python scripts/un_mcp.py nets <design>                      # 列全部网络
python scripts/un_mcp.py components <design>                # 器件全量清单（省略 --type 即全量；前缀自发现，不漏件）
python scripts/un_mcp.py components <design> --type R       # 按 refdes 前缀过滤
python scripts/un_mcp.py comp <design> U1                   # 单器件全引脚+MPN+描述
python scripts/un_mcp.py xnet <design> --net VDD_nRF        # 按网名追连通链
python scripts/un_mcp.py xnet <design> --pin U1.H23         # 从引脚追连通链
python scripts/un_mcp.py search <design> --nets --pattern "^SWD"      # 网名正则
python scripts/un_mcp.py search <design> --by mpn --pattern "TPS"     # 器件字段搜（refdes/mpn/description/value）
python scripts/un_mcp.py erc <design>                       # ERC 电气检查（原始输出）
python scripts/un_mcp.py erc <design> --triage              # ERC + single_pin 三分法降噪（推荐）
python scripts/un_mcp.py variants <design>                  # 列 variant
python scripts/un_mcp.py vdns <design> <variant>            # 该 variant 的 DNS 清单
python scripts/un_mcp.py vdiff <design> <A> <B>             # 两 variant diff
python scripts/un_mcp.py export <design> [out.json]         # export-json：批量查询前先导一次 → 转本地 netlist_json.py（毫秒级）
python scripts/un_mcp.py call <tool> --design <d> --args '{"json":...}'   # 通用入口（兜底任何工具）
```

**design 预检已内建**：路径不存在 / 单独给 .SchDoc（提示同目录 .PrjPcb）/ 乱扩展名（给支持格式清单）→ 精确指引，不裸栈。

**list_components 前缀自发现**：type 必填且无通配——脚本用 `type:"*"` 触发一次报错，从 `Available prefixes: [...]` 解析该设计的真实前缀全集再遍历（实测 PCA10056 16 个前缀含 FID/BAT，KiCad CM5 含 H/M/MODULE/USB）。**静态前缀表永远补不齐，别手写死**。

**Cadence .dat 三件套（OrCAD 第三方网表包）——自研解析器，MCP 不支持：**

拿到的是 `pstxnet.dat` + `pstxprt.dat` + `pstchip.dat`（三个同目录，OrCAD "Export Netlist" 产物，没有 .DSN 时用）：

```bash
python scripts/cadence_dat_parse.py <目录或pstxnet.dat>              # overview：网/节点/器件统计
python scripts/cadence_dat_parse.py <路径> nets [--pattern VBUS]     # 网络清单
python scripts/cadence_dat_parse.py <路径> comp U5                   # 器件全引脚+PART_VALUE
python scripts/cadence_dat_parse.py <路径> xnet --net VBUS           # 网络连通成员
python scripts/cadence_dat_parse.py <路径> search --by mpn --pattern AM335
python scripts/cadence_dat_parse.py <路径> erc                       # single_pin 确定性枚举
```

- 连通性主体是 pstxnet.dat（FILE_TYPE=EXPANDEDNETLIST，NET_NAME→NODE_NAME→引脚号+功能名），**引脚级完整，L1 级置信度**
- 实测 BeagleBone Black 官方网表：312 网/1710 节点/385 器件；AM3358 的引脚功能名（AIN0-7/MDC/DDR_A13）直接可读
- **边界**：三件套不含 CIS variant/DNS 装配信息（那在 .DSN 里）——variant 相关问题必须拿 .DSN

**Eagle（EAGLE 6+ XML）——自研解析器：**

```bash
python scripts/eagle_parse.py <板.sch>                # overview
python scripts/eagle_parse.py <板.sch> nets [--pattern GP]
python scripts/eagle_parse.py <板.sch> comp JP1       # 器件引脚+deviceset
python scripts/eagle_parse.py <板.sch> xnet --net SDA
python scripts/eagle_parse.py <板.sch> search --by value --pattern LM
python scripts/eagle_parse.py <板.sch> erc            # single_pin 枚举
```

- EAGLE 6.0 (2011) 起 .sch 为 UTF-8 XML，`nets/net/segment/pinref` 显式连通性，**L1 级置信度**（实测 SparkFun Pi_Wedge v12：28 器件/20 网，SDA→JP3.11/JP8.SDA 引脚级正确）
- **.sch 扩展名多工具共用**（KiCad legacy / OrCAD / LTspice / TINA）——脚本看文件头判源，非 Eagle XML 给精确拒识话术
- EAGLE ≤5 二进制：拒识，引导用 Eagle/Fusion 重存 XML 或 KiCad 导入转 .kicad_pro
- **LTspice .asc：不做**——画布格式无显式网表，恢复连通性要几何重建，成本/受众不成比例（判"引导"：导出 SPICE netlist 或转其他格式）

**立创EDA（EasyEDA Pro）——独立解析器，不依赖 universal-netlist：**

```bash
python scripts/lceda_parse.py <工程.eprj3>     # 文件夹工程：索引+各页器件/网线/网名
python scripts/lceda_parse.py <页.esch2>       # 单页原理图
python scripts/lceda_parse.py <板.epcb2>       # PCB：PAD_NET 直接给 pad→net 表（24 pads → GND/VCC 实测通过）
```

- `.eprj3` 是官方开放格式（JSON 索引 + JSON-line 文档），本脚本直接解析，输出 L1.5 级（器件+Designator+DeviceName+网名+导线拓扑）
- `.eprj`（SQLite 单文件，老格式）用 vendor/ 内的 easyeda-pro-analyzer（MIT）单独起 MCP
- 引脚级连通性：原理图符号在系统库，本机没装立创EDA时不可得——已标注，不硬猜；PCB 侧 PAD_NET 无此限制

**L1-J：.netlist.json 本地查询（纯 Python，无 MCP/Node/npx）**——universal-netlist 的开放导出格式，任何工具产出的 `.netlist.json` 都能查；也是 `export` 子命令导出后做批量查询的落地路径：

```bash
python scripts/netlist_json.py overview <file>              # 工程速览（含 NC/single_pin 统计）
python scripts/netlist_json.py nets <file> [--pattern I2C]  # 列全部网络（可正则过滤）
python scripts/netlist_json.py components <file> [--type R] # 器件清单
python scripts/netlist_json.py comp <file> U1               # 单器件全引脚（NC 脚直接列出=回答"哪些脚没用"）
python scripts/netlist_json.py xnet <file> --net VDD        # 追连通链（穿透 0Ω/电感/磁珠，保守规则见下）
python scripts/netlist_json.py xnet <file> --pin U1.H23     # 从引脚追
python scripts/netlist_json.py search <file> --nets --pattern "SCL|SDA"
python scripts/netlist_json.py search <file> --by mpn --pattern "TPS"
python scripts/netlist_json.py erc <file>                   # single_pin/NC/未命名网 事实枚举
python scripts/netlist_json.py nc <file> [refdes]           # NC 引脚枚举（配 datasheet 总脚数=未用脚集合）
```

口径说明（与 MCP 的差异，用的时候要声明）：
- **--format json**：`erc`/`nc` 支持（--format json 给结构化 JSON，适合程序化消费）；overview/xnet/search 恒为 text——机器可读优先走 `un_mcp.py export` 导出后直接读 .netlist.json 原文件
- **xnet 穿透是本地保守实现**：只穿透 value 为 0Ω 类（0/0R/0Ω/0ohm）或 refdes 前缀 L/FB/FL 的两端器件；MCP 规则可能更宽，关键结论回 MCP 复核
- **netlistHash 软校验**：上游 canonicalization（JS 侧）未复现，哈希不符只 warning 不阻塞；完整性以 universal-netlist 加载为准
- schema 结构硬校验：缺 `universalNetlistSchemaVersion`/nets/components 直接拒（防拿普通 JSON 冒充）

MCP 工具面（11 个，2026-10-20 全部实测通过）：

| 工具 | 用途 |
|---|---|
| `list_designs` | 目录下发现工程（含 design_variants） |
| `list_components` / `list_nets` | 器件/网络总览 |
| `search_nets` / `search_components_by_refdes|mpn|description` | 正则搜索（大小写不敏感） |
| `query_component` | 单器件全引脚连接 + MPN/厂商/描述 |
| `query_xnet_by_net_name` / `query_xnet_by_pin_name` | **信号追踪主力**：穿透串联元件的完整连通链（参数名是 `net_name` / `pin_name`，格式 `REFDES.PIN`） |
| `run_erc` | 电气规则检查：single_pin/未命名网络/名字空格冲突等，按 errors/warnings 分组，Do-Not-Stuff 自动跳过 |

CLI 降级（没有 Python 或脚本不可用时）：`npx -y @intelligentelectron/universal-netlist export-json <design> [out.netlist.json]` → .netlist.json（schema v2），之后用 netlist_json.py 查；`un_mcp.py export <design>` 已封装此路径（native/npx 自动选）。

**批量查询标准打法**：MCP 每次查询都重启会话（实测单次约 5.4s，含全工程解析）——一次 `export` 导出 `.netlist.json`，之后全部走 `netlist_json.py` 本地查询（毫秒级），结果与 MCP 同源同数（实测 PCA10056：344 器件/236 网络双边一致）。

**⚠ 多 variant 设计的 export 边界（2026-10-21 NanoESP32 实锤）**：export-json CLI 导出的 .netlist.json **不含 DNS/variant 标记**（指定 --design-variant 与默认导出逐字段相同）——**谁不贴装（DNS/DNI）的结论只能走 MCP 查询通道**（`vdns`/`comp --variant`）；export 只用于连通性/器件清单批量查。单 variant 设计无此问题。

**xnet 输出按 MPN 聚合**：`components_by_mpn` 里同型号同连接的器件会合并成一条，`refdes` 是数组、`total_count` 是数量（如 `["C7","C8","C12"] count:3`）——**不要只看第一个 refdes 就下结论说"漏器件"**，取数要遍历整个 refdes 数组。

输出规范：报器件数/网络数 + 文件来源 + "本结果来自确定性解析器，引脚级数据可信"。

## 第三步：L2 PDF 预读

```bash
python scripts/pdf_probe.py board.pdf            # 探测：文本层有无、refdes/net label 命中数、页数
python scripts/pdf_probe.py board.pdf --dump out.md   # 导出逐页文本摘要（按 refdes 聚合）
```

输出规范：必须带这句 → "**PDF 提取仅含文本标签，不包含连通性；引脚级连接请提供原格式工程**"。逐页 refdes 统计用来回答"这板子大概什么结构、第几页是电源"，为后续深查定位页码。

## 定位：大模型的手和眼

**本 skill 只做"识别"——把设计文件变成大模型能查的结构化数据。不做"判断"**：
- ❌ 不做审查结论（"这个设计有问题/没问题"）——判断是大模型拿着本 skill 喂的数据自己下的
- ❌ 不内置审查规则库 / CRC 检查单 / 评审 checklist
- ❌ 不做"评分 / Go-No-Go / 合规结论"类输出
- ✅ 只做：解析（网表）、查询（器件/网络/连通性）、枚举（ERC/variant/DNS 原始事实）

**给大模型（Agent 使用者）的分工说明**：本 skill 输出的所有数据都是**确定性解析结果**（解析器直读，非推理）——这就是你的"眼睛"；`un_mcp.py`/MCP 工具就是你的"手"，查什么都行。拿到数据后怎么审、下什么结论、按什么标准判，是你（大模型）的职责，与本 skill 无关。ERC 结果只是**解析器视角的机器事实**（如"这根网只挂了一个脚"），不是审查结论；对事实的工程解读由你完成。

### 审查功能去留：定案不做（2026-10-21 评估结论，终态）

- **判断依据**：PCA10056 实测 6/6 审查场景均可由本 skill 供给事实（5/6 一步到位），两个缺口（符号不画 NC 脚 / 不能按功能猜网名）均有确定性替代路径（datasheet 引脚总数 − 网表脚数、引脚反查优先）——**事实供给已覆盖审查需求，不需要规则库**。
- **结论**：审查判断永远归大模型；本 skill 不做、也不再扩展任何审查类能力（规则库/checklist/评分/Go-No-Go 一律不做）。已建的 `erc --triage` 属于**确定性事实降噪**（把显然无意义的 single_pin 分流），不算审查，保留。
- **后续迭代范围**：只做"手和眼"的深化——格式覆盖、解析健壮性、查询命令丰富度。谁再提"给 skill 加审查规则"，把这段甩过去。

## 第四步：数据输出（识别完交给大模型判断）

按用户问题组合上面工具，输出固定结构：
- **结论先行**：先答用户问的（"这信号连到哪"/"这页有什么"）
- **证据表**：引脚级数据直接引用网表字段（器件 refdes、pin、net）
- **下一步建议**：给出可直接执行的后续查询命令

### 审查场景的标准打法（2026-10-21 实测 6 场景校准）

大模型拿本 skill 做审查时，按场景选路径。核心经验：**引脚反查优先于网名猜测**。

| 审查场景 | 标准打法 | 供给完整度 |
|---|---|---|
| 电源域去耦配置 | `xnet --net VDD_xxx` 拉全网节点 → 逐个 `comp` 查 value | ✅ 容值+数量全出 |
| 天线/时钟匹配网络 | `xnet --net <天线/晶振网>` → 看每器件 pin→net 拓扑 + value | ✅ 含串并关系 |
| I2C/SPI 上拉配置 | **不要猜网名**：先 `comp <主控>` 找 SCL/SDA 引脚 → 拿 net → `xnet` | ✅ 电阻值+模拟开关配置位全出 |
| USB/接口防护 | 引脚反查（D+/D-）或 `xnet` → ESD 器件/测试点是否在位 | ✅ |
| 晶振/时钟源配置 | `xnet` 追 XL1/XL2 类网络 → solderbridge 配置位状态 | ✅ 含 SB 通断 |
| NC/未使用引脚 | `comp <主控>` 列全引脚 + `erc --triage` 的 single_pin + **外部 datasheet 引脚表对照** | ⚠️ 见下方 gap 说明 |

**两个已知 gap 与缓解（2026-10-21 评估实锤）**：
1. **NC 审查**：原理图符号常常不画 NC 脚（实测 PCA10056 的 U1 74 脚里 0 个带 NC 名），skill 只能回答"每个连了的脚连到哪"，回答不了"哪些脚没用"。缓解：大模型拿 datasheet 引脚总数 - 网表出现的脚 = 未用脚集合，再逐个看处理方式。
2. **网名发现**：按功能语义搜网名不可靠（搜 `I2C` 空手而归——实际网名是 `SCL/SDA`；搜 `USB` 找不到——实际是 `D_P/D_N`）。网名是设计者随手起的。缓解：审查场景一律走**引脚反查**（`comp` 主控 → 引脚名/网络 → 追查），或 `list_nets` 全量枚举后人肉识别。

### ERC 结果的降噪（解析器职责，判断留给大模型）

`un_mcp.py erc <design> --triage` 只做**数据降噪**——把 ERC 的 single_pin 原始 finding 分成三桶，输出的是"分好类的原始事实"，不是结论：

| 桶 | 分类依据（纯事实） |
|---|---|
| ① 无意义 | KiCad `unconnected-` 前缀网（解析器自己标记的未连接脚） |
| ② 模块/连接器对侧单脚 | 挂在 Module*/J/CN 连接器 refdes 上的单脚网（客观拓扑特征） |
| ③ 其余 | 不满足①②特征的，原样留给大模型判断 |

实测校准数据（供大模型参考的先验）：CM5 载卡 126 个 single_pin → ③桶 0 个；PCA10056 的 2 个③桶追踪后实为 DNS 去耦（去耦电容在 variant 里被跳过）。**③桶和大模型的工程解读是什么关系，由大模型定**——本 skill 不替它下"正常/异常"的结论。

**variant / BOM 装配对比**（多 variant 设计）：

```bash
python scripts/un_mcp.py variants <design>                     # 列全部 variant
python scripts/un_mcp.py vdns <design> <variant> [--type R]    # 该 variant 的 DNS（不贴装）清单
python scripts/un_mcp.py vdiff <design> <variantA> <variantB>  # 两个 variant 的器件/DNS diff
```

实测：LAUNCHXL-CC1310 `Standard` variant → `vdns` 报 13 个 DNS（Value 标记型，`dns:true` 来自 query/list）。**注意边界**：官方文档实锤 CIS variant-only 的未贴装器件（如 R13 的 0Ω variant-only DNI）在 `list_components` 分组里**不带 dns 标志**，但 `query_component` 单查 R13 返回 `dns:true, manufacturer:"DO NOT MOUNT"`——所以 **vdns 清单数可能少于实际 DNI 数**，关键器件一律用 `query_component` 复核，不拿 vdns 当唯一依据。

ERC 原始 finding 的直译（事实对照，供大模型解读时用）：

| ERC finding | 直译（机器事实） |
|---|---|
| `net.single_pin` | 网络只挂了一个脚 |
| `net.unnamed` | 网络是自动命名（NetC3_2 这类局部名） |
| `skipped.dns` | Do-Not-Stuff 跳过数：当前 variant 有 N 个器件未贴装 |

## 支持与不支持

| 支持 | 不支持 |
|---|---|
| Altium .PrjPCB + .SchDoc（多页/harness/端口/总线连接） | .PcbDoc / .kicad_pcb / Gerber / ODB++（PCB 布局，另行选型） |
| Cadence OrCAD .DSN（含 CIS variant / Do Not Stuff） | LTspice .asc / TINA / Qucs（无显式网表或小众，判引导） |
| **Cadence .dat 三件套（自研 cadence_dat_parse.py，实测 BeagleBone）** | EAGLE ≤5 二进制 .sch（拒识，引导重存 XML） |
| KiCad .kicad_pro / .kicad_sch（.net 旁路免 kicad-cli，实测） | 扫描版 PDF / 图片 / 手绘（硬拒，不 OCR 硬猜） |
| **Eagle 6+ .sch XML（自研 eagle_parse.py，实测 Pi_Wedge）** | 立创EDA 原理图侧引脚级（v4 符号几何在云端系统库，本地工程不内嵌——导线级网络可给） |
| **立创EDA Pro .eprj3 / .esch2 / .epcb2 / .eprj2（自研解析器；eprj2=v4 主格式 SQLite，PCB 侧 pad→net 引脚级实测）** | .netlist.json 的 netlistHash 强校验（上游 JS canonicalization 未复现，只做软校验） |
| **.netlist.json 通用网表（L1-J 本地查询，纯 Python；export round-trip 实测）** | 加密 .DSN 无密码时（支持解密但密码须用户提供） |
| 矢量 PDF 文本层预读（L2） | EMC/SI/热分析（用 pcb-emc-guard 知识类技能） |
| ERC 电气规则检查 | BOM 成本/供货分析 |

## 已知边界（诚实清单）

- **KiCad 已实测**（cm5-minima 载卡）：有工程旁导出的 .net 时直接解析成功（本机无 kicad-cli 也能跑）；U1=LIS3DH 引脚级正确；ERC 126 个 single_pin 经三分法全部归位（63 个 unconnected NC + 63 个 CM5 模块对侧单脚，0 个需人工确认）
- **Cadence .DSN 已实测**（MULTIO）：解析/ERC 正常；list_components 需带 `{"type":"U"}` 参数（type 必填）
- **Cadence .dat 三件套（pstxnet/pstxprt/pstchip）MCP 不支持** → 用自研 `cadence_dat_parse.py`（连通性完整）；但 CIS variant 的未贴装信息不写入 .dat——**variant 问题必须拿 .DSN**，只有 .dat 时 DNS 判据只剩 Value 标记一种
- **加密 OrCAD .DSN**：设 `UNIVERSAL_NETLIST_DSN_PASSWORD_FILE`（密码文件路径，每行一个密码）或 `UNIVERSAL_NETLIST_DSN_PASSWORD`（单密码）环境变量后重跑即可——脚本 spawn/子进程继承环境，密码只从环境读取，不进工具调用/输出/日志（上游承诺）。典型报错 `Password-protected OrCAD design: set ...` 或 `No password ... opens this OrCAD design`（给的密码全不对）
- **DesignError 防线**：设计级错误（缺 .net/文件损坏/加密没密码）会 exit 2 并透出解析器原文+处置清单——**绝不会显示"器件总数 0"**；若看到 0 器件+正常退出，是版本过旧，更新脚本
- **KiCad 网名带页路径前缀**（如 `/CM5/BT_nDis`），query_xnet 必须带全前缀，先 `search_nets` 拿精确网名再查
- 扫描版 PDF / 图片 / 手绘（硬拒，不 OCR 硬猜）
- 密码保护的 OrCAD 设计：读环境变量取密码（见 universal-netlist docs/password-protected-designs.md）
- **Cadence CIS variant 设计必须选 variant**：声明了 variant 的 .DSN 拒收 `<Default>`，要先 `list_designs` 看 `design_variants` 再传 `design_variant` 参数
- **立创EDA 原理图侧连通性（2026-10-21 二次修订，CLI 实测）**：实际创建/保存过的工程符号几何**完整内嵌**在 esch2（PART/PIN 块）——lceda_parse.py 已实现引脚级连通性推导（PART/PIN/LINE 并查集分网 + NETFLAG 网名），与官方 Protel 网表逐脚对账一致；未命名网（$1N2 类）用 WIRE 组 id 代名。仅 example 工程类（引用系统库未保存几何）退化到导线级。PCB 侧 PAD_NET 引脚级不受影响
- **.netlist.json（L1-J）**：schema v1/v2 均可读（结构相同）；netlistHash 软校验（未复现上游算法，不阻塞）；xnet 串联穿透为保守规则（0Ω 类 + L/FB/FL 前缀两端器件），关键结论回 MCP 复核；普通 JSON（无 universalNetlistSchemaVersion）直接拒
- **单独 .SchDoc/.kicad_sch**：MCP 经 .PrjPcb/.kicad_pro 发现工程，单页文件预检拒给（root .kicad_sch 例外可试）；预检失败时脚本给出同目录工程线索
- 本 skill 是**识别底座（手和眼）**：只输出解析事实，不输出审查判断——审查结论由大模型基于本 skill 提供的数据自行得出

## 排错

| 症状 | 处置 |
|---|---|
| 给的是目录 | 预检自动扫出同目录工程清单+designs 指引；或主动 `designs <目录>` |
| 查网名报 "Net 'X' not found" | 查询 miss：用 `nets` 列全部或 `search --nets --pattern <关键词>`；KiCad 网名带页路径前缀要带全 |
| 查器件报 "Component 'X' not found" | 查询 miss：`components` 列全部或 `search --by refdes --pattern <前缀>` |
| 给 .net 报预检失败 | 正确行为：.net 不能单独喂，改给同目录 .kicad_pro（实测纠偏，上游只认工程入口） |
| MCP 工具不可用 | 脚本三通道自动选（native/npx）；或走 L1-J：`un_mcp.py export` 导出后 `netlist_json.py` 本地查；或 CLI 降级 `npx -y @intelligentelectron/universal-netlist export-json ...` |
| 启动报"找不到 universal-netlist 启动方式" | 三通道全失败：装 native 二进制（install.ps1，无 Node 依赖）或装 Node 20+ 让 npx 进 PATH |
| design 预检失败（不存在/单独 .SchDoc/乱扩展名） | 脚本已给精确指引：补 .PrjPcb（会同目录线索）、`designs` 发现工程、或对照支持格式清单 |
| list_components 报 "No components with prefix '*'" | 这是**前缀自发现的探测手段**，正常；真要列器件用 `components` 子命令（省略 --type 自动全量） |
| list_components 报 "Missing required parameter: type" | type 必填且无通配——别直接 call list_components，用 components/search 子命令 |
| export 失败（exit 1） | 解析器命名第一个缺陷：通常是文件损坏或非完整工程（如只给单页 .SchDoc） |
| netlist_json.py 报"普通 JSON 不是 Universal Netlist" | 文件缺 universalNetlistSchemaVersion——不是导出格式；用 `un_mcp.py export <design>` 从原格式重新导出 |
| 解析退出码 1 | stderr 有解析器报错，通常是文件损坏或非完整工程（如只给了单个 .SchDoc 没给 .PrjPCB）→ 引导用户补工程文件 |
| xnet 报 -32602 "expected string, received undefined at net_name/pin_name" | 参数名写错了：是 `net_name` 和 `pin_name`（pin_name 格式 `REFDES.PIN`），不是 netName / refdes+pin |
| list_components 报 type undefined | `type` 参数必填：`{"type":"U"}`（按 refdes 前缀过滤） |
| query_xnet 报 "Net ... not found"（KiCad） | KiCad 网名带页路径前缀（`/CM5/BT_nDis`），必须带全；先 `search_nets` 拿精确网名 |
| Cadence 报 "<Default> refused"（声明了 variant 的设计） | 该设计必须选具体 variant：先 `list_designs` 看 `design_variants`，把名字传进 `design_variant` 参数 |
| 传 .dat 报 "Unsupported design file format" | MCP 不支持 .dat——用 `cadence_dat_parse.py`（同目录三件套一起给） |
| 报 "defines design variants [...] Pass design_variant" | 多 variant 设计（Altium Not-Fitted 分组 / CIS）：查询命令加 `--variant <名字>`；名字见报错原文或 `variants <design>` |
| 报 "Password-protected OrCAD design" | 加密 .DSN：设 `UNIVERSAL_NETLIST_DSN_PASSWORD_FILE`（每行一个密码的文件）或 `UNIVERSAL_NETLIST_DSN_PASSWORD`，重跑即解 |
| 报 "No password ... opens this OrCAD design" | 给的密码全不对：核对密码文件内容/编码（1-255 可打印 ASCII） |
| .sch 报"不是 EAGLE 6+ XML" | .sch 扩展名多工具共用：看文件头判源——二进制=EAGLE≤5（重存）；`(kicad_sch`=KiCad legacy（本 skill 不吃 legacy，转 .kicad_pro）；LTspice/TINA=不支持 |
| 大模型要审查结论 | 本 skill 只给数据不给判断——审查逻辑是大模型自己的职责 |
| KiCad 报找不到 kicad-cli | 设 KICAD_CLI_PATH 环境变量；或工程旁有导出的 .net 时可自动识别（实测 cm5-minima 无需 kicad-cli） |
| PDF 探测显示 0 命中 | 大概率扫描版 → 走 L3 话术 |
| npx 首次跑卡住 | 在拉包，等；或先 `npm install -g` 亦可 |
| 命令行传 JSON 参数报解析失败 | Windows 下 JSON 参数**不能以 `^` 开头**（被 cmd 当转义符吃掉，如 `{"pattern":"^SWD"}`）；改用不含 `^` 的 pattern 或改用文件传参 |
| Python subprocess 调脚本找不到文件 | 传 **Windows 风格路径**（`盘符:\project\...`）；Git Bash 的 `/d/work/...` 会被 Windows Python 解析成错误盘符路径而失败 |
