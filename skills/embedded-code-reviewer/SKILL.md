---
name: embedded-code-reviewer
description: 一段嵌入式C/C++代码喂进来，30秒揪出会让板子死机的雷：ISR里调延时函数、共享变量缺volatile、数组越界、除零、memcpy超限等28条规则，逐条附MISRA C:2012/C++:2008映射与修复建议，一键生成中文HTML审查报告，支持CI门禁。
license: MIT
compatibility: Python 3.10+，仅标准库，离线运行；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.1.1"
  display_name: 嵌入式C/C++代码审查器
  display_name_en: Embedded C/C++ Code Reviewer
  examples_zh:
  - 帮我审查这段中断处理代码
  - 这个变量要不要加 volatile
  - 代码能不能过 MISRA 检查
---
# 嵌入式代码审查

给嵌入式 C 代码做"体检"：不用编译、不用装工具链，喂一段代码进来，按高危/中危/低危分级输出问题清单，每条带位置、原因、修复建议和 MISRA C:2012 规则编号引用。

## 什么场景该用它

- **中断里埋雷**：ISR 里调 `HAL_Delay`/`printf`/`vTaskDelay`，现场就是随机死机、-hardfault，编译器一个警告都不给——规则 1/7/16/22 专抓这类
- **抢不出来的玄学 bug**：中断和主循环共享的变量忘加 `volatile`，开优化后主循环永远读不到新值——规则 2 覆盖 =/++/--/复合赋值全部写法
- **过 MISRA/功能安全审查**：每条问题附 MISRA C:2012 编号引用（经 IAR C-STAT/Klocwork/Parasoft 多源核实，无杜撰编号）
- **接手陌生工程**：`--dir` 批量扫描整个目录，HTML 报告一图看懂哪里最烂

## 30 秒看效果

喂入一段真实风格的定时器中断代码：

```c
volatile uint32_t g_adc_raw;
uint8_t g_frame_ready;
void TIM1_IRQHandler(void) {
    HAL_Delay(5);                       // ← 想等 ADC 稳定
    g_adc_raw = ADC1->DR;
    g_frame_ready++;                    // ← 主循环会读它
    uint8_t buf[4];
    buf[5] = 1;                         // ← 手滑
    int total = g_adc_raw * 4096;
    switch (g_frame_ready) { case 1: break; }
    vTaskDelay(10);
}
```

审查输出（**评分 66/100**，4 高危 2 低危）：

| 规则 | 级别 | 位置 | 问题 | MISRA |
|------|------|------|------|-------|
| R2 | 🔴 高危 | L2 | 中断共享变量 `g_frame_ready` 未加 volatile（`g_adc_raw` 已有则豁免） | — |
| R1 | 🔴 高危 | L4 | ISR 中使用阻塞函数 HAL_Delay——中断里卡 5ms，全系统中断延迟被拖死 | — |
| R3 | 🔴 高危 | L8 | 数组 `buf` 索引 5 越界（声明大小 4），踩坏栈上相邻内存 | R18.1, R1.3 |
| R16 | 🔴 高危 | L11 | ISR 中调用 FreeRTOS 阻塞 API vTaskDelay（应改用 FromISR 变体） | — |
| R12 | 🟢 低危 | L9 | 变量 total 定义后未使用 | — |
| R15 | 🟢 低危 | L10 | switch 缺少 default 分支 | R16.4 |

## 快速上手

**Agent 调用**（本 skill 场景）：提供 `file_path`（文件）、`dir`（目录递归）或 `code`（粘贴代码）任一，可选 `rules: all/high/medium/low`。

**命令行**：

```bash
python reviewer.py main.c                    # 单文件全规则
python reviewer.py main.cpp                  # C++ 文件（轻量支持，含裸 new 检测）
python reviewer.py main.c high               # 只看高危
python reviewer.py --dir ./src               # 整个目录（.c/.h/.cpp/.hpp 全识别）
python reviewer.py --dir ./src all --html report.html   # 目录 + HTML 报告
```

exit code：0=无问题、1=发现问题、2=用法/内部错误（CI 集成友好）。

## 检测规则速查（28 条）

