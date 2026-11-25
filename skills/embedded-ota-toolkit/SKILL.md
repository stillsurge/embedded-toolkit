---
name: embedded-ota-toolkit
description: 让固件升级别变砖：15 条防砖规则审计 IAP/OTA 升级代码（跳转未设VTOR、未关中断、升级无CRC、擦写未喂狗等），每条附可直接粘贴的修复代码；另配 CRC 计算、分区规划、镜像打包与校验工具，覆盖 Cortex-M/RISC-V 与 Arduino/ESP8266，一键中文 HTML 报告。
license: MIT
compatibility: Python 3.10+，仅标准库，离线运行；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.2.0"
  display_name: 嵌入式OTA升级工具包
  display_name_en: Embedded OTA / Bootloader Toolkit
---
---

# 嵌入式 OTA / Bootloader 升级工具包

两个工具，一件事：**让固件升级别变砖**。

- `ota_audit.py` —— 审计侧：静态扫描升级代码，按高危/中危/低危报出防砖漏洞（不编译、不接硬件）
- `ota_tool.py` —— 工具侧：算 CRC、生成 64 字节镜像头、算分区表、打包 `.pkg`、校验包

**平台覆盖**：审计侧面向 **Cortex-M 全家族**（ST STM32 / GD32 / CH32 / APM32 / Nordic nRF5x / NXP / 瑞萨 RA…）、**RISC-V**，以及 **Arduino / ESP8266 框架层**（ESP32 用 Arduino 框架时命名词汇与 ESP-IDF 完全不同，单独适配）。规则信号同时认 ST HAL、GD32 FMC、Nordic nrfx、ESP-IDF、Zephyr、MCUboot、Arduino/ESP8266 与通用命名。工具侧（`ota_tool.py`）是**纯字节运算，与芯片平台完全无关**。详见下方「平台适用性」。

## 什么场景该用它

- **升级后一进中断就死**：跳转 APP 前忘了 `SCB->VTOR` 重定位，APP 的中断全跳到 bootloader 向量表 —— 规则 1 专抓
- **分层升级的砖机事故**：APP 分区是空的/烧了一半照跳，直接 hardfault —— 规则 3
- **“升级完能启动但逻辑错乱”**：收到的数据没校验就写 flash，传输误码变成固件 —— 规则 4
- **升级中途被看门狗打断**：擦写几秒钟不喂狗，失败一次多一次变砖机会 —— 规则 6
- **"升级成功但固件是坏的"**：NOR flash 只能把 1 写成 0，目标页没先擦就写 —— 规则 14
- **打包不知道头里放什么**：给你一个工业上够用的 64 字节镜像头格式 + 生成器 + 校验器

## 30 秒看效果

喂入一段真实风格的 IAP 跳转 + 升级写入代码：

```c
/* bootloader.c */
#define APP_BASE 0x08008000

void iap_load_app(void) {
    typedef void (*app_fn)(void);
    app_fn app = (app_fn)APP_BASE;
    __set_MSP(*(volatile uint32_t *)APP_BASE);
    app();
}

void ota_write_image(uint8_t *buf, uint32_t len) {
    flash_erase(0x08008100);
    flash_write(APP_BASE, buf, len);
    HAL_Delay(100);
}
```

审计输出（**评分 49/100**，4 高危 4 中危 3 低危）：

| 规则 | 级别 | 位置 | 问题 |
|------|------|------|------|
| R1 | 🔴 高危 | L7 | 跳转 APP 前未重定位中断向量表（全文无 `SCB->VTOR`） |
| R2 | 🔴 高危 | L7 | 跳转前未关闭中断（无 `__disable_irq`） |
| R3 | 🔴 高危 | L7 | 跳转前未校验 APP 有效性（无栈顶/向量表检查） |
| R4 | 🔴 高危 | L13 | 升级数据无完整性校验（写 flash 但无 CRC） |
| R5 | 🟡 中危 | L12 | 擦除地址 `0x08008100` 非 1K/2K/4K 整数倍 |
| R7 | 🟡 中危 | L12 | 分区地址硬编码（裸 `0x08xxxxxx`） |
| R9 | 🟡 中危 | 全文 | 无防降级版本校验 |
| R10 | 🟡 中危 | 全文 | 升级状态未持久化（掉电无法续传） |
| R11 | 🟢 低危 | L13 | flash 写未检查返回值 |
| R12 | 🟢 低危 | 全文 | 升级流程无进度输出 |
| R13 | 🟢 低危 | L14 | 升级流程中存在硬编码延时 |

