---
name: embedded-code-generator
description: 说「给我一个256字节串口环形缓冲」，直接得到可编译的量产级.h+.c：15类嵌入式C模块（PI控制器、RS485、CRC、环形缓冲、SVPWM、软件I2C/SPI、FSM、DMA接收、shell、按键消抖等），含Doxygen注释与错误处理，518项gcc断言验证，未指定的参数按推荐默认值直接产出。
license: MIT
compatibility: Python 3.10+，仅标准库；生成代码可选使用本机 arm-none-eabi-gcc 编译验证；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.1.1"
  display_name: 嵌入式代码生成器
  display_name_en: Embedded Code Generator
  examples_zh:
  - 给我一个 256 字节串口环形缓冲区
  - PI 控制器代码怎么写才不积分饱和
  - RS485 收发方向切换的代码
---
# 嵌入式代码生成器

> **当前版本：1.1.0**（2026-09-28）｜**全部 15 类模板免费开放，无使用门槛**

不要让 AI 现场手写并发/时序敏感的模块——手写环形缓冲容易漏边界、手写 CRC 容易错多项式、手写 PI 容易积分饱和、手写按键消抖容易漏弹跳和回绕。本技能给出**已经过测试验证**的量产级模板：15 类常用模块的 `.h` + `.c` 文件对，每个模板包含完整 Doxygen 注释、参数校验、错误处理和使用示例，且全部通过配套审查器闭环扫描（0 高危 0 中危）与 gcc 测试套件（18 个测试 518 项断言）验证。

## 什么场景该用它

- **要一个环形缓冲/PI 控制器/CRC**：不想自己造轮子，更不想造一个没测试的轮子——直接取模板，按参数表配置即可
- **AI 生成的代码不敢直接用**：这里的每个模板都带 518 项断言的测试背书，算法正确性有据可查
- **模块质量要求高**：ISR 安全（单生产者单消费者无锁）、C99 无动态内存、C++ 兼容、定点数支持、溢出保护——这些坑模板里已经踩过一遍

## 工作流程

1. **确认模块类型**：从用户需求中判断需要哪个模块（见下方模块表）。
2. **读取模板文件**：从 `templates/` 目录读取对应的 `.h` 和 `.c` 文件。
3. **收集配置参数**：根据模块参数表向用户确认可配置项（如 Kp/Ki、引脚定义、缓冲区大小等）。**用户未指定的项直接采用下方「推荐默认值」，不要反问拖延**；仅平台相关项（引脚号、USART 实例）在用户没给时用占位宏输出并在使用说明中标注需替换。
4. **填充并输出**：根据用户参数填充配置宏和初始化代码，输出完整可编译的 `.h` 和 `.c` 文件内容。如果用户提供了 MCU 平台信息（如 STM32F4、GD32E230），在注释中补充平台适配说明。
5. **使用说明**：输出后简要说明该模块的关键注意事项（ISR 安全、时序要求等）。

## 模块清单与参数

