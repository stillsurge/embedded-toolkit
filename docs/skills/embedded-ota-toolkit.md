# 嵌入式OTA升级工具包（embedded-ota-toolkit）

**作用**：在固件升级链路交付前，按 15 条防砖规则静态审计 IAP/OTA 代码，每条给可直接粘贴的修复写法。

当前版本 **1.2.0**：15 条规则 + CRC / 分区 / 镜像打包校验工具。

## 15 条防砖规则

| 级别 | 规则 |
|---|---|
| 高危 | 跳转未重定位 VTOR、跳转前未关中断、跳转前未校验 APP（栈顶落 SRAM、复位向量落 flash）、升级数据无完整性校验 |
| 中危 | 擦除地址未按页对齐、擦写期间未喂看门狗、分区地址硬编码、接收等待无超时、无防降级版本校验、升级状态未持久化、写入前未见擦除、关闭看门狗后未见恢复 |
| 低危 | flash 写未检查返回值、升级流程无进度输出、硬编码延时 |

判定取向是**宁漏勿误**：成熟工程与普通 flash 代码不误报，每条规则附判据与豁免口径。

## 配套工具

- CRC 计算
- 分区规划
- 镜像打包与校验（64 字节镜像头、小端）

## 平台

Cortex-M / RISC-V；对 Arduino、ESP8266 的框架层封装做过单独验证。

## 用法

```bash
python ota_audit.py <file.c>                  # 文本审计
python ota_audit.py --dir <目录>               # 批量
python ota_audit.py <file.c> --html r.html    # 中文 HTML 报告
python ota_audit.py <file.c> --fail-under 0   # CI 门禁
```

## 已知边界

- 静态分析，不做控制流求解；跨函数跳转只按调用点形态判定
- 汇编实现的 bootloader 不做语义审计
- 只审升级链路，不审应用功能

## 边界

不用于：Run-time 升级失败现场排障（用 `embedded-debug-trees` 的 flash / boot 树）、寄存器写入核验（用 `embedded-register-verify`）。