## 快速上手

**审计**

```bash
python ota_audit.py bootloader.c                     # 单文件
python ota_audit.py bootloader.c high                # 只看高危
python ota_audit.py sketch.ino                       # Arduino 草图（.ino/.pde 均可）
python ota_audit.py --dir ./boot                     # 整个目录（.c/.h/.cpp/.hpp/.cc/.cxx/.ino/.pde）
python ota_audit.py --dir ./boot --html report.html  # 生成中文 HTML 报告
python ota_audit.py --dir ./boot --fail-under 80     # CI 门禁：整体分低于 80 就返回 1
```

exit code：0=无问题、1=有问题、2=用法/内部错误（CI 友好；配合 `--fail-under N` 可按分数卡门禁）。

**打包**

```bash
# 1) 算 CRC
python ota_tool.py crc app.bin

# 2) 规划分区（生成 .h，含编译期溢出断言）
python ota_tool.py layout --flash 256K --align 2K boot:32K app:96K app_bak:96K cfg:8K --out partition.h

# 3) 打包（bin + 64B 镜像头），顺带生成 MCU 侧头文件
python ota_tool.py pack app.bin -o app.pkg --addr 0x08008000 --ver 1.2.3 --hw-id 0x0001 --emit-header

# 4) 校验（可指定期望板型/地址，防串板）
python ota_tool.py verify app.pkg --hw-id 0x0001 --addr 0x08008000
```

exit code：0=成功、1=校验不通过、2=用法错误。

> 工具扫不出的部分别漏了：`references/ota-checklist.md` 是上板前的人工自检清单（含断电/断连/错包三类必做故障注入），且逐条标注了哪些已被哪条规则覆盖（`[R1]`…`[R15]`）、哪些必须上真板（`[HIL]`）。

## 新项目端到端路径（毕设/从零起步照这个顺序）

1. **规划分区**：`ota_tool.py layout` 算出分区表并生成 `partition.h`（含编译期溢出断言），bootloader/APP 都从这里取地址宏，别再手写裸地址
2. **写完升级代码先自查**：`ota_audit.py bootloader.c --html report.html`，把高危清到 0、整体分 ≥80 再上板；报告里每条问题都附可直接粘贴的修复代码
3. **打包交付**：`ota_tool.py pack app.bin --emit-header` 出 `.pkg` + MCU 侧解析头文件
4. **上板前最后一步**：`ota_tool.py verify app.pkg --hw-id 0x0001 --addr 0x08008000` 确认包完整、板型/地址没串；真板再过一遍 `ota-checklist.md` 的断电/断连/错包三类故障注入

## 审计规则速查（15 条）

