# 嵌入式OTA/Bootloader工具包（1.2.0）

**两个工具，一件事：让固件升级别变砖。** 审计侧不编译、不接硬件，静态扫描你的升级代码，按高危/中危/低危报出 15 条防砖漏洞，每条附可直接粘贴的修复代码；工具侧算 CRC、规划分区、生成镜像头、打包校验升级包——从"检查"到"交付"一条链。

## 它解决什么问题

| 你遇到的 | 它帮你抓的 |
|----------|-----------|
| 自写 bootloader，跳 APP 后程序跑飞/卡死 | 跳转前未重定位 VTOR、未关中断、未校验 APP 有效性（三条高危，可一次全踩） |
| 升级到一半断电/拔线，设备变砖 | 写入前未擦除、升级状态未持久化、接收等待无超时 |
| 升级数据传输出错，刷进坏固件 | 升级数据无 CRC/哈希校验、flash 擦除地址未按页对齐 |
| 擦写 flash 时设备莫名复位 | 擦写期间未喂看门狗、关闭看门狗后未恢复 |
| 老版本漏洞固件被刷回来 | 无防降级版本校验 |
| 分区地址手算出错，一编译就冲突 | 分区表规划工具：给 Flash 大小和分区清单，输出地址表 + 带编译期溢出断言的 partition.h |
| 升级包不知道给哪块板 | 64 字节镜像头：magic/硬件ID/版本/CRC，防串板防错包 |

## 为什么可信

- **成熟工程零误报**：MCUboot / wolfBoot / Adafruit DFU / ESP-IDF / Zephyr 实测 100 分
- **官方例程的坑也能抓**：ST 官方 IAP 例程真隐患被抓住（跳转三件套缺两件，80 分）——量产项目照抄它翻车的常见原因
- **190 项测试断言**（145 审计 + 45 工具），含四平台召回验证与 Arduino 框架层 26 条用例
- **诚实标注覆盖范围**：架构级规则跨 Cortex-M 全家族与 RISC-V；外设级认 ST HAL、GD32 FMC、nrfx、ESP-IDF、Zephyr/MCUboot、Arduino/ESP8266 写法；识别不到的平台会明示，不硬报

## 快速上手

```bash
python ota_audit.py bootloader.c          # 单文件审计（评分 + 问题清单 + 修复代码）
python ota_audit.py --dir ./src --html report.html   # 目录批量 + HTML 报告

python ota_tool.py layout --flash 256K boot:32K app:96K app_bak:96K cfg:8K --out partition.h
python ota_tool.py pack app.bin --addr 0x08008000 --ver 1.2.3 --emit-header
python ota_tool.py verify app.pkg
```

审计发现问题 exit code = 1，可直接挂 CI 门禁。

## 作为 Agent Skill 使用

> 这是一个跨平台的 **Agent Skill（智能体技能）包**。把它装进任意支持 Agent Skills 标准的 AI 助手（Claude Code、扣子 Coze、Cursor 等），AI 就能在对话中自动调用。

### 安装

- **扣子 Coze**：技能 → 上传技能 → 选本 zip → 发布
- **Claude Code / Cursor**：解压放进 skills 目录（`~/.claude/skills/` 等），重启会话
- **其它平台**：识别到 `SKILL.md` 即自动加载

装好后直接说人话：「帮我看看这段 IAP 跳转代码会不会变砖」。

### 包结构

- `SKILL.md` —— 技能说明书（AI 按需读取，上下文负担小）
- `ota_audit.py` —— 审计引擎，纯 Python 3 标准库，不联网、不耗 AI 额度
- `ota_tool.py` —— 打包工具（CRC / 分区表 / 镜像头 / .pkg 打包校验）
- `references/` —— 更新记录、上板前自检清单（细节按需加载）

## 兼容性

纯 Python 3.8+（实测 3.13），Windows/macOS/Linux 通用，无第三方依赖。审计对象支持裸机 Cortex-M/RISC-V 与 Arduino/ESP8266 框架写法。

---
*本技能包可自由分发。AI 生成结果请人工复核后再用于生产。*
