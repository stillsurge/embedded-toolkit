# 嵌入式寄存器写入审计器（embedded-register-verify）

**作用**：核验 C/C++ 代码里的寄存器写入是否与芯片 SVD 一致。输出分"报 / 未判定 / 通过"三桶，退出码 1 表示检出问题。

当前版本 **1.17.0**。

## 命令

**零配置（不需要 SVD、芯片或代码文件）：**

```bash
python scripts/verify.py demo      # 用内置演示芯片 + 内置样例跑一遍 E01–E13，退出码 0 = 工具正常
python scripts/verify.py doctor    # 环境体检：本机有哪些 SVD 来源、怎么上手
python scripts/verify.py rules     # 列出核验规则
```

**核验真实代码（需要芯片 SVD）：**

```bash
python scripts/verify.py check main.c --chip STM32G431                      # 按芯片名找本机 CMSIS-Pack
python scripts/verify.py check src/ --svd ./STM32G431xx.svd --checklist     # 直接给 SVD 文件
python scripts/verify.py check --patch changes.diff --chip STM32G431        # 只验补丁新增行
python scripts/verify.py check main.c --chip ESP32-S3 --headers "$IDF_PATH/components/soc/esp32s3/include/soc"
```

`--checklist` 生成逐项复查清单；`--format json` 给 Agent 解析；`--explain` 把寄存器定义内联进报告。
补丁模式只核验新增行，但文件级检查（E06/E07/E11）会用磁盘上的完整文件做上下文，未改动的时钟
使能可见，不会误报。

## 检出规则

| 编号 | 规则 |
|---|---|
| E01–E05 | 外设 / 寄存器 / 位域存在性、值超宽、枚举合法性 |
| E06–E07 | 时钟使能、硬编码地址 |
| E10 | 中断分组 |
| E11 | 使能后写 DMA 配置寄存器 |
| E12 | 只写寄存器读改写 |
| E13 | 写 1 清零寄存器上的读改写（掩码未覆盖全部 W1C 位时会把已置位标志顺带清零；掩码未知记未判定） |

## 覆盖的代码写法

- 文件类型：`.c` / `.h` / `.cpp` / `.cc` / `.cxx` / `.hpp` / `.hh` / `.hxx` / `.ino`
- CMSIS 结构体写：`USART1->CR1`
- CMSIS 宏：`SET_BIT` / `MODIFY_REG`（置位值兼容字段相对与 ST 风格带位置两种约定）
- 厂商别名：`NRF_USBD`、`R_PORT0`、`R_` 前缀
- 地址别名宏：`#define REG (*(volatile uint32_t *)0x...)`
- 地址访问宏：`HWREG`、`HWREGBIT`、`MMIO32`、`REG32`、`_SFR_MEM8`、`_SFR_IO8`
- 指针表达式写入、函数宏作左值（`GPIO_ODR(GPIOA) |= x`）
- 裸寄存器名（AVR / MSP430 风格 `PORTB = 0xFF`）
- CMSIS union / 数组风格：`PORT->Group[0].DIRSET.reg`
- Renesas FSP：`REG_b` 位域视图、`R_GPT0` 指针宏按地址解析
- Silicon Labs：端口字母 `P[3]` → `PD_DOUT`、`REG.FIELD` 直写、`_S` 安全别名
- pico-sdk / RP2040：小写指针宏 `dma_hw->intr`、`_u()` 拼贴宏、嵌套成员 `resus.ctrl` → `CLK_SYS_RESUS_CTRL`
- TI 直寄存器宏（`SYSCTL_RCGC2_R`），指针别名按地址核验
- 通道名同义写法：`DMA1_Channel3` ↔ `DMA1_CH3` ↔ SVD 后缀 `CCR3`
- ESP-IDF `REG_WRITE` / `REG_SET_FIELD`（需配 `--headers`；`#include` 自动跟随、分号分隔多 include 目录、多参数函数宏、`BIT(n)`）
- 文件内与头文件的 C/C++ `enum` 常量求值（隐式自增按 C 语义）

## 判定细节

- 位域直写按位域宽度判断超宽
- `isDefault` 默认项不误报
- AVR 数据空间 `0x800000` 口径自动探测；`char` / `unsigned char` / `short` 等指针类型全覆盖
- 条件编译块降级处理（E01 / E02 / E03 / E10 / E12 / E13）
- 补丁模式用整文件做上下文，E06 / E07 / E11 不因未改动的使能 / 置位误报
- 汇总带按类计数与未判定原因分布，附复查清单

## 输出与闭环

- 每条问题带 `next` 字段：可直接执行的 `embedded-register-lookup` 命令（已带本次 `--svd` / `--chip` / `--demo` 参数）
- `--explain` 把寄存器定义内联进报告，含写 / 读语义与相关置位 / 清位寄存器建议
- 支持目录模式与 `git diff` 模式（`--patch`）
- 只做词法分析，不执行被检查代码

## 实测记录

- 注入集召回 229/229 = 100%（合成芯片，见 `benchmarks/verify-recall.md`）
- 正样本 55 文件 0 误报
- 真实源码 0 误报：ESP-IDF v4.4.7（224 处写入）、TI TivaWare（363 处）、libopencm3 STM32F1（366 处，3 处为文件级时钟检查在库代码上的已知限制）、AVR Arduino 核心（33 处）、Microchip SAMD 核心（49 处）、Renesas RA FSP（36 处）、Silicon Labs Gecko SDK emlib（318/309 处 × 3 份 SVD）、NXP MCUXpresso（23 文件）、pico-sdk 2.1.0（22 文件 / 47 处写入，RP2040）

详见 `benchmarks/verify-dogfood.md`。

## 边界

不用于：HAL/LL 结构体配置语义（这类会进「未判定」）、外挂器件命令（Flash、传感器）、时序正确性、通用代码风格、寄存器事实查询（用 `embedded-register-lookup`）。

只认 SVD 里的名字与命名约定，不做完整 C 解析、不跨文件分析；E07 时钟使能是**文件级**检查，使能在其它文件时用 `--no-clock-check` 关闭该项。
