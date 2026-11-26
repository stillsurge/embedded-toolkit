# 嵌入式故障诊断器（embedded-debug-trees）

**作用**：按症状定位 MCU 固件与硬件故障根因。每一步先给证据采集动作（回读寄存器、示波器、故障快照）再下判断，避免"直接开药"。

当前版本 **1.4.1**：十一棵树、69 个节点。

## 十一棵树

| 树 | 覆盖内容 |
|---|---|
| HardFault | CFSR 按位解读、FPU / NOCP、LOCKUP、故障快照 |
| 通信不通 | 配置 → 时序 → 数据流三层，含 RS485 方向控制 |
| DMA | 只收一次、错位、偶发损坏、Cache 一致性、DMAMUX |
| CAN / CAN-FD | 物理层、位时序、过滤器、发送邮箱、bus-off |
| RTOS | FromISR、优先级映射、时基没跑 |
| 启动失败 | VTOR、复位源、SWD 连不上 |
| 低功耗与唤醒 | 睡死、时钟回落、进不了低功耗、调试器影响 |
| USB | 识别不到、枚举失败、CDC、缓冲对齐 |
| 片上 Flash | 写不进、等待周期、读保护 |
| RTC | 时钟源、写保护、首次上电 |
| LCD | 背光、花屏、触摸 |

## 命令

- `search`：按症状关键词检索。支持中英文、同义词、中文整句反向匹配、bigram 兜底；`--tree` 限定树，`--format json` 供程序解析
- `show`：整树展示
- `rootcauses <tree>`：指定树的根因排行，按实战经验排序并如实标注（必须带树名，如 `rootcauses hardfault`）
- `see`：跨树线索与转入

检索不到时明确返回 `E_NOT_FOUND`，不编造决策路径。

## 评测

- 检索评测由 `tools/knowledge_bench.py` / `tools/knowledge_check.py` 执行，CI 强制
- 用例数与召回 / p@1 / MRR 见 `benchmarks/knowledge-recall.md`
- 触发用例：40 正 + 19 反
- 触发实测（2026-10-20，路由 `deepseek_for_coding`）：命中率 52.5%，反例 33/33 零误触发。未触发主因是强路由模型对咨询型问题直接作答，详见 `benchmarks/trigger-results-trees.md`

## 边界

不用于：寄存器事实查询（用 `embedded-register-lookup`）、寄存器写入核验（用 `embedded-register-verify`）、配置语义坑（用 `embedded-peripheral-pitfalls`）、电机行为故障（电机控制域）、FPGA/RTL 排障（不在本库范围）。
