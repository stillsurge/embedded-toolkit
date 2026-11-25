---
name: motor-pid-tuner
description: 输入电机参数，算出FOC电流环/速度环/位置环PI参数并给调参诊断：震荡、超调、稳态误差怎么破，29种模式含参数辨识、阶跃仿真、稳定性裕度、保护阈值，支持STM32/GD32/C2000代码生成。
license: MIT
compatibility: Python 3.10+，仅标准库，离线运行；不联网、不执行用户代码。
metadata:
  author: fangcun
  version: "1.1.1"
  display_name: 电机PID调参器
  display_name_en: Motor PID Tuner
  examples_zh:
  - 帮我算电流环 PI 参数，Rs=0.5Ω Ls=2mH 开关 20kHz
  - 电机转起来抖动是什么原因
  - 速度环响应太慢怎么调
---
# 电机PID调参器 1.1.0

> **更新**：新增「30 秒上手」——从内置电机参数库到三环一键计算的实测命令路径，新用户不用再啃 29 种模式表。

> **更新**：`report_gen.py --format html` 落地——单文件 HTML 调参报告（内嵌 SVG 阶跃响应仿真曲线、三环参数卡、保护阈值表、校验结果分色），可直接分享/存档。

> **更新**：异常兜底消息全中文化并附自助排查提示（`python main.py <模式名> --help`）；frontmatter 补 version 字段对齐三包口径。
>
> **更新**：修复 validate 模式参数不全时的误导性警告，补充位置环数字域 Kd 说明。

## 什么场景该用它

- **拿到电机参数不知道 PID 怎么起**：给 Rs/Ls/J/Kt，按期望带宽直接算出三环 PI/PID（连续域+数字域+Q 格式），不用翻公式
- **调参时震荡/超调/稳态误差**：描述现象，给出诊断与对策（Kp/Ki 朝哪调、要不要加 anti-windup）
- **要出一份能发群里的调参报告**：`--format html` 一键生成可视化报告，参数+曲线+保护阈值+建议一页带走
- **量产前的防护与校验**：过流/过压/过温/堵转阈值、参数合理性 sanity check、温升灵敏度

基于电机物理参数和期望带宽，自动计算FOC三环（电流环/速度环/位置环）PI/PID参数。支持29种工作模式（main.py），外加独立报告生成器（report_gen.py），覆盖从参数计算到代码生成、量产防护到无感启动的完整工作流。v6新增一键调参报告生成。

> **调用方式**：`python main.py --mode <mode> [参数...]`，模式名为 `current`/`speed`/`position` 等（不是 `current_loop`）。报告生成用独立脚本 `python report_gen.py`。

## 30 秒上手

不知道参数从哪来？先用内置参数库，再一键计算（以下命令均实测可跑）：

```bash
# 1) 看内置的 10 款常用电机参数（2207/2804/5010/6354/8318 等）
python main.py --mode preset

# 2) 取一颗具体电机的完整参数（自动推算 psi_f / J）
python main.py --mode preset --preset-name 2207-1500KV

# 3) 三环一把算：把上一步的参数喂进去（--bw 是电流环带宽，速度/位置环自动按 10:1:0.1 折算）
python main.py --mode all --rs 0.052 --ls 0.0000085 --j 0.001 --kt 0.0065 --psi-f 0.00061905 --pole-pairs 7 --bw 1000 --vbus 12 --imax 20
```

第 3 步输出：三环 Kp/Ki/Kd（连续域+数字域）、带宽比检查、Q 格式 C 宏、前馈系数。只需要电流环的话更简单：`python main.py --mode current --rs 0.052 --ls 0.0000085 --bw 1000`，三个参数就够。

## 工作流程

### 1. 识别用户需求