| # | 模块 | 模板文件 | 关键参数 | 触发关键词 |
|---|------|---------|---------|-----------|
| 1 | PI控制器 | `pi_controller.h/c` | Kp, Ki, Ts(采样时间), out_min/max, i_min/max | PI、PID、比例积分、控制器、anti-windup、抗积分饱和 |
| 2 | RS485收发切换 | `rs485_tc.h/c` | DE端口/引脚, RE端口/引脚(可选), USART实例 | RS485、DE、RE、半双工、方向切换、TC标志、收发控制 |
| 3 | 一阶低通滤波 | `lowpass_filter.h/c` | fc(截止频率), Ts(采样时间) 或 alpha | 低通、滤波、LPF、IIR、一阶滤波、平滑 |
| 4 | CRC校验 | `crc_utils.h/c` | 数据缓冲区, 长度；可选CRC_USE_TABLE | CRC、校验、CRC8、CRC16、Modbus、CCITT、checksum |
| 5 | 环形缓冲区 | `ring_buffer.h/c` | 缓冲区大小, 元素类型(RB_ELEM_TYPE), 满策略 | ring buffer、环形缓冲、FIFO、队列、ISR队列、无锁 |
| 6 | SVPWM | `svpwm.h/c` | Vdc(母线电压), pwm_period | SVPWM、空间矢量、PWM、FOC、三相、PMSM、BLDC、占空比 |
| 7 | 软件I2C主机 | `soft_i2c.h/c` | SCL/SDA引脚宏, bit_delay(决定速率), 支持时钟拉伸 | I2C、IIC、软件模拟、开漏GPIO、读寄存器、WriteThenRead |
| 8 | SPI主机 | `spi_master.h/c` | mode(0~3), msb_first, cs_active_low | SPI、片选、全双工、CPOL、CPHA、四模式、Transfer |
| 9 | ADC均值滤波 | `adc_avg_filter.h/c` | ReadFn采样函数指针, N(采样次数), 去极值开关 | ADC、均值滤波、采样、去极值、防溢出、电源纹波 |
| 10 | 有限状态机框架 | `fsm_framework.h/c` | 转移表(源态/事件/目标态/守卫/动作), on_entry/on_exit | 状态机、FSM、表驱动、转移表、守卫条件 |
| 11 | DMA环形接收缓冲 | `dma_ring.h/c` | 缓冲区(须为DMA循环模式目标), 硬件写位置换算 | DMA、循环模式、circular、UART接收、idle中断、不丢包、追新数据 |
| 12 | 软件定时器 | `soft_timer.h/c` | now(时基), period, mode(单次/周期), 回调, user | 软件定时器、轮询、主循环、单次/周期、回调、回绕安全 |
| 13 | 命令行shell | `mini_shell.h/c` | 命令表(name/help/handler), MAX_ARGS | shell、命令解析、串口命令、msh、argv、命令表、调试接口 |
| 14 | 轻量断言框架 | `lite_assert.h/c` | LA_MODE(记录/停机/复位), MAX_RECORDS, 复位钩子 | 断言、assert、故障记录、量产、不停机、错误统计、防御 |
| 15 | 按键扫描消抖 | `key_scan.h/c` | KS_MAX_KEYS, KS_DEBOUNCE_TICKS, KS_LONG_PRESS_TICKS, KS_REPEAT_TICKS, KS_ACTIVE_LEVEL | 按键、按键扫描、消抖、去抖、长按、短按、连按、自动重复、key scan、debounce |

## 推荐默认值（用户未指定时直接用）

用户没有给参数时**按本表取默认直接产出代码，不要反问**；输出后在「使用说明」里列出实际采用的默认值，提醒可替换。

| # | 模块 | 推荐默认值 |
|---|------|-----------|
| 1 | PI控制器 | Ts=0.001s（1kHz），out_min/max 与 i_min/max 均为 ±1.0（归一化占空比）；Kp/Ki 未给时先用 Kp=0.5、Ki=10.0 占位并注明需按实际对象整定 |
| 2 | RS485收发切换 | DE/RE 并接同一 GPIO（占位宏 `RS485_DE_Pin`），USART1；发送完成后等 TC 标志再拉低 DE |
| 3 | 一阶低通滤波 | Ts=0.001s，fc=50Hz（速度反馈/采样平滑通用档） |
| 4 | CRC校验 | CRC16/MODBUS（初始值 0xFFFF），`CRC_USE_TABLE=1` 查表法 |
| 5 | 环形缓冲区 | 串口数据流/日志：256 字节、`RB_ELEM_TYPE=uint8_t`、满策略 OVERWRITE；命令解析：128 字节、REJECT |
| 6 | SVPWM | Vdc=24V，pwm_period=0.0001s（10kHz） |
| 7 | 软件I2C主机 | 100kHz 标准模式（`SI2C_DelayHalfBit` 半位周期 5μs）；SCL/SDA 引脚为平台相关项，用户没给时用占位宏 |
| 8 | SPI主机 | mode 0、MSB first、CS 低有效 |
| 9 | ADC均值滤波 | N=8，开去极值（N≥3 才生效） |
| 10 | 有限状态机框架 | 转移表按需求列；guard/action 未提时填 NULL（无守卫/无动作） |
| 11 | DMA环形接收缓冲 | 256 字节、uint8_t（UART ≤115200 波特率下够用） |
| 12 | 软件定时器 | 时基 1ms（SysTick），period 按用户需求 |
| 13 | 命令行shell | MAX_ARGS=8，行缓冲 128 字节，命令表按用户列出的命令填充，大小写敏感 |
| 14 | 轻量断言框架 | LA_MODE=记录模式（量产不停机），MAX_RECORDS=8，复位钩子为 `NVIC_SystemReset` |
| 15 | 按键扫描消抖 | 消抖 20ms（按 1ms 扫描周期）、长按 1s、连按重复 200ms、8 键、低有效（上拉+按键接地；高有效改 `KS_ACTIVE_LEVEL=1u`）；电平作函数参数传入，GPIO API 无关 |

