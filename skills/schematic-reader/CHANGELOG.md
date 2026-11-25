# schematic-reader 更新日志

## v1.0.3（2026-10-26）—— 补 display_name_en（平台驳回）+ 拆掉自己造的假长度门禁

> 平台驳回：「缺少 Skill 英文展示名（display_name_en），请在 SKILL.md frontmatter 中填写」。

**根因**：frontmatter 里有 `display_name`（中文）但**没有 `display_name_en`**。
官方文档的字段表与模板都要求中英双语展示名，平台按必填校验。

**为什么又漏**：v1.0.2 的门禁只校验「YAML 能不能解析」和「描述长度」，
**没校验展示名是否存在**；`verify.py` 的 skill 必填列表同样漏了这两个字段，
所以带病包一路放行到上传环节。

**修复与加固**：
- `SKILL.md` 补 `display_name_en: Schematic Reader`
- `_pack.py` 新增**门禁 2b：中英文展示名必填**（正则独立判，不依赖 PyYAML，环境缺 yaml 也拦得住）
- `_pack.py` 门禁 8 的真 YAML 必填清单补齐 `name / display_name / display_name_en / license`
- `verify.py`：skill 必填清单补齐同名 4 项 + 改为**真 YAML 取值**（原来正则只认带引号的值，
  本包 description 无引号 → 长度检查形同虚设）；专家包**内嵌 skill 也逐个查 frontmatter**
- **拆掉假门禁**：v1.0.2 写死的 `description ≤195 / zh ≤98 / en ≤220` 是**专家包 plugin.json 的口径**，
  被错套到 skill 包上。实际已上传成功的 `embedded-timing-calc` 实测 `description 838 / zh 174 / en 389`
  全部过审——那条门禁不但没拦住问题，还把本包描述硬压到 194 字符、离线只剩 1 字符余量。
  现改为「实测成功包最大值 ×1.5」：`1200 / 300 / 600`
- 变异测试 7/7：删 `display_name_en` / 删 `display_name` / 删 `license` / 删 `version` /
  描述超长 / 塞回半角冒号 → 全部 rc=1 拦截，还原后 md5 一致

**未改动**：功能、脚本、资产（`.epcb2` cid 修复、Cadence export-json 都在）。


## v1.0.2（2026-10-26）—— 修 frontmatter 真 YAML 解析失败（平台驳回）

> 平台驳回：「SKILL.md 格式错误 — frontmatter 无法解析
> （yaml: line 5: mapping values are not allowed in this context）」。

**根因**：`description_en` 里写了 `into pin-level netlists: query components` ——
**半角冒号 + 空格**让 YAML 把它当成新的映射键，解析直接失败。
该写法是 v1.0.1 用脚本批量改写文案时引入的（原来用句号）——**把一个能解析的包改成了不能解析的**。

**为什么之前的门禁没拦住**：当时只有**正则启发式**（查「半角冒号+空格」），
没覆盖到这处形态；而平台用的是**真 YAML 解析器**。

**修复与加固**：
- 文案改为 `into pin-level netlists — query components`（破折号替代冒号）
- `_pack.py` 新增**门禁 8：frontmatter 真 YAML 解析**（`yaml.safe_load`），
  解析失败即拦截并报出错行号；缺 PyYAML 时也直接报错（不许静默跳过）
- 变异测试 4/4：放回 `netlists: query`、中文里的半角冒号+空格、删 `author` 必填字段 → 全部 rc=1 拦截

**未改动**：功能、脚本、资产（1.0.1 的 `.epcb2` 修复与 Cadence 导出桥接都在）。


## v1.0.1（2026-10-24）—— 从专家包副本回灌：修复 .epcb2 解析崩溃 + 新增 Cadence 导出桥接

> 同一个 skill 复用进 `hardware-design` 专家包后，在那边修了缺陷并加了能力，本条把它们回灌到独立版，
> 避免两个副本分叉（独立版此前仍是 1.0.0，带着同一个 bug）。

**修复（真实缺陷，两个副本都有）**
- `lceda_parse.py parse_pcb_doc` 漏定义 `cid`，PCB 文档只要含 COMPONENT 块就 `NameError` 崩溃
  —— **`.epcb2`（PCB pad→net）这条能力从来没跑通过**。已修（`cid = head.get("id")`）。
  实测对照：修复前跑 `testdata/eprj3-format/example/eprj3-example/pcb/PCB1.epcb2` 直接 NameError，修复后正常出 JSON。
  注意：1.0.0 的发布 zip（`schematic-reader-1.0.0.zip`）里带的 `lceda_parse.py` 是**未修复版**。

**新增**
- `cadence_dat_parse.py export-json`：Cadence 三件套 → Universal Netlist JSON v2 桥接，
  让 `.dat` 侧工程也能被 `netlist_json.py` / universal-netlist 下游消费。口径：只导出三件套实际存在的事实，
  没有的 MPN / Manufacturer 写 "N.A." 不猜。

**未改动**
- `run_regression.py` 仍绑定本地 testdata（本目录 testdata 齐全，不随包分发，见 `testdata/THIRD_PARTY_NOTICES.md`）。


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

- native 二进制装好（免 Node 依赖），find_server 双候选探测（LOCALAPPDATA + 用户工具目录）
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
