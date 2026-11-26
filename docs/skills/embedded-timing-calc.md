# 嵌入式时序计算器（embedded-timing-calc）

**作用**：凡问"该填多少 / 是多少 / 选多大 / 误差多少"，一次算出结果，并回显公式与合法性依据。全部离线计算。

当前版本 **1.1.2**：37 个计算器。

## 计算器清单

### 串行通信（8）

| ID | 算什么 |
|---|---|
| `uart` | UART 波特率、BRR 值、实际波特率与误差判定（<2% 可用） |
| `serial-baud` | 常用波特率速查 |
| `spi` | SPI 分频 |
| `spi-time` | SPI 传输耗时 |
| `i2c-rp` | I2C 上拉电阻上下限与推荐值（std / fast / Fm+，`Rp_max=tr/(0.8473×Cb)`） |
| `i2c-time` | I2C 总线耗时 |
| `modbus-silence` | Modbus 帧间隔 |
| `can-bit` | CAN 位时序、TQ 段分配、采样点位置（检查 75–87.5%） |

### 定时与执行器（7）

| ID | 算什么 |
|---|---|
| `timer` | 定时器 PWM 的 PSC / ARR 互算与反推（多组推荐） |
| `deadtime` | 死区占比 |
| `pwm-dim` | PWM 调光位深 |
| `ws2812` | WS2812 位时序 |
| `servo` | 舵机脉宽 |
| `stepper` | 步进电机 |
| `wdg` | 看门狗超时 |

### 模拟与采样（8）

| ID | 算什么 |
|---|---|
| `adc-rad` | ADC 最大源阻抗 |
| `rc` | RC 截止频率 |
| `rc-settle` | RC 建立时间 |
| `nyquist` | 采样定理 |
| `divider` | 分压电阻 |
| `ntc` | NTC 换算 |
| `ppm` | 晶振 ppm 与累计误差 |
| `sensor-lsb` | 传感器分辨率换算 |

### 时钟与系统（7）

| ID | 算什么 |
|---|---|
| `pll` | PLL 参数 |
| `esp32-clk` | ESP32 外设时钟 |
| `rp2040-uart` | RP2040 UART 分频 |
| `usb-clk` | USB 48MHz 推导链 |
| `rtc-drift` | RTC 走时误差 |
| `battery` | 电池续航 |
| `flash-wear` | Flash 擦写寿命 |

### FPGA（7）

| ID | 算什么 |
|---|---|
| `fpga-uart` | UART 整数分频与误差 |
| `fpga-slack` | 静态时序 slack 与 Fmax |
| `fpga-pwm` | PWM 位深 |
| `fpga-i2c` | I2C 分频 |
| `fpga-debounce` | 消抖窗口 |
| `fpga-cdc` | CDC 检查单 |
| `fpga-fifo` | 异步 FIFO 溢出 |

用 `timing.py list` 查看当前全部 ID，`timing.py <id> --help` 查看单个参数。

## 已知不支持

- I2C Hs-mode：该模式为电流源上拉，本工具不支持，抛 `E_UNSUPPORTED`，需按 UM10204 Hs-mode 章节人工核对

## 输出

每条结果包含：结果值、公式回显、合法性判定、阈值出处。`--format json` 输出统一信封。

公式审查记录见 `benchmarks/review-timing-calc.md`。

## 边界

不用于：排障决策（用 `embedded-debug-trees`）、配置坑查询（用 `embedded-peripheral-pitfalls`）、寄存器事实（用 `embedded-register-lookup`）。