## 代码质量标准

所有生成的代码遵循以下标准：

- **C99 标准**：纯 C99，不依赖外部库，无需动态内存分配（不使用 malloc/free）
- **Doxygen 注释**：每个文件、函数、结构体字段都有 `@brief`/`@param`/`@return` 注释
- **C++ 兼容**：所有头文件包含 `#ifdef __cplusplus extern "C"` 保护
- **参数校验**：所有公开函数检查 NULL 指针和非法参数，返回错误码或使用 assert
- **ISR 安全**：环形缓冲区采用单生产者单消费者无锁设计，使用 volatile 和内存屏障
- **定点数支持**：PI 控制器和低通滤波器提供 Q16.16 定点版本（条件编译）
- **溢出保护**：定点数乘法使用 64 位中间变量，加法进行溢出检查
- **配置裁剪**：通过宏定义控制功能（查表法、定点版、断言等），适应不同 Flash/RAM 预算
- **MISRA-C 考虑**：避免隐式类型转换、使用有意义的返回码、不使用变长数组

## 读取模板的方法

读取 `templates/` 下对应的 `.h` 和 `.c` 文件。每个文件是一个完整的、可直接编译的模板，包含：

- 文件头注释（功能、算法说明、使用示例、注意事项）
- 配置宏定义区
- 类型定义
- 函数声明/实现
- 使用示例（在 `@code` / `@endcode` 块中）

读取模板后，根据用户参数修改：
1. 配置宏的默认值（如 `RB_STRATEGY`、`CRC_USE_TABLE`）
2. 结构体初始化中的参数值
3. 平台相关的类型定义和底层访问函数

## 自检测试

包内 `tests/` 目录附带 18 个自检测试、共 518 项断言，覆盖全部 15 类模板的算法正确性（已补齐 PI 控制器 / 低通滤波 / RS485 / SVPWM 四类，随 DMA 环形缓冲 / 软件定时器 / shell / 断言框架 / 按键扫描五类新增，实现每类模板都有专属测试）。在包根目录执行：

```
make test
```

