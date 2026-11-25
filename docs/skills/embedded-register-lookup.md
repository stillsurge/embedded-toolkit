# 寄存器百事通（embedded-register-lookup）

**作用**：基于芯片的 CMSIS-SVD 查外设、寄存器、位域、复位值、中断号与 NVIC 使能位。每条结论带 `source`（文件、设备、版本）与 `label`（证据等级）。

当前版本 **1.11.1**。

## 能力清单

### 查询与解码

- 按名字查外设 / 寄存器 / 位域：`lookup USART1.CR1.UE`
- 地址反查：`addr 0x4001380C`
- 寄存器值按位解码：`decode RCC.CR 0x00040002`
- 位域速查（掩码、复位值、枚举）与位图：`fields` / `diagram`
- 写值计算（值可用枚举名）：`set TIM1.CR1 CEN=1 DIR=UP`
- 中断号与 NVIC 使能位、优先级字节（如 `NVIC.IPR9 第 1 字节`）：`irq`
- CMSIS 风格宏生成，含枚举值宏与 `isDefault` 默认项说明：`macros`
- 双芯片对比、外设级整体对比：`diff --chip-a ... --chip-b ...`
- 地址区间查询

### 读改写语义提示

`decode --write`、`set`、`lookup` 寄存器视图三处都会提示读改写陷阱，覆盖：

- `modifiedWriteValues`（写 1 清零、写 1 置位等）
- `readAction=modifyExternal`

### 写通道关联

自动关联置位 / 清位 / 翻转寄存器：

- `OUT0` → `OUTSET0` / `OUTCLR0` / `OUTTGL0`
- `GPIO_OUT` → `GPIO_OUT_SET` / `_CLR` / `_XOR`

### SVD 定位与质量

- 环境体检：`doctor`（本机 SVD 从哪来、有没有）
- 本机芯片清单：`devices --filter STM32`
- SDK 自带 SVD 自动发现：PlatformIO / Arduino15 / ESP-IDF / Pico SDK / CMSIS-Pack，覆盖 ESP32 系列与 RP2040
- SVD 质量检查：`lint`（识别厂商常见的多宽度视图 / 位域别名，不误报）
- 解析缓存，SVD 改动后自动失效

### 边缘写法兼容

- 裸寄存器名直接查（AVR / MSP430 风格 `lookup UCSR0B`，重名时列候选）
- `addr` 低地址自动按 AVR 数据空间口径（`0x800000+`）探测
- `isDefault` 枚举默认项渲染为"其余值，默认"，核验器 E05 不误报
- Markdown 表格输出（`--format md`），可直接粘贴进文档

## 输出与集成

- 默认中文文本；`--format json` 输出统一信封，供 Agent 解析；`--out 文件` 保存
- 零配置试用：`--demo` 使用内置合成演示芯片（非真实芯片）
- 与 `embedded-register-verify` 共用同一份 SVD 与缓存规则，核验报告的 `next` 字段可直接执行本技能命令