| # | 级别 | 规则 | 一句话 |
|---|------|------|--------|
| 1 | 🔴 | ISR阻塞调用 | ISR 里调 HAL_Delay/printf/malloc/free |
| 2 | 🔴 | 共享变量缺 volatile | 中断↔主循环共享变量，覆盖全部写法，含数组元素 |
| 3 | 🔴 | 数组越界 | 变量索引无边界检查、循环 `i<=N` off-by-one（识别循环头豁免） |
| 4 | 🔴 | 硬编码寄存器值 | 裸数字直写寄存器（#define 封装豁免） |
| 16 | 🔴 | FreeRTOS API in ISR | 调任务级 API（FromISR 变体不报） |
| 19 | 🔴 | 寄存器指针解引用 | `*(volatile uint32_t*)0x40000000` |
| 22 | 🔴/🟢 | RT-Thread API in ISR | 挂起类/内存类/对象创建类 high；timeout=0 试探型 low；release/send 合法不报 |
| 5 | 🟡 | 临界区未配对 | __disable_irq 后未开中断 |
| 6 | 🟡 | 整数溢出 | 乘法无范围检查（含 return 表达式） |
| 7 | 🟡 | ISR 中浮点运算 | 惰性压栈开销 |
| 8 | 🟡 | malloc 未判空 | 动态分配后不检查 NULL |
| 10 | 🟡 | 浮点 == 比较 | 应改范围判断 |
| 11 | 🟡 | sprintf 溢出风险 | 应改 snprintf |
| 17 | 🟡 | 大局部数组 | 局部数组累计 ≥512B 耗任务栈 |
| 18 | 🟡 | 递归函数 | 无 MMU 的 MCU 上栈溢出风险 |
| 20 | 🟡 | 裸 int 位域 | 符号性实现定义（C99 6.7.2.5） |
| 21 | 🟡 | 宏副作用 | `#define NEXT(n) ((n)++)` 类陷阱宏（豁免口径经语料校准） |
| 23 | 🟡 | C++ 裸 new | 非放置形态 `new`（禁异常环境致命），仅扫 .cpp/.hpp |
| 9 | 🟢 | 硬编码延时 | 主流程延时（ISR 内由 R1 覆盖） |
| 12 | 🟢 | 未使用变量/函数 | 定义后未引用 |
| 13 | 🟢 | 魔术数字 | 裸数字（下标/实参豁免） |
| 14 | 🟢 | 函数缺注释 | 非 static 函数（CubeMX 生成函数豁免） |
| 15 | 🟢 | switch 缺 default | — |
| 24 | 🟢 | 十六进制字面量缺 u/U 后缀 | ≥`0x80000000` 且参与运算（MISRA C:2012 R7.2 轻量口径） |
| 25 | 🔴 | 除数为零 | 除法/取模除数为常量 0（C11 6.5.5 未定义，Cortex-M 上 UsageFault/HardFault） |
| 26 | 🔴 | memcpy 长度超限 | memcpy/memset 等长度实参超过目标数组大小（sizeof(更大数组) 同抓） |
| 27 | 🟡 | 数组形参 sizeof | 形参数组被调整为指针，sizeof 得到 4/8（C99 6.7.5.3） |

完整 MISRA 映射表与编号核实说明见 `references/misra-mapping.md`；历史版本明细见 `references/CHANGELOG.md`。

## 输出

JSON：`summary{high,medium,low,total}` + `issues[]{rule_id,severity,line,title,description,suggestion,misra,misra_refs}` + 评分（100 分起，高危-8/中危-4/低危-1）。`--dir` 模式额外含 `top5_files` 与每文件明细；`--html` 时 JSON 中 `html_report` 字段指向生成的报告文件。

## 可靠性与已知边界

- **误报控制经真实语料校准**：2-IMU + 9-other 全量池 170,991 个手写嵌入式文件、seed 20260914 抽样 400 实测，0 扫描错误，各规则命中分布与验收线比对通过；历史误报治理明细（ISR 判定根除、HAL 驼峰回调、递归 97%→0 等）见 references/CHANGELOG.md 变更记录
- **120 项测试断言**（tests/test_reviewer.py）全部通过，含每条规则正反例与 MISRA 映射断言
- 已知残留（有意取舍，非缺陷）：规则 3 全小写枚举常量下标仍报；规则 21 不扫 #define 续行、CMSIS 无前缀寄存器宏残留个位数命中；规则 20 按缩量口径 stdint 位域不报
- 不替代编译器警告与专业静态分析工具（PC-lint/Coverity）；MISRA 映射供合规参考，正式合规请用正式工具复核