| # | 级别 | 规则 | 一句话 |
|---|------|------|--------|
| 1 | 🔴 | 跳转未重定位 VTOR | 跳 APP 前必须 `SCB->VTOR = APP_ADDR` |
| 2 | 🔴 | 跳转前未关中断 | 需 `__disable_irq()` 并清 NVIC pending |
| 3 | 🔴 | 跳转前未校验 APP | 校验栈顶落在 SRAM、复位向量落在 flash |
| 4 | 🔴 | 升级数据无完整性校验 | 写 flash 前/后必须比对 CRC/哈希 |
| 5 | 🟡 | 擦除地址未按页对齐 | 非 1K/2K/4K 整数倍，会擦错页 |
| 6 | 🟡 | 擦写期间未喂看门狗 | 开了 WDT 却不喂 = 升级必被复位 |
| 7 | 🟡 | 分区地址硬编码 | 裸 `0x08xxxxxx`，应走分区表宏 |
| 8 | 🟡 | 接收等待无超时 | `while(!rx_done)` 死等，掉线即砖 |
| 9 | 🟡 | 无防降级版本校验 | 缺版本比较，可刷回漏洞固件 |
| 10 | 🟡 | 升级状态未持久化 | 状态只放 RAM，掉电即丢 |
| 11 | 🟢 | flash 写未检查返回值 | 写失败不该静默 |
| 12 | 🟢 | 升级流程无进度输出 | 现场排障只能靠猜 |
| 13 | 🟢 | 硬编码延时 | 魔数延时换平台即失准 |
| 14 | 🟡 | 升级写入前未见擦除 | NOR 只能 1→0，目标页不先擦 = 写坏 |
| 15 | 🟡 | 关闭看门狗后未见恢复 | 关了 WDT 不恢复 = 刷完跑飞再也救不回来 |

**判定口径**：

- 升级链路规则（R4、R6、R8–R15）以「OTA 语境关键字或跳转迹象」为门控；普通业务代码（例如只是往 flash 存配置）不会被升级类规则刷屏——这是刻意的误报治理
- 语境关键字用**「前一字符非字母数字」**匹配，而不是 `\b`：真实代码里它们几乎总带下划线前缀（`esp_ota_write` / `nrf_dfu_flash_store` / `gd32_ota_apply` / `my_iap_handler`），用 `\b` 会让整套升级规则**静默失效**；同时又不至于把 `quota` 这种普通词误判成 OTA
- **框架层语境额外认驼峰与点号形态**：`ArduinoOTA` / `ESPhttpUpdate` / `Update.begin(` / `Updater.write(`。这一支单独的、**大小写敏感**的正则——若带上大小写不敏感，`quota` 里嵌的小写 `ota` 会被吃进来。纯 `ArduinoOTA` 草图（`setup` 里 `begin`、`loop` 里 `handle`）不含独立的 ota 词元，只靠上面那套边界判定**根本判不出 OTA 语境，会让整套规则静默不触发、输出假的 100 分**
- 「跳转迹象」必须是**调用形态**：`__set_MSP(`、`jump_to_app(`、`((void(*)(void))addr)()`、`asm volatile("mov pc, …")`；名字里带 `start_app` 的变量、中断向量表初始化里的 `(void (*)(void))(&END_STACK)` **不算**跳转
- **跨文件存疑降级**：本文件缺某步骤、但存在「该步骤由外部模块承担」的证据（`#include "image.h"`、`verify_*()`、自建 `IV[]` 向量表、`*_partition_state()`）时，改为**低危**并标注【需人工确认·疑在外部模块完成】；没有这类证据则仍按**高危**报（不靠感觉放水，tests 里有正反例各一条守着）
- **框架代管改为 notes（不计分）**：Arduino 的擦除由 `Update` 库内部完成，sketch 里结构上永远看不到 `erase`——此时 R14 改出提示而不是问题（在框架层报 R14 恒为误报）
- **notes（不计分）**：跳转被托管给框架函数（`mbed_start_application()`、`bootloader_app_start()`）时，输出一条提示而不是"缺失"告警——避免把框架的内建三步当成漏做
- **R13 只抓"替代超时的魔数延时"**：`<50ms` 的延时视为让出 CPU／节流（Arduino 的 `delay(2)`/`delay(10)`），不报；延时所在窗口已有超时护栏（`millis()`/`deadline`/`HAL_GetTick`）时不报；Arduino `loop()` 体内的延时是空闲节拍器，不报
- R5（擦除未对齐）、R7（裸 flash 地址）是**通用 flash 卫生检查**，凡出现即报，不限于升级代码

## 平台适用性（诚实版）

分三层说清楚，避免"以为能用在某平台、其实只认 STM32 写法"：

