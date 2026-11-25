# 外设避坑清单（embedded-peripheral-pitfalls）

**作用**：配置前对照已知坑，或用"配置看起来都对但就是不工作"时逐项排查。每坑 = 症状 + 对策。

当前版本 **1.2.1**：二十五类外设、148 个配置坑。

## 覆盖外设

`adc` `c` `can` `crc` `dac` `dbg` `dma` `eth` `exti` `flash` `gpio` `i2c` `link` `modbus` `mpu` `pwr` `rcc` `rtc` `sd` `sensor-bus` `spi` `tim` `uart` `usb` `wdg`

## 命令

- `search`：按外设 / 症状检索，中英文、同义词、中文整句反向匹配、bigram 兜底；`--category` 限定分类，`--format json`
- `show`：分类坑表
- `rule`：配置口诀——时钟 → GPIO → 外设 → 中断 → 使能

时序数值类坑带 `next` 字段，直接指到 `embedded-timing-calc`。

## 与核验器的分工

- `embedded-register-verify` 查寄存器写入**合法性**（位是否存在、值是否超宽）
- 本库查配置**语义陷阱**（顺序、模式、约束）

## 评测

- schema / 同源校验与检索评测同上，CI 强制
- 触发用例：35 正 + 14 反
- 触发实测：命中率 14.3%，反例零误触发。偏低主因同决策树（路由模型直接作答），详见 `benchmarks/trigger-results-trees.md`

## 边界

不用于：故障已发生要定位根因（用 `embedded-debug-trees`）、寄存器事实查询（用 `embedded-register-lookup`）。
