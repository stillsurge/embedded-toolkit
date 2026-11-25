## 改了什么

<!-- 一句话说明改动范围 -->

## 为什么

<!-- 触发这次改动的问题、实测数据或手册依据 -->

## 验证

- [ ] `python tools/sync_core.py`（改动 `shared/etk_core` 时必做）
- [ ] `python tools/check_repo.py` 输出「仓库检查通过。」
- [ ] `python -m pytest -q` 全部通过

## 影响面

- [ ] 版本号已同步（`SKILL.md` metadata.version 与 scripts 的 `__version__`）
- [ ] `CHANGELOG.md` 已记录
- [ ] `README.md` / `docs/skills/` 已在行为变化时更新
- [ ] 未引入第三方运行时依赖，未联网，未 `eval` / `exec`

## 备注

<!-- 已知限制、未覆盖场景、后续计划 -->