用户可能的表达方式：
- "帮我算电流环PI参数" / "速度环怎么调" / "位置环PD"
- "电机参数Rs=0.5 Ls=2mH，带宽1kHz"
- "电机一直震荡怎么办" / "超调太大"
- "Ziegler-Nichols调参" / "临界增益法"
- "生成PID代码" / "STM32 PID代码" / "完整FOC代码"
- "Q格式定点化" / "对标MCSDK"
- "前馈补偿" / "交叉耦合解耦"
- "仿真一下阶跃响应" / "看看波形"
- "Rs温升30%对参数影响多大" / "灵敏度分析"
- "前向欧拉和梯形法对比" / "离散化方法"
- "弱磁控制参数" / "高速区怎么算"
- "无感FOC观测器增益" / "SMO参数"
- "有没有常用电机参数库" / "2207电机参数"
- "PWM 20kHz带宽设多少" / "带宽建议"
- "导出MATLAB格式" / "Simulink验证"
- "SVPWM代码" / "七段式SVPWM"
- "抗积分饱和" / "anti-windup" / "积分器跑飞"
- "死区补偿" / "dead-time compensation" / "电压畸变"
- "多采样率" / "电流环和速度环不同频率" / "降采样"
- "相位裕度" / "幅值裕度" / "稳定性分析" / "Bode图"
- "参数校验" / "参数合不合理" / "sanity check"
- "过流保护" / "过温保护" / "堵转检测" / "I2t"
- "温度补偿" / "Rs温漂" / "磁钢温度系数"
- "无感启动" / "I/F启动" / "高频注入" / "零速启动"
- "GD32的PWM怎么配" / "TI C2000适配"
- "已知Kp=12.57 Ki=3141，反推带宽"
- "我不懂这些参数，引导我输入"

### 2. 交互式引导

当用户不确定需要哪些参数时，使用 `--mode interactive --target <loop>` 获取参数需求清单，然后逐个向用户询问。这比一次性要求所有参数更友好。

### 3. 收集参数

根据用户需求类型，收集必要参数。如果用户没给全，主动询问缺失的关键参数。也可以使用 `--mode preset` 查看常用电机参数库，或使用 `--mode suggest-bw --pwm-freq <kHz>` 自动推荐带宽。

**⚠️ CLI 参数名对照（调用前必读）**：下文的参数符号（Rs/Ls/J/Kt…）是物理量记号，`main.py` 实际 CLI 参数**一律全小写**。调用时以下表为准，禁止把大写记号直接当 CLI 参数传：

| 文档符号 | CLI 参数 | 单位 |
|---|---|---|
| Rs | `--rs` | Ω |
| Ls | `--ls` | H（mH 先换算成 H） |
| J | `--j` | kg·m² |
| B | `--b` | N·m·s/rad |
| Kt | `--kt` | N·m/A |
| 带宽 | `--bw` | Hz |
| 母线电压 | `--vbus` | V |
| 最大电流 | `--imax` | A |
| 磁链 ψf | `--psi-f` | Wb |
| 极对数 | `--pole-pairs` | 对 |
| 采样周期 | `--ts` | s |
| 阻尼比 | `--zeta` | — |

**all 模式带宽折算规则**：`--mode all` 时 `--bw` 给的是**电流环**带宽；速度环自动按 1/10、位置环按 1/100 折算（内置 10:1:0.1 带宽比），可用 `--speed-ratio` / `--pos-ratio` 覆盖默认比例。单独算速度环/位置环时直接给各自带宽（速度环典型 50-200Hz）。

**电流环PI计算需要：**
- Rs：定子电阻（Ω）
- Ls：定子电感（H），注意单位换算（mH→H）
- 带宽：期望电流环带宽（Hz），典型值500-2000Hz

**速度环PI计算需要：**
- J：转动惯量（kg·m²）
- B：摩擦系数（N·m·s/rad），未知时可设0
- Kt：转矩常数（N·m/A）
- 带宽：期望速度环带宽（Hz），典型值50-200Hz
- zeta：阻尼比（默认0.707，临界阻尼用1.0）

**位置环PD/PID计算需要：**
- J、Kt（同上）
- 带宽：期望位置环带宽（Hz），典型值10-50Hz
- zeta：阻尼比（默认0.707）

**Ziegler-Nichols法需要：**
- Kc：临界增益（系统开始等幅振荡时的Kp值）
- Tc：振荡周期（秒）
- 控制器类型：P / PI / PID

**调参诊断需要：**
- 用户描述症状（震荡/超调/响应慢/稳态误差/噪声大等）
- 当前参数值（如有）

### 4. 调用计算脚本

收集完参数后，调用 `main.py` 执行计算。根据用户需求选择对应功能模块：