| 层 | 适用范围 | 说明 |
|---|---|---|
| **工具侧** `ota_tool.py` | **任意平台** | CRC32/CRC16/MD5/SHA256、64B 镜像头、分区表算术、打包与校验——纯字节运算，与 MCU 架构无关 |
| **审计·架构级规则** R1 R2 R3 R8 R9 R12 | **Cortex-M 全家族 + RISC-V** | 用架构标准写法判定：`SCB->VTOR` / `__set_MSP` / `__disable_irq` / `CPSID i`（全 Cortex-M 通用）；RISC-V 认 `csrw mtvec` |
| **审计·外设级规则** R4 R5 R6 R7 R11 R13 R14 R15 | **取决于平台命名** | 已覆盖 ST HAL/SPL、GD32 FMC、Nordic nrfx、ESP-IDF、Zephyr/MCUboot、**Arduino/ESP8266** 与通用命名（`flash_write` / `flash_erase` / `*_erase_sector`） |
| **审计·框架层适配** | **Arduino / ESP8266** | 命名词汇与 ESP-IDF **完全不是一套**，单独适配 |

**框架层（Arduino / ESP8266）具体认什么**：

| 用途 | 识别的写法 |
|---|---|
| OTA 语境 | `ArduinoOTA`、`ESPhttpUpdate`、`httpUpdate`、`Update.begin(` / `Updater.write(` 等点号成员调用 |
| flash 写（R11/R14/R4） | `Update.write(...)` / `Updater.write(...)`（返回已写字节数，失败须判） |
| 完整性校验（R4 豁免） | `Update.end(true)`、`Update.setMD5(...)`——库内已完成比对 |
| 看门狗（R6/R15） | `ESP.wdtDisable(` / `ESP.wdtEnable(` / `ESP.wdtFeed(` |
| 日志（R12） | `Serial.print` / `println` / `printf` / `write`（点号形态） |
| 超时（R8） | `millis()` / `micros()`，以及 `while (client.connected())` 这类**链路等待** |
| 状态持久化（R10） | `Preferences` / `prefs.put*` / `nvs_set_*` / `EEPROM.write` |
| 扫描范围 | `.ino` / `.pde` 已纳入 `--dir` 目录扫描（早前会被整个跳过） |

**平台识别**：报告会标出识别到的平台（`arduino` / `stm32` / `gd32` / `ch32` / `nordic` / `esp-idf` / `zephyr` / `rt-thread` / `riscv` / `cortex-m`），便于判断结论可信度。识别**只用于标注，不参与打分**。`arduino` 判定**排在 `esp-idf` 之前**——ESP32 用 Arduino 框架时同样含 `esp_*` 调用，不先判框架层会被误标成 ESP-IDF。

**已知平台限制（照实说，不粉饰）**：

- **R7（裸 flash 地址）只认 `0x08xxxxxx` 系**——即 ST / GD32 / CH32 / APM32 这类 flash 映射到 `0x08000000` 的芯片。nRF52（基址 `0x00000000`）、ESP32（`0x10000`）上**不报，属漏报而非误报**。
- **ESP32 没有 `SCB->VTOR` 语义**（启动走 image header + MMU，不是重定位向量表），R1/R2/R3 不适用；工具也不会误报（已实测）。
- **框架托管型 bootloader**（mbed-bootloader，跳转交给 `mbed_start_application()`）本文件不含跳转三步，输出 notes 提示而非报缺失。
- **Arduino 只审 sketch 层，不审库内部**：擦除与校验都在 `Update` 库里，sketch 里看不见。所以 R14 在 Arduino 上改出 notes（不再当问题报）、R4 靠 `Update.end(true)` 作为"库内已校验"的证据。**换句话说：Arduino 上"没报 R4/R14"只代表 sketch 没漏做，不代表库本身没问题**——库版本的行为要自己核对。
- **AVR Arduino（Uno / Nano / Mega）天然不适用**：AVR 没有自升级代码（bootloader 是 optiboot，靠串口 STK500 烧写），sketch 里不存在 OTA 流程。这类文件判定为非 OTA 语境、得 100 分，属于**"没有可审计对象"而不是"代码安全"**，别误读。
- **不宣称"全覆盖"**：若某平台的 flash/看门狗 API 命名不在信号表内，相应规则**会静默不触发**（得出虚高的分）。拿不准时直接看 JSON 的 `signals` 字段确认信号是否被认出。

