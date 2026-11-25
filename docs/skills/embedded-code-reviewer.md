# 嵌入式C/C++代码审查器（embedded-code-reviewer）

**作用**：把一段嵌入式 C/C++ 喂进来，按 27 条规则逐条报问题，附 MISRA 映射与修复建议。

当前版本 **1.1.2**：27 条规则，分高危 / 中危 / 低危。

## 规则分布

| 级别 | 条数 | 代表规则 |
|---|---|---|
| 高危 | 8 | ISR 里调阻塞函数、共享变量缺 volatile、数组越界与循环 off-by-one、硬编码寄存器值、FreeRTOS 任务级 API 进 ISR、寄存器指针解引用、除零、memcpy 长度超限 |
| 条件分级 | 1 | RT-Thread API 进 ISR：挂起/内存/对象创建类判高危，timeout=0 试探型判低危，release/send 合法不报 |
| 中危 | 12 | 临界区未配对、整数溢出、ISR 中浮点、malloc 未判空、浮点 == 比较、sprintf 溢出、大局部数组、递归、裸 int 位域、宏副作用、C++ 裸 new、数组形参 sizeof |
| 低危 | 6 | 硬编码延时、未使用变量/函数、魔术数字、函数缺注释、switch 缺 default、十六进制字面量缺 u 后缀 |

每条附 MISRA C:2012 / C++:2008 编号引用。设计取向是**宁漏勿误**：无法确定的写法标「未判定」而不是硬报。

## 用法

```bash
python reviewer.py <file.c>            # 文本输出
python reviewer.py --dir <目录>        # 批量
python reviewer.py <file.c> --html r.html   # 中文 HTML 报告
```

规则速查表见 `SKILL.md`，逐条含判据与豁免口径。

## 已知边界

- 纯静态、不做类型推导；跨文件符号不追踪
- 宏展开后语义无法确定的，按源码形态判定并标「未判定」
- 非标准扩展（`__attribute__`、内联汇编）不做语义分析

## 边界

不用于：寄存器写入与 SVD 的一致性核验（用 `embedded-register-verify`）、外设配置语义坑（用 `embedded-peripheral-pitfalls`）、编译告警替代（那是编译器的事）。