```bash
python main.py --mode <mode> [参数...]
```

**mode 取值（29种）：**

| 分类 | mode | 功能 |
|------|------|------|
| 核心计算 | `current` | 电流环PI计算 |
| 核心计算 | `speed` | 速度环PI计算 |
| 核心计算 | `position` | 位置环PID计算 |
| 核心计算 | `zn` | Ziegler-Nichols法 |
| 核心计算 | `all` | 三环完整计算+Q格式+前馈 |
| 诊断 | `diagnose` | 调参诊断（5种症状） |
| 定点化 | `qformat` | Q格式定点化（对标MCSDK） |
| 前馈 | `feedforward` | 前馈补偿参数 |
| 代码生成 | `code` | 单环/完整C代码生成 |
| 仿真 | `simulate` | 阶跃响应仿真 |
| 分析 | `sensitivity` | 参数灵敏度分析 |
| 分析 | `discretize` | 多种离散化方法对比 |
| 高级 | `fieldweak` | 弱磁控制参数计算 |
| 高级 | `observer` | 观测器增益（SMO/龙伯格） |
| 便捷 | `preset` | 常用电机参数库 |
| 便捷 | `suggest-bw` | 自动带宽建议 |
| 导出 | `export` | MATLAB格式导出 |
| 代码 | `svpwm` | 完整七段式SVPWM代码 |
| 代码 | `platform` | 多平台适配（STM32/GD32/C2000） |
| 交互 | `interactive` | 交互式参数引导 |
| 反算 | `reverse` | 参数反算（Kp/Ki→带宽/阻尼） |
| **量产** | `antiwindup` | 抗积分饱和策略（Clamping/反算/跟踪） |
| **量产** | `deadtime-comp` | 死区补偿参数与代码 |
| **量产** | `multirate` | 多采样率控制指导 |
| **分析** | `stability` | 稳定性裕度（相位裕度/幅值裕度/Bode数据） |
| **校验** | `validate` | 参数物理合理性校验 |
| **量产** | `protection` | 故障保护阈值（过流/过压/过温/堵转/I2t） |
| **量产** | `tempcomp` | 温度补偿（Rs/磁链温漂+代码） |
| **无感** | `startup` | 无感启动策略（I/F+高频注入） |
| **报告** | `report_gen.py`（独立脚本，非 --mode） | 一键生成完整调参报告(Markdown) |

**各模式参数说明：**

核心计算模式（current/speed/position/all）：
- `--rs`, `--ls`, `--j`, `--b`, `--kt`, `--bw`, `--zeta`, `--ts`
- `--vbus`, `--imax`, `--psi-f`, `--pole-pairs`（all模式）
- `--rshunt`, `--aop`, `--vref`（可选，推算imax）

仿真模式（simulate）：
- `--loop`（current/speed/position）, `--kp`, `--ki`, `--kd`
- `--rs`, `--ls`（current）, `--j`, `--b`, `--kt`（speed）
- `--ts`, `--steps`（默认2000）, `--ref`（默认1.0）, `--output-limit`

灵敏度分析（sensitivity）：
- `--loop`（默认current）, `--rs`, `--ls`, `--j`, `--kt`, `--b`, `--bw`, `--zeta`
- `--variation`（默认30，百分比）

离散化方法（discretize）：
- `--kp`, `--ki`, `--kd`, `--ts`, `--method`（forward/backward/tustin/all）

弱磁控制（fieldweak）：
- `--psi-f`, `--ls`, `--vbus`, `--pole-pairs`, `--rated-speed`, `--max-speed`

观测器增益（observer）：
- `--rs`, `--ls`, `--psi-f`, `--pole-pairs`, `--bw`（电流环带宽）
- `--observer-type`（smo/luenberger/all）, `--max-speed`（SMO用）

电机参数库（preset）：
- `--preset-name`（可选，指定型号；不指定则列出全部）

带宽建议（suggest-bw）：
- `--pwm-freq`（kHz）, `--rs`, `--ls`（可选）

MATLAB导出（export）：
- `--loop`, `--kp`, `--ki`, `--kd`, `--rs`, `--ls`, `--j`, `--b`, `--kt`
- `--format`（默认matlab）