> 空口说跨平台不算数——见下节「跨平台召回验证」：四个平台各写一个真实风格的坏 bootloader，实测全部命中。

## 真实开源语料实测（判定口径的依据）

这些口径不是拍脑袋定的：每处修正都来自在**真实生产级 bootloader** 上跑出来的具体结果。
语料仅本地实测、**未随包分发**（避免第三方许可证问题），仓库与文件路径写在 `references/CHANGELOG.md` 里，可自行复现。

### 一、不该报的（成熟工程 / 普通 flash 代码）

| 类别 | 样本 | 结果 |
|---|---|---|
| 双 Bank / swap 框架（MCUboot，多平台） | `loader.c` `image_validate.c` `swap_misc.c` `boot_serial.c` | **100 分零命中** |
|  | `bootutil_misc.c`（trailer/状态工具模块） | 98 分（2 条**低危待人工确认**：校验与版本比较在独立模块） |
| 安全 bootloader（wolfBoot） | `image.c` `libwolfboot.c` `loader.c` `update_flash.c` | **100 分零命中** |
|  | `boot_arm.c`（只负责跳转那一步） | 97 分（3 条**低危待人工确认**：跳转三步在别的文件） |
| 商用 DFU（Nordic nRF52） | Adafruit `main.c` `boards.c` `flash_nrf5x.c` | **100 分零命中** |
| 框架内置 OTA | ESP-IDF `esp_ota_ops.c` `bootloader_utility.c`、Zephyr `dfu/boot/mcuboot.c`、mbed-bootloader `main.cpp` | **100 分零命中** |
| 负向对照（本不该报） | littlefs `lfs.c`、SPIFFS、Zephyr `flash_map.c`、ESP-IDF NVS、STM32 HAL `stm32f1xx/f4xx_hal_flash.c` | 7 个文件全部 **100 分零误报** |

### 二、该报的（真实隐患）

| 样本 | 结果 |
|---|---|
| ST STM32Cube `IAP_Main`（F1 / F4 / F7 三系列） | **80 分**，命中 R1+R2（真隐患：跳转前既未设 VTOR 也未关中断，而 `HAL_Init()` 已使能 SysTick）+ R9 |

### 三、跨平台召回验证（自写最小坏样本，非第三方代码）

四个平台各写一个「故意有缺陷」的 bootloader，验证规则并非 STM32-only：

| 平台 | 样本用到的真实写法 | 期望命中 | 实得 |
|---|---|---|---|
| Nordic nRF52 | `nrfx_nvmc_words_write` / `nrfx_wdt_init` / 取 APP 向量后跳转 | R1 R2 R3 R4 R6 R8 R12 | 全中（**51 分**），且不误报 R7 |
| ESP-IDF | `esp_partition_write` / `esp_task_wdt_init` / `while(!rx){}` | R4 R6 R8 R14 | 全中，且**不误报** R1/R2/R3 |
| RISC-V（CH32V） | `csrw mtvec` / `FLASH_Program` | R2 R3 R4 R8 R12 | 全中，`csrw mtvec` 被认作向量表重定位 → **不报 R1** |
| GD32（FMC） | `fmc_page_erase(0x08008100)` / `fmc_word_program` | R4 R5 R7 R11 | 全中 |

### 四、框架层（Arduino / ESP8266）验证

框架层是早先完全漏掉的维度——**同一颗 ESP32，Arduino 写法与 ESP-IDF 写法命名词汇毫无重叠**。
同样用"自写故意写坏的样本"去撞（两份草图各自端到端跑引擎）：

