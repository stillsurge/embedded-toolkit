# schematic-reader 更新日志

## v0.8.2（2026-10-21）—— skill 发布定稿

- frontmatter compatibility 更新到实际状态：universal-netlist 四通道自动选（native 二进制 / PATH / managed npx / PATH npx）；不装 universal-netlist 时自研纯 Python 解析器覆盖 .dat 三件套 / Eagle XML / .netlist.json / 立创 eprj3·eprj2·esch2·epcb2；pymupdf 缺失自动 pip --user 安装；Python 3.10+
- 版本历史移入独立 CHANGELOG.md（发布物更干净）

## v0.8.1（2026-10-21）—— 上架前通用性加固（功能零新增）

- un_mcp 通道探测补第四通道 `shutil.which("universal-netlist")`（他人机器官方 installer 装完 native 在 PATH，显式候选路径探测不到）
- pdf_probe pymupdf 自愈链补第二级：专用 venv 没有 → 当前解释器 pip --user 自动装（阿里云镜像）→ 自动重跑 → 仍失败才报错（他人机器零手动配置）
- run_regression 移除开发机 venv 硬编码路径（pdf_probe 自愈链接管）
- 回归 35/35 全绿

## v0.8.0（2026-10-21）—— 立创原理图引脚级连通性落地

- parse_sch_page 重写：PART/PIN 块解析（内嵌符号定义）+ 引脚绝对坐标推导（COMPONENT 位置 + rotation 旋转符号局部坐标）
- 三个实测踩坑修复：①PIN 短 id（e3/e7）跨符号重复——Pin Number ATTR 按"PIN 块紧跟其 ATTR"文件顺序配对；②WIRE 组是绘制合并不是电气网络——LINE 端点重合做并查集分网；③NETFLAG 命中条件节点结构错误——修正为 len(node)==3 and node[1]=='seg'
- 引脚级推导与立创官方导出的 Protel 网表**逐脚对账完全一致**（4 器件 8 脚验证）
- 输出新增 schematics[].pin_nets（"DESIGNATOR.PIN" → 网名）
- 未命名网（立创自动名 $1N2 类）文件中不存名，用 WIRE 组 id 代名（结构不受影响）

## v0.7.0（2026-10-21）—— 立创 eprj2 主格式解锁

- native 二进制装好（免 Node 依赖），find_server 双候选探测（LOCALAPPDATA + D:\tools）
- 立创EDA Pro v4.1.78 逆向：v4 主格式 .eprj2（SQLite 单文件）——PCB 侧 PAD_NET(pad_obj,pin,net) = pad→net 引脚级全通（实测 82 pad/17 网，D1.2→VCC_IN 正确）；SCH 器件 34 件全带 MPN/厂商/立创编号（attributes 表按 device_uuid 直查）
- lceda_parse.py 新增 parse_eprj2_sqlite（sqlite3 标准库零依赖）

## v0.6.1（2026-10-21）—— 第二轮真板验证（穷尽清单）

- vdiff 真实 SKU 差异通过（NanoESP32 ABX00083 vs ABX00092：唯一差异 JP1/JP2 DNS 翻转，交叉验证语义正确）
- export 补 --design-variant 透传；实锤上游 CLI 盲区：导出的 .netlist.json 不含 DNS/variant 标记——DNS 结论只能走 MCP 查询通道（已写进警告与 SKILL.md）
- xnet 穿透真板对照通过（本地保守穿透 vs MCP 在真实 0Ω R14 双边一致）
- --help drift 抽查 4 脚本无漂移

## v0.6.0（2026-10-21）—— 真实工程实战检验

- BLDC_Controller（STM32F405+IR2136 FOC 板）全审查动线通过：overview 154 器件 → U 类 9 件 → comp U6 引脚反查（PA8/9/10→H1/H2/H3 桥臂）→ xnet → erc triage
- NanoESP32（Arduino ABX00083）抓到真 gap：声明 variants 但查询命令面无 --variant——补齐全部查询命令 `--variant` 透传 + DesignError 专项提示给可复制命令例子
- 实测教学：Altium 导出网表 description 常为空——主控识别用 components --type U 看 comment 字段

## v0.5.2（2026-10-21）—— 动线完善

- netlist_json.py `--format json` 补齐实现（原来声明了没实现）
- run_regression 新增 J 组：工作副本 vs 安装目录逐文件 md5 对比（忘同步直接报红）
- 中文+#+空格文件名实测 MCP 全通

## v0.5.0~0.5.1（2026-10-21）—— 健壮性

- DesignError 防线：设计级错误 exit 2 并透出解析器原文（不吞错）
- 使用流程动线：目录输入自动扫工程、查询 miss 对症指引、目录友好化
- pymupdf 自愈安装

## v0.4.0（2026-10-21）—— 三通道 + 新格式

- 启动三通道自动选（native / managed npx / PATH npx）
- 新格式 L1-J .netlist.json（纯 Python 本地查询）与 .dat 三件套、Eagle 6+ XML 自研解析器
- design 预检：路径存在性 + 扩展名识别 + 单 .SchDoc 提示同目录 .PrjPcb
- search/export 命令、list_components 前缀自发现（不漏件）、overview 主控候选词边界匹配
- pdf_probe/lceda_parse 坏文件防护

## v0.1~0.3（2026-10-20~21）—— 初版

- Altium .PrjPCB / KiCad / Cadence .DSN 引脚级解析（universal-netlist MCP）
- ERC 三分法降噪（single_pin 分桶：NC / 模块对侧 / 需人工）
- 矢量 PDF 文本层 L2 预读 + 扫描版 L3 拒识
- 立创 eprj3/esch2/epcb2 解析器、PCA10056/BeagleBone/Pi_Wedge/CM5 真板实测