SVPWM代码（svpwm）：
- `--vbus`, `--deadtime`（默认500ns）

多平台适配（platform）：
- `--platform-choice`（stm32/gd32/c2000）, `--pwm-freq`, `--vbus`, `--imax`

交互式引导（interactive）：
- `--target`（current/speed/position/all）

参数反算（reverse）：
- `--kp`, `--ki`, `--kd`, `--loop`（current/speed/position）
- `--rs`, `--ls`（current）, `--j`, `--b`, `--kt`（speed/position）
- `--no-speed-loop`（位置环单环模式）

抗积分饱和（antiwindup）：
- `--loop`（current/speed/position）, `--kp`, `--ki`, `--output-limit`
- `--aw-method`（clamping/backcalc/trackback/all, 默认all）, `--ts`

死区补偿（deadtime-comp）：
- `--vbus`, `--pwm-freq`（kHz）, `--deadtime`（ns, 默认500）
- `--rated-current`（可选, 计算THD）

多采样率（multirate）：
- `--pwm-freq`（kHz）, `--bw`（电流环带宽Hz）
- `--speed-ratio`（默认10）, `--pos-ratio`（默认10）

稳定性分析（stability）：
- `--loop`（current/speed/position）, `--kp`, `--ki`, `--kd`, `--ts`
- `--rs`, `--ls`（current）, `--j`, `--b`, `--kt`（speed/position）
- `--no-speed-loop`（位置环单环模式）

参数校验（validate）：
- `--rs`, `--ls`, `--psi-f`, `--j`, `--kt`, `--b`, `--pole-pairs`
- `--ts`, `--bw`, `--pwm-freq`（均可选, 传入的参数才会校验）
- `--psi-f` 未提供时跳过 Kt 与 1.5·ψf·极对数 一致性检查（仅保留范围校验error）；显式传0时行为不变

故障保护（protection）：
- `--rated-current`（A）, `--vbus`, `--device-type`（IGBT/MOSFET, 默认MOSFET）

温度补偿（tempcomp）：
- `--rs`, `--ls`, `--psi-f`, `--bw`, `--pole-pairs`
- `--temp-min`（默认25）, `--temp-max`（默认125）, `--temp-points`（默认5）
- `--magnet-type`（NdFeB/SmCo/Ferrite, 默认NdFeB）

无感启动（startup）：
- `--rs`, `--ls`, `--psi-f`, `--pole-pairs`, `--vbus`
- `--rated-speed`, `--pwm-freq`, `--rated-current`
- `--startup-method`（if/hfi/all, 默认all）, `--transition-speed`（rpm, 默认5%额定）

一键调参报告（report）：
- 通过 `python report_gen.py` 调用（独立脚本）
- 参数：`--rs --ls(mH) --j --kt [--b --psi-f --pole-pairs --vbus --imax --pwm-freq --bw-current --zeta --ts --motor-model --platform]`
- 选项：`--no-position`（不含位置环）、`--no-protection`（不含保护）、`--with-stability`（含稳定性分析）、`-o/--output <文件>`（保存到文件，不加则打印到stdout）
- 输出：完整Markdown调参报告，含电机参数表、三环PI参数（连续域+数字域）、带宽比检查、Q格式C宏、前馈系数、参数校验、保护阈值、调参建议
- 用 `-o report.md` 保存后可发给客户或归档
- ⚠️ **单位注意**：`report_gen.py` 的 `--ls` 输入单位是 **mH**（内部自动转H）；而 `main.py` 的 `--ls` 输入单位是 **H**（如1.5mH需写 `--ls 0.0015`）。
- ⚠️ 章节编号为动态生成，若未提供 `--psi-f` 则无前馈章节，编号自动连续。

脚本输出结构化JSON，解析后向用户展示。

### 5. 展示结果

结果展示要点：
- 列出计算得到的Kp/Ki/Kd值，标注物理单位
- 显示计算所用的公式和推导过程（简要）
- 给出带宽比检查结果（内环应为外环5-10倍）
- 提供调参建议（从理论值出发的微调方向）
- 仿真模式：展示时域指标（上升时间、超调、 settling time）
- 灵敏度分析：展示参数变化对Kp/Ki的影响百分比和敏感度评级
- 如用户需要，生成C代码