| 样本 | 修复前 | 修复后 |
|---|---|---|
| 坏·Arduino-ESP32 HTTP OTA（`Update.begin/write/end` 返回值全不查、`ESP.wdtDisable()` 关了不管、无回滚、写完直接 `ESP.restart()`） | **99 分**，仅 1 条低危 | **82 分**，命中 R8 R9 R10 R11 R13 R15 |
| 好·同场景成熟写法（返回值必查 + `millis()` 超时护栏 + `Update.rollBack()` + `Preferences` 启动计数） | 100 分 | **96 分**（仅 R9——该草图**确实**没做防降级版本比较，属实） |
| 纯 `ArduinoOTA` 草图（`setup` 里 `begin`、`loop` 里 `handle`） | 100 分（**连 OTA 语境都判不出来，整套规则静默不触发**） | **99 分**（已正确判为 OTA 语境；仅 R12 无进度输出） |
| AVR（Uno）无 OTA 草图 | 100 分 | 100 分（**正确的不适用**：AVR 没有自升级代码） |

修复前那三个 99 / 100 / 100 正是这次要修的核心问题：**坏草图与好草图只差 1 分，等于没有鉴别力**。

**结论**：

- 成熟工程不会被误报刷屏（MCUboot / wolfBoot / Adafruit / ESP-IDF / Zephyr / mbed 全 100，或 97–98 的"待人工确认"）
- 官方 IAP 例程里的**真隐患被抓住**——ST 的 IAP 例子确实是「跳转三件套缺两件」，这不是误报，而是很多量产项目照抄它翻车的原因
- 仅有的"噪声"是跨文件分工产生的几条低危【需人工确认】，属可接受代价
- 纯自测不能算证据：首轮 102 项测试全绿时仍有 2 处真实误报；124 项全绿时，**跨平台召回其实是坏的**——`is_ota_ctx` 用了 `\b`，而真实代码里 `esp_ota_write` / `nrf_dfu_` 这类下划线前缀写法全都匹配不上，导致整套升级规则**静默不触发**（得出假的 100 分）。是这轮「拿四个平台的坏样本去撞」才逼出来的
- **同一个坑有第二个变体**：上一轮修的是"下划线前缀"（`esp_ota_write`），修完 140 项测试全绿，看起来干净了；但 **Arduino 侧其实完全没被覆盖**——`ArduinoOTA` 里 `OTA` 的前一字符是字母 `o`（**驼峰前缀**），同一套边界判定照样拒绝，纯 ArduinoOTA 草图连 OTA 语境都判不出来。**词边界不能只防一种形态**，这是拿 Arduino 坏样本去撞才现形的
- **框架层不是"架构层"的子集**：ESP-IDF 认得 ≠ Arduino 认得。命名族要按「架构 × 厂商 HAL × **框架层** × 语言风格（下划线/驼峰/点号）」多维切分，少一个维度就等于漏一块

## 镜像头格式（64 字节，小端）

| 偏移 | 类型 | 字段 | 说明 |
|---|---|---|---|
| 0 | u32 | magic | `0x50555746`（小端存储即 ASCII "FWUP"） |
| 4 | u16 | header_ver | 头格式版本，当前 1 |
| 6 | u16 | hw_id | 硬件标识，防串板 |
| 8 | u32 | fw_ver | `major<<16 \| minor<<8 \| patch` |
| 12 | u32 | load_addr | 镜像加载地址 |
| 16 | u32 | image_size | 镜像字节数 |
| 20 | u32 | image_crc | 镜像 CRC32 |
| 24 | u32 | header_crc | 头自身 CRC32（计算时该字段置 0） |
| 28 | u32 | timestamp | 打包 UTC 时间戳 |
| 32 | u32 | flags | bit0=强制升级 bit1=允许降级 |
| 36 | u8[28] | reserved | 保留，全 0 |

注意：MCU 侧解析**不要用 `sizeof(ota_image_header_t)`** 做长度校验（结构体对齐会变），用 `OTA_HEADER_SIZE`（64）。

## 输出

