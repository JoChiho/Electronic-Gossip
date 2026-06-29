# Changelog

本文件记录 bagua 各版本变更，格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [0.9.3] - 2026-06-29

### Added

- **六十四卦爻辞全文**（384 条《周易》原文，`yao_texts_data.py`）
- AI 提示词与 Markdown 导出附带爻辞；变爻以 ★ 标注
- 构建脚本 `scripts/build_yao_texts.py`（数据来源 open-iching）

## [0.9.2] - 2026-06-29

### Added

- 历史记录**搜索**：CLI `--list-records --search <关键词>`；GUI 历史窗口搜索框
- 历史记录**导出 Markdown**：`--export-record` / `--export-records`（支持 `-o` 与 `--search` 筛选）
- GUI 历史窗口：「导出所选」「导出列表」按钮
- 模块 `record_markdown.py`：记录转 Markdown 纯逻辑

### Changed

- GUI 主表单：出生/起卦地点与经纬度展示（真太阳时）
- GUI 布局：AI 提示词全宽主区域、复制工具栏

## [0.9.1] - 2026-06-29

### Added

- **出生时区**与**起卦时区**拆分（GUI 时间起卦区 / CLI 分步设置）
- 出生经度 / 起卦经度分开配置；八字与起卦真太阳时独立开关
- 八字排盘支持出生地真太阳时（仅影响八字，不参与卦象演算）

### Changed

- 旧版 `longitude` / `use_true_solar` 配置自动迁移为起卦字段

## [0.9.0] - 2026-06-29

### Added

- 时间起卦：公历输入不变，算卦自动换算**节气历**（立春换年、寅月起算）
- **真太阳时**校正（经度修正 + 时差方程）；设置面板可配经度与开关
- AI 提示词展示用户公历时刻 + 节气历算卦分量，并注明解读口径

### Changed

- 公历时间起卦不再直接用公历月日数字；农历显式输入模式保持原逻辑

## [0.8.1] - 2026-06-29

### Changed

- 拆分 `gui.py`：`gui_app.py`（主窗口）、`gui_forms.py`（表单与配置）、`gui_history.py`、`gui_constants.py`
- CI 接入 `ruff` 静态检查与 `mypy` 类型检查
- 发版脚本增加 `check_release.py` 版本与 CHANGELOG 一致性校验

## [0.8.0] - 2026-06-24

### Added

- CLI/GUI 配置互通：起卦方式、铜钱输入、时间选项跨入口共享
- GUI 设置面板：自动排盘 / 自动复制 / 卦辞开关
- 非交互模式读取 config；`--no-copy` 关闭自动复制
- Windows 安装说明：`docs/WINDOWS_INSTALL.md`

## [0.7.0] - 2026-06-24

### Added

- PyInstaller 双版本：`bagua.exe` + `bagua-gui.exe`
- 构建脚本：`scripts/build.ps1` / `scripts/build.sh`
- Release CI：push tag `v*` 自动构建 zip
- 项目状态文档：`docs/PROJECT_STATUS.md`

## [0.6.0] - 2026-06-24

### Added

- 八字自动排盘：出生时间 → 八字；CLI/GUI 均支持
- 农历时间起卦：`--calendar lunar` / GUI 历法切换
- 卦辞摘要：AI 提示词附带本卦/之卦卦辞要点
- 夏令时提示：tzdata 可用时自动 DST；回退模式明确提示

## [0.5.0] - 2026-06-24

### Added

- CLI 非交互参数：`--method` / `-q` / `--save` / `--copy` 等
- 历史记录管理：`--list-records` / `--show-record` / `--delete-record`
- GUI 历史记录：历史窗口查看、加载提示词、删除
- GUI 卦象 Canvas：六爻图形化绘制
- 剪贴板优化：`clipboard.py` 多平台回退

## [0.4.0] - 2026-06-24

### Added

- Tkinter GUI：图形界面起卦、复制提示词、保存记录
- 双入口：`python -m bagua`（CLI）/ `python -m bagua.gui`（GUI）

## [0.3.0] - 2026-06-24

### Changed

- 架构重构：拆分 service / divination / hexagram 等模块，CLI 瘦身
- `perform_divination()`：CLI 与 GUI 共用统一起卦入口
- 测试增至 20 项：含 test_service.py、test_divination.py

## [0.2.1] - 2026-06-24

### Fixed

- Windows 启动崩溃 `ZoneInfoNotFoundError`：添加 `tzdata` 依赖 + 固定偏移回退

### Changed

- 铜钱法自动模拟；输入改为 `1`/`2`
- 时区地区选择 + 完整标注
- 用户信息持久化至 `~/.bagua/config.json`
- pytest + GitHub Actions CI

[0.9.3]: https://github.com/example/bagua/compare/v0.9.2...v0.9.3
[0.9.2]: https://github.com/example/bagua/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/example/bagua/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/example/bagua/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/example/bagua/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/example/bagua/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/example/bagua/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/example/bagua/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/example/bagua/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/example/bagua/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/example/bagua/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/example/bagua/releases/tag/v0.2.1