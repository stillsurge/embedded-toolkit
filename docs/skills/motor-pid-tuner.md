# 电机PID调参器（motor-pid-tuner）

**作用**：给电机参数和期望带宽，算出 FOC 三环 PI/PID 参数，并给调参诊断。

当前版本 **1.1.1**：29 个工作模式 + 独立报告生成器。

## 29 个模式（`--mode`）

| 分类 | 模式 |
|---|---|
| 核心计算 | `current` 电流环、`speed` 速度环、`position` 位置环、`zn` Ziegler-Nichols、`all` 三环+Q格式+前馈 |
| 诊断 | `diagnose` 5 种症状诊断 |
| 定点化 | `qformat` Q 格式（对标 MCSDK） |
| 前馈 | `feedforward` |
| 代码生成 | `code` 单环/完整 C 代码、`svpwm` 七段式 SVPWM、`platform` STM32/GD32/C2000 |
| 仿真 | `simulate` 阶跃响应 |
| 分析 | `sensitivity` 灵敏度、`discretize` 离散化对比、`stability` 相位/幅值裕度 + Bode |
| 高级 | `fieldweak` 弱磁、`observer` SMO/龙伯格增益 |
| 便捷 | `preset` 电机参数库、`suggest-bw` 自动带宽 |
| 导出 | `export` MATLAB 格式 |
| 交互 | `interactive` 引导式收集参数 |
| 反算 | `reverse` Kp/Ki → 带宽/阻尼 |
| 量产 | `antiwindup` 抗饱和、`deadtime-comp` 死区补偿、`multirate` 多采样率、`protection` 保护阈值、`tempcomp` 温漂补偿 |
| 校验 | `validate` 物理合理性校验 |
| 无感 | `startup` I/F + 高频注入 |

`svpmw` 为历史拼写，保留兼容，等价于 `svpwm`。

## 报告

一键调参报告用独立脚本（不是 `--mode`）：

```bash
python report_gen.py --format html    # 单文件 HTML：SVG 阶跃响应、三环参数卡、保护阈值、校验结果
```

## 用法示例

```bash
python main.py --mode current --rs 0.5 --ls 0.002 --bw 1000 --ts 0.0001
python main.py --mode all --rs 0.5 --ls 0.002 --j 0.0001 --kt 0.05 --vbus 24 --pole-pairs 7
```

## 边界

输出是**理论计算与整定建议**，上机必须按实测微调。不覆盖：电机本体设计、逆变器硬件选型、无感观测器的实机标定。
