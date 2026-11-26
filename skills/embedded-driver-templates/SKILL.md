---
name: embedded-driver-templates
description: 预验证驱动模板与外设初始化顺序查询工具——算法层纯 C99 平台无关，平台差异全部收在 port 适配层（示例给 STM32 HAL，dht11 另附 Arduino 写法，换其它平台照此自己写）。当用户要移植常用驱动——DHT11、DS18B20、HC-05、HC-SR04、MPU6050、SSD1306、SG90 舵机、28BYJ-48 步进、ESP8266-AT——或问这个驱动占哪些外设、初始化顺序有什么硬要求、接线怎么接有什么坑、换一块芯片怎么改时使用。9 款驱动全部带验证记录+接线表+坑清单，外设用法取自各驱动适配层注释原句。模板是移植参考非即拷即用；不生成新驱动代码（用 embedded-code-generator）、不做协议一致性判定与报文拆解（随嵌入式联调专家包提供）。
license: MIT
compatibility: Python 3.10+，仅标准库，离线运行；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.0.1"
  display_name: 嵌入式驱动模板库
---

# 嵌入式驱动模板库 1.0.0

移植驱动前先查这里：**9 款预验证驱动**（DHT11 / DS18B20 / ESP8266-AT / HC-05 / HC-SR04 / MPU6050 / SG90 舵机 / SSD1306 / 28BYJ-48 步进），覆盖**温湿度、测距、显示、无线、姿态、电机**几大类最常用外设。算法层是纯 C99 不依赖任何库，平台差异全部收在 port 适配层，换芯片只改 port 层——**要填的适配接口每款 2-5 个**（`dht11`/`ds18b20` 各 5 最多，`stepper_28byj48` 2 最少；`esp8266at` 是纯解析库但仍要填 3 个 UART 接口），示例以 **STM32 HAL（F4 头文件）**为主，`dht11` 另给一份 Arduino 写法。每款带：

- **验证记录**（各驱动 assets/ 下 meta 信息文件的 verified 字段：该款的 C 断言项数 + 口径 + 没验到什么——如 `assets/hc05__meta.json`）
- **接线表**（assets/ 下各驱动自带的接线表文件：引脚对照、供电要求、常见坑——如 hc05 的接线表是 `assets/hc05__wiring.md`）
- **坑清单**（各驱动 assets/ 下 meta 信息文件的 common_pitfalls 字段：供电/时序/初始化顺序的实战坑）
- **外设占用与初始化硬要求**（取自各驱动 *_port.h 适配层注释**原句**——回答"这个驱动到底要哪几个外设、初始化顺序上有什么硬要求"，不凭记忆讲 HAL 顺序）

**验证口径**（2026-10-27 实跑，不是打算跑）：9 款逐款 `gcc 16.2.0 -Wall -Wextra -O1` **零警告**编译，C 逻辑测试合计 **107 项断言 0 失败**，Python 交叉验证 **49 项**通过。**测试台随包发布**，这些数你可以自己重跑：

```bash
python tests/run_c_tests.py        # 需要 gcc；跑完只往系统临时目录写产物
```

`tests/stub/` 是 9 份**假端口头**（不含任何 HAL/CMSIS），靠 `#include <xxx_port.h>` 的尖括号搜索顺序顶掉真 port 层，所以**不需要装任何芯片厂商的库**就能编译。⚠️ 这只证明**算法层在 PC 上算得对、编得过**；**上板实测一款都没做过**——真机时序（DWT 微秒精度、I2C 拉伸、单总线采样）仍以你自己的板子为准。

**引擎与 mcu-debug-mcp v4.5.4 core.py 同源（S2）**：函数原样抽取，`assets/` 下驱动文件以 `<驱动名>__<文件名>` 平铺（平台 Skill 包仅支持两级目录），内容与上游 `mcu_debug_mcp/drivers/` 同一份。

## 何时使用

- "MPU6050 接 I2C 哪些脚 / 移植要注意什么"
- "ESP32/Arduino 上怎么读 DHT11 / 移植要注意什么"（DIY/创客场景）
- "SSD1306 驱动有没有现成的 / 初始化顺序什么要求"
- "HC-05 模块怎么接 / AT 模式波特率多少"
- "这些驱动都占哪些外设、HAL 符号要哪些"
- 排查"外设配了却读不到数"——先查适配层初始化顺序硬要求

## 何时不用

- 生成新的通用 C 模块（环形缓冲/状态机/PI 控制器等 15 类）→ embedded-code-generator
- 协议一致性判定（两边对不上哪边错了）/ 报文逐字段拆解 → 这两类能力随「嵌入式联调专家」包提供，本库不含
- 实机验证驱动行为 → 调试域工具（mcu-debug-mcp 的 serial/analyze 系列）

## 命令

```bash
python scripts/driver_templates.py list                 # 9 款驱动一览（含验证记录）
python scripts/driver_templates.py get hc05             # 驱动全文
python scripts/driver_templates.py wiring mpu6050       # 接线与避坑
python scripts/driver_templates.py api                  # 外设占用与初始化顺序总览
python scripts/driver_templates.py api-get mpu6050      # 单驱动初始化要求全文
python scripts/driver_templates.py demo
```

## 输出纪律

- 驱动查询结果带验证记录（assets/ 下 meta 信息文件原文），照实说口径：**零警告编译 + 107 项 C 断言 + 49 项 Python 交叉验证，但一款都没上板实测**；用户想复跑就指本包 `tests/run_c_tests.py`
- 初始化顺序要求引用适配层注释**原句**，不转述不脑补
- 模板是移植参考：提示用户按自己芯片的 HAL/LL 库适配 port 层，改完对照该芯片手册复核寄存器、时钟数与位域（尤其 port 层示例里的定时器时钟）