### 6. 补充说明

**带宽选择经验：**
- 电流环带宽 < PWM频率/10
- 速度环带宽 = 电流环带宽 / 5~10
- 位置环带宽 = 速度环带宽 / 5~10
- 可用 `--mode suggest-bw` 自动推荐

**理论值与实际值的差距来源：**
- 温升导致Rs变化（+30-50%）→ 可用 `--mode sensitivity` 量化分析
- 磁饱和导致Ls下降
- 采样延迟和计算延迟
- 量化误差和噪声
- 建议从理论值的70%开始，逐步增大

**离散化提醒：**
- 连续域Ki需乘以采样周期Ts才是数字域Ki
- 可用 `--mode discretize --method all` 对比三种离散化方法
- Tustin（梯形法）精度最高但计算量略大
- 位置环数字域Kd = Kd_continuous / Ts，数值较大属正常现象（如Kd=8882.64、Ts=50μs时约1.78e6）；定点化实现时建议先对Kd缩放（如按2^-n移位）或直接使用浮点运算，避免Q格式溢出

**Q格式定点化说明：**
对标ST MCSDK的定点化方案，将物理域PI参数转为int16+DIV格式：
1. 标幺化：Kp_pu = Kp × Imax / Vmax（Vmax = Vbus/√3）
2. 离散化：Ki_d = Ki_pu × Ts
3. Q编码：value = raw / DIV，DIV自动选最大2的幂使raw ∈ [-32767, 32767]
4. 输出C宏：PID_KP_DEFAULT / PID_KPDIV / PID_KPDIV_LOG（直接对标MCSDK）

**前馈补偿说明：**
dq轴电压方程存在交叉耦合和反电动势项，PI控制器无法直接处理：
- Vd_ff = -ωe × Ls × Iq（d轴交叉耦合）
- Vq_ff = +ωe × Ls × Id + ωe × ψf（q轴交叉耦合+反电动势）

**弱磁控制说明：**
当电机转速超过基速时，反电动势接近母线电压极限，需要注入负Id来削弱有效磁通：
- 基速：n_base = Vmax / (ψf × 2π × 极对数) × 60
- 弱磁Id：Id_fw = (Vmax/ωe - ψf) / Ls（当ωe > ωbase时）
- 退磁极限：Id_fw_max = -ψf / Ls（永磁体不可逆退磁风险）

**观测器增益说明：**
- SMO：滑模增益K_smo需大于反电动势最大值，低通滤波引入相位延迟需补偿
- Luenberger：全阶观测器极点配置在电流环带宽2-5倍处

**完整代码生成（code --full）：**
生成motor_controller.h + motor_controller.c，包含：
- 电流环PI（d/q双轴）+ 前馈补偿接口
- 速度环PI
- 位置环PD（可选）
- 抗积分饱和（clamping）
- 初始化函数 + FOC中断服务函数模板

**SVPWM代码生成（svpwm）：**
生成完整七段式SVPWM C函数，包含扇区判断、T1/T2计算、比较值生成、死区处理

**多平台适配（platform）：**
- STM32：TIM1中心对齐PWM + ADC注入通道
- GD32：TIMER0 PWM + ADC规则组（寄存器映射差异）
- TI C2000：ePWM(AQ+TB模块) + ADC SOC触发

**电机参数库（preset）：**
预置10款常用BLDC/PMSM电机参数（2207/2804/5010/6354/8318等），选型号自动填充Rs/Ls/Kt/极对数

## 输出格式示例

```
📊 电流环PI参数计算结果
━━━━━━━━━━━━━━━━━━━━━
电机参数：
  Rs = 0.5 Ω
  Ls = 2.0 mH
  期望带宽 = 1000 Hz (ωc = 6283 rad/s)

PI参数（连续域）：
  Kp = Ls × ωc = 2e-3 × 6283 = 12.57 V/A
  Ki = Rs × ωc = 0.5 × 6283 = 3141.6 V/(A·s)

PI参数（数字域，Ts=50μs）：
  Kp = 12.57
  Ki = 3141.6 × 50e-6 = 0.157

带宽检查：✓ 电流环带宽合理
调参建议：从Kp=8.8（70%）开始，观察电流阶跃响应
```
