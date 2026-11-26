# 嵌入式驱动模板库（embedded-driver-templates）

**作用**：移植常用驱动前先查这里，拿预验证过的源码、适配层、接线表和坑清单，别从论坛抄。

当前版本 **1.0.1**：9 款驱动，算法层纯 C99 平台无关，平台差异收在 port 层。

## 9 款驱动

| 驱动 | 接口特征 |
|---|---|
| DHT11 温湿度 | 单总线，时序敏感，另附 Arduino 写法 |
| DS18B20 | 单总线，ROM 搜索 / 多点 |
| HC-05 蓝牙 | UART + AT 命令，配对状态下部分 AT 不可用 |
| HC-SR04 超声 | 触发/回响双引脚，回响脉宽测距 |
| MPU6050 | I2C，初始化顺序与量程配置有硬要求 |
| SSD1306 OLED | I2C/SPI，显存分页 |
| SG90 舵机 | PWM 周期 20ms、脉宽 0.5–2.5ms |
| 28BYJ-48 步进 | 四相八拍，减速比 |
| ESP8266-AT | UART + AT，需 3 个 UART 函数适配 |

每款带：可编译源码（`.c/.h`）、port 适配层（`*_port.h`）、接线表（`wiring.md`）、元数据（`meta.json`，含验证记录）。

## 验证记录

- C 逻辑测试 107 项断言 0 失败（9 款合计）
- `gcc -Wall -Wextra` 逐款零警告（2026-10-27 实跑）
- 另有外设初始化顺序查询：问「这个外设初始化有什么硬要求」直接查

## 命令

```bash
python scripts/driver_templates.py list          # 9 款驱动一览（含验证记录）
python scripts/driver_templates.py get hc05      # 单款驱动全文
python scripts/driver_templates.py wiring mpu6050 # 接线与避坑
python scripts/driver_templates.py api           # 外设占用与初始化顺序总览
python scripts/driver_templates.py api-get mpu6050  # 单驱动初始化要求
```

`engine.py` 是库模块（数据与查询实现），不是 CLI 入口。

## 边界

模板是**移植参考**，不是即拷即用：换平台要自己写 port 层。不生成新驱动代码（用 `embedded-code-generator`），不做协议一致性判定与报文拆解。
