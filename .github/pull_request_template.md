## 改了什么

<!-- 一句话说明改动范围。若动了 skills/ 下任何文件，标题请写明技能名与版本，例如：
     feat: embedded-timing-calc 1.1.2——补 SPI 时钟极性组合表 -->

## 为什么

<!-- 触发这次改动的问题、实测数据或手册依据 -->

## 改动类型

- [ ] 只改治理文件（`docs/` / `README` / `CHANGELOG` / `.github/` / `tools/` / `release/`），不动技能内容
- [ ] 改了技能内容（必须走完发布流程，见 [docs/release-process.md](../docs/release-process.md)）

## 验证

- [ ] `python tools/sync_core.py`（改动 `shared/etk_core` 时必做）
- [ ] `python tools/check_repo.py` 输出「仓库检查通过。」
- [ ] `python -m pytest -q` 全部通过
- [ ] 改了技能内容：`python tools/check_release.py` 通过

## 发布合规（改了技能内容才需要填）

- [ ] 该技能已发布过，`release/published.json` 已登记且 `version` 与 `SKILL.md` 一致
- [ ] 版本号已递增（`SKILL.md` 的 `metadata.version` 与脚本 `__version__` 一起改）
- [ ] `docs/skills/<技能名>.md` 已同步；行为变化时 `README.md` 技能表也更新
- [ ] `CHANGELOG.md` 已记录
- [ ] 未联网、未 `eval` / `exec` / `compile`；如确需第三方包，已在技能根 `requirements.txt` 声明

## 备注

<!-- 已知限制、未覆盖场景、后续计划。若本次对外的分发渠道还没跟上，写清什么时候补 -->
