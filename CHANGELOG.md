# 变更记录

本项目的版本号在 `.claude-plugin/plugin.json`（插件聚合版本）与各技能 `SKILL.md` 的
`metadata.version`（技能独立版本）两处维护。质量门 `tools/check_repo.py` 会校验技能版本与脚本
`__version__` 一致。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。完整历史见
[Releases](https://github.com/stillsurge/embedded-toolkit/releases)。

## [1.24.2] - 2026-10-21

### 变更

- 作者名统一为「周衡」。
- 五个技能的市场能力介绍改为「痛点 + 硬指标」写法。

## [1.24.1] - 2026-10-21

### 修复

- 三个新技能的 `--help` 补使用示例（epilog）：用户旅程审计发现新人首跑断点。
- 技能版本升 patch：trees 1.3.1 / pitfalls 1.2.1 / timing 1.1.1。

### 文档

- 补时序审查单收编闭环与 v1.3.0 FPGA 触发抽测记录。

## [1.24.0] - 2026-10-20

### 新增

- 排障决策树补 CAN/CAN-FD 树与 DMA 坑类别，覆盖嵌入式高频故障面（11 树 / 23 类），依据字段补齐。
- 覆盖面收口：flash 补 QSPI/XIP 坑，通信树补物理层根因（共地 / 接反 / 电平），评测 +2（232 例）。

### 修复

- 五技能全量体检：核验语义、时序公式、检索量具、元数据一致性。
- `timing-calc` 输出在 GBK 控制台因 `µ` 字符崩溃，stdout 统一 UTF-8。
- 测试辅助函数改用 `write_bytes`，兼容 Python 3.9（CI 修复）。
- 把关复核：usb-enum 描述符口径（18 字节是设备描述符）、mpu 背景区域语义（PRIVDEFENA 非 region 0），
  补 `next`×20 / `see`×18 闭环。

### 文档

- 避坑清单依据字段补齐至 148/148 并重新生成 references。
- README 增加「让 Agent 更愿意查库」建议配置。
- 回填 v1.2.0 触发轮（`deepseek_for_coding` 路由）：决策树 52.5% / 避坑 14.3%，反例 33/33 零误触发。

## [1.22.1] - 2026-10-20

### 变更

- 知识技能 description 重构：中文症状句前置。
- 真机触发 A/B 回填：描述前置后 +10pp（决策树 49% → 59%、避坑 38% → 47%），反例零误触发。

## [1.22.0] - 2026-10-19

### 新增

- 知识技能并入：排障决策树 v1.1.0 + 外设避坑清单 v1.1.0。

### 修复

- 清理误入仓库的评测原始产物与嵌套重复目录。

## [1.21.1] - 2026-10-18

### 新增

- 核验器 E13 规则（写 1 清零寄存器读改写）、pico-sdk 生态支持（verify 1.16.0）。

### 修复

- 交付体检修正：E13 覆盖判定、闭环提示、`--define` 警告（verify 1.16.1 / lookup 1.11.0）。

## [1.21.0] - 2026-10-17

### 新增

- 细节深化 III：C/C++ `enum` 常量求值、补丁模式用整文件做上下文（verify 1.15.0）。

## 更早版本

v1.20.0 及以前的变更见 [Releases](https://github.com/stillsurge/embedded-toolkit/releases)。