审计 JSON：`summary{high,medium,low,total}` + `issues[]{rule_id,severity,line,title,description,suggestion}` + `notes[]{line,note}`（不计分的提示）+ `score`（100 起，高危-8/中危-4/低危-1）+ `signals`（文件级信号，便于二次开发）。`--dir` 模式额外含 `top5_files` 与整体 `score`；`--html` 时 JSON 中 `html_report` 指向报告文件（报告里"提示"单独一块，不混进问题表）。

打包 JSON：`package/package_size/image/image_size/load_addr/fw_version/hw_id/image_crc32`。

## 可靠性与已知边界

- **190 项测试断言**（145 审计 + 45 工具，tests/）全部通过，每条规则配正反例；含「写法规范的 bootloader 应零命中」的防误报底线测试，以及从真实开源代码暴露的写法形态固化成的回归用例（向量表初始化不算跳转、HAL 函数定义不报 R11、宏里的 flash 写不报 R11、菜单/LED 反馈算进度输出、跨文件降级正反例、**Nordic/ESP-IDF/RISC-V/GD32 四个平台的召回用例**、**Arduino/ESP8266 框架层的 26 条用例**——含"坏草图必须比好草图低 10 分以上"的鉴别力断言）
- **去噪**：块注释/行注释/字符串字面量内的代码不计入信号（`// jump_to_app()` 不会误触发）；`asm volatile("mov pc, …")` 这类内联汇编里的跳转**单独抽取识别**，不会被去噪误杀
- 已知边界（有意取舍）：本包是**静态文本分析**，不做数据流/控制流分析——「校验在别的文件里做」「分区状态由 partition 模块管」这类跨文件分工，会在本文件报出**低危待人工确认**（不再直接按高危断言）；规则 5 只认常量擦除地址，宏地址不判；规则 7 每文件只报一次（避免刷屏）；跳转写在纯汇编文件（`.s`/`.asm`）时不扫
- **门控范围**：规则 1–3 仅在检测到跳转迹象时判定；规则 4、6、8–15 均以「OTA 语境（`ota` / `iap` / `dfu` / `firmware` / `upgrade` / `bootloader` 关键字，允许下划线前缀与驼峰前缀；或跳转迹象）」为门控，普通业务代码不触发（例如非升级代码里的 `HAL_Delay`、普通参数存储里的 `flash_write` 都不会被报成升级隐患）；**规则 5（擦除未对齐）与规则 7（裸 flash 地址）属于通用 flash 卫生检查，凡出现即报，不限于升级代码**——但 R7 只认 `0x08xxxxxx` 系地址
- **平台边界**：架构级规则（R1–R3、R8、R9、R12）跨 Cortex-M 全家族与 RISC-V；外设级规则的信号覆盖 ST HAL/SPL、GD32 FMC、Nordic nrfx、ESP-IDF、Zephyr/MCUboot、Arduino/ESP8266 与通用命名。遇到未覆盖的平台 API 命名时规则会**静默不触发**，请核对 JSON 的 `signals` 字段（详见「平台适用性」）
- **框架层边界（照实写）**：Arduino 的擦除/校验在 `Update` 库内部，sketch 里看不见——R14 改出不计分提示，R4 以 `Update.end(true)` 为库内校验证据；AVR（Uno/Nano/Mega）无自升级代码，**天然不适用**，得 100 分是"没有可审计对象"而非"代码安全"
- 不替代上板实测与硬件在环（HIL）验证；升级链路正确性最终以真板打断电、断连、错包三类故障的实测为准

## 文件结构

```
embedded-ota-toolkit/
├── SKILL.md
├── ota_audit.py            # 审计引擎（15 条规则 + 提示 + HTML 报告）
├── ota_tool.py             # 工具集（crc/layout/pack/verify）
├── references/
│   ├── CHANGELOG.md
│   └── ota-checklist.md    # 人工自检清单（上板前过一遍）
└── tests/
    ├── test_ota_audit.py
    └── test_ota_tool.py
```