- **环境要求**：gcc（支持 C99 即可），PI/低通/SVPWM 测试链接 libm，无其他依赖
- **覆盖范围**：
  - CRC-8/MAXIM、CRC-16/MODBUS、CRC-16/CCITT-FALSE（位翻转与查表 `CRC_USE_TABLE` 两种编译配置）、Modbus RTU 标准帧
  - 环形缓冲区 FIFO 顺序、满缓冲 REJECT/OVERWRITE 两种策略（编译期宏分别构建）、空/满边界与参数校验
  - 软件I2C：位级从机模拟器验证 START/地址帧/读写单字节/ACK/NACK/组合传输 WriteThenRead、时钟拉伸、总线释放
  - SPI主机：边沿精确从机验证模式 0/1/2/3 四种 CPHA 采样时刻、MSB/LSB 序、全双工同时收发、事务级 CS 包裹
  - ADC均值滤波：顺序回放与固定电平两种采样源、基本均值、去极值均值（255×65535 满量程累加不溢出、255 截断保护）
  - FSM框架：表驱动转移、守卫链（首个通过者优先）、on_entry/on_exit 回调时序、自环转移、非法事件保持原态、Reset 语义
  - PI控制器：后向欧拉离散响应手算校验、抗饱和钳位（饱和期间不积分手算验证无 windup 残留）、独立积分限幅状态语义、Reset/在线重整定
  - 一阶低通：双线性变换 α 系数公式校验、阶跃响应手算（y1/y2/y3）、稳态收敛、α 强弱对比、未初始化透传保护
  - RS485方向控制：mock 平台层记录 DE 引脚时序（初始化收态/发送拉高/TC 后拉低/超时强制拉低）、BUSY 防重入、假 USART 寄存器验证 DR 最后写入字节、零长度与 NULL 参数
  - SVPWM：零矢量三相 0.5 对称、扇区角扫 30°~330° 逐扇区映射、扇区1 占空比手算、过调制限幅 [0,1]、母线电压加倍需求收缩
  - DMA环形缓冲：顺序写读、跨尾回绕、分段读（读停尾部循环调用）、 overrun 追圈重同步（读位置跳到最新有效字节）、drain 模式（NULL 出参丢弃）、参数校验
  - 软件定时器：单次到期自动失活、周期重复触发计数、Stop/Start 重装填、回调内 Stop 自身安全、uint32 回绕（0xFFFFFF9C+100 跨零精确触发）、多定时器独立计数、参数校验与池满
  - 命令行shell：argc/argv 切分（多空格/tab 容忍）、CRLF/LF 剥离、空行忽略、大小写敏感、未知命令、handler 负值透传与钳位、reply 截断保护（NUL 收尾）、NULL 参数
  - 轻量断言：通过不断言不记录、失败记录（file/line/expr）、计数饱和、池满覆盖最旧、Clear、复位钩子按 LA_MODE 编译分支行为正确
  - 按键扫描：按下/释放双侧消抖确认（19 tick 不触发、20 tick 精确触发）、弹跳拒绝（按下与释放方向的毛刺均回退）、DOWN 边沿不重复、长按 1000 tick 单次触发、连按 200 tick 节奏、再次按压可重新长按、uint32 回绕（0xFFFFFFF8 按下跨零精确确认）、双键独立计时互不干扰、非法 id 防御无副作用、低有效/高有效两种极性各编译一套全套运行
- **预期结果**：518 项断言全部 `[PASS]`，末尾打印 `=== ALL TESTS PASSED ===`，编译零警告；任一断言失败时 `make` 返回非 0

```
=== 运行输出示例（节选）===
[PASS] I2C: addr+W acked, reg byte written 0x5A
[PASS] SPI mode3: master rx 0xC3 == slave tx echoed
[PASS] Trimmed mean {100..170} == 135 (drop 1 low + 1 high)
[PASS] FSM: guard chain first-match wins, short press 2 ticks
Summary: 24 checks, 24 passed, 0 failed
=== ALL TESTS PASSED ===
```

`make clean` 清理编译产物。

## 输出格式

输出时使用 Markdown 代码块，分别标注 `.h` 和 `.c` 文件名：

```
### 文件名: module_name.h
```c
// 完整头文件内容
```

### 文件名: module_name.c
```c
// 完整源文件内容
```
```

## 注意事项

- 模板中的平台抽象层（如 RS485 的 GPIO/USART 访问、软件I2C/SPI 的引脚读写钩子）使用 weak 函数，用户应根据具体 MCU 覆盖实现。
- PI 控制器必须在固定周期 Ts 调用，采样抖动会影响控制性能，建议使用硬件定时器。
- SVPWM 输出为归一化占空比 (0.0~1.0)，需根据具体定时器 ARR 值转换为比较寄存器值。
- 环形缓冲区在 8 位 MCU（如 AVR）上使用时，需定义 `RB_ENTER_CRITICAL` / `RB_EXIT_CRITICAL` 宏保护 16 位索引访问。
- 软件 I2C 速率由 `SI2C_DelayHalfBit` 决定，标准模式 100 kHz 时半位周期约 5 μs；从机时钟拉伸依赖 `SI2C_WAIT_SCL` 等待 SCL 实际变高，勿删。
- SPI 主机模式由 `SPI_Config_t.mode`（CPOL=bit1, CPHA=bit0）一次性配置，事务中不可切换；片选极性在用户 CS 钩子内处理，模板传入语义值（1=选中）。
- ADC 均值滤波累加器为 uint32_t，N≤255 时满量程 16 位采样不会溢出；去极值模式要求 N≥3，否则自动退化为普通均值。
- FSM 转移表中同一「源态+事件」存在多条规则时构成守卫链，按表序首个 guard 通过者生效；全部 guard 失败保持原态。注意自环转移也会触发 on_exit/on_entry，副作用计数应放在动作函数而非 on_entry。
