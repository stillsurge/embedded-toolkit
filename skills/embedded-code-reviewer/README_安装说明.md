# 嵌入式代码审查器（1.1.0）

**一段代码喂进来，30 秒告诉你它会不会在现场死机。** 27 条规则静态审查嵌入式 C/C++ 代码——ISR 里调阻塞函数、共享变量缺 volatile（含数组元素）、数组越界与循环 off-by-one、除零、memcpy 长度超限、整数溢出、寄存器硬编码、裸 int 位域、宏副作用、C++ 裸 new、FreeRTOS/RT-Thread 中断上下文违规——按高危/中危/低危分级，每条附 MISRA C:2012 / MISRA C++:2008 编号引用与修复建议，`--html` 一键生成可分享的中文审查报告（自带 MISRA 覆盖声明）。

## 它解决什么问题

| 你遇到的 | 它帮你抓的 |
|----------|-----------|
| 板子随机死机/hardfault，编译器零警告 | ISR 中调 HAL_Delay/printf/vTaskDelay/rt_thread_mdelay（规则 1/16/22） |
| 开优化后主循环"读不到"中断更新的变量 | 中断↔主循环共享变量缺 volatile，覆盖 =/++/--/复合赋值（规则 2） |
| 偶发踩内存 | 数组越界、裸 int 位域符号性实现定义（规则 3/20） |
| C++ 工程里裸 new 禁异常环境下失败即致命 | .cpp 文件裸 new 检测，placement/nothrow 豁免（规则 23） |
| 过 MISRA/功能安全审查没工具 | 每条问题带 MISRA 编号引用（IAR C-STAT/Klocwork/Parasoft 多源核实） |
| 接手陌生工程不知道哪最烂 | --dir 批量扫描（.c/.h/.cpp/.hpp 全识别）+ HTML 报告 |
| memcpy 长度手滑写大，踩坏隔壁变量 | 长度实参超过目标数组大小（规则 26，sizeof(更大数组) 同抓） |
| 形参数组 memset 清不干净 | 数组形参 sizeof 得到指针大小 4/8（规则 27，C99 6.7.5.3） |

## 为什么可信

- **真实语料校准**：170,991 个手写嵌入式文件的全量池、抽样 400 实测 0 扫描错误；多轮误报治理（递归误报率 97%→0、假 ISR 根除、厂商库宏豁免、R7.2 口径两轮校准）全程有数据
- **120 项测试断言**全绿，每条规则有正反例
- **判据可溯源**：FreeRTOS/RT-Thread 检测逐条对照官方文档与内核源码（RT-Thread 判据双源核实于 2026-09-15）

## 30 秒上手（命令行，不需要 AI）

```bash
python reviewer.py motor_isr.c              # 单文件审查
python reviewer.py motor.cpp                # C++ 文件（轻量支持）
python reviewer.py --dir ./src              # 整个目录批量
python reviewer.py --dir ./src all --html report.html   # 生成 HTML 报告
```

发现问题 exit code = 1，可直接挂 CI。

## 作为 Agent Skill 使用

> 这是一个跨平台的 **Agent Skill（智能体技能）包**。把它装进任意支持 Agent Skills 标准的 AI 助手（Claude Code、扣子 Coze、Cursor 等），AI 就能在对话中自动调用。

### 安装

- **扣子 Coze**：技能 → 上传技能 → 选本 zip → 发布
- **Claude Code / Cursor**：解压放进 skills 目录（`~/.claude/skills/` 等），重启会话
- **其它平台**：识别到 `SKILL.md` 即自动加载

装好后直接说人话：「帮我审查这段中断处理代码有没有问题」。

### 包结构

- `SKILL.md` —— 技能说明书（AI 按需读取，约 110 行，上下文负担小）
- `reviewer.py` —— 审查引擎，纯 Python 3 标准库，不联网、不耗 AI 额度
- `references/` —— MISRA 映射表、更新记录（细节按需加载，不占对话上下文）
- `tests/test_reviewer.py` —— 135 项断言测试套件

## 兼容性

纯 Python 3.8+（实测 3.13），Windows/macOS/Linux 通用，无第三方依赖。

---
*本技能包可自由分发。AI 生成结果请人工复核后再用于生产。*
