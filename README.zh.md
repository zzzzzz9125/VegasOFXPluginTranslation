# Vegas OFX Plugin Translation

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

本项目基于英文原始 XML 字符串，为 VEGAS Pro 中的第三方 OFX 插件提供多语言本地化翻译文件。

## 法律声明

本仓库**不提供**任何插件的盗版、破解或修改版二进制文件。

本仓库仅提供 VEGAS Pro 可读取的 XML 本地化翻译文件。

## OFX 插件在 VEGAS Pro 中是什么？

OFX（OpenFX）是 VEGAS Pro 和大量第三方视频特效使用的插件标准。

在 VEGAS Pro 中，OFX 插件通常安装在以下路径之一：

- 公共 OFX 路径：
  `C:\Program Files\Common Files\OFX\Plugins\`
- 独立 VEGAS OFX 路径：
  `...<VEGAS 安装路径>\OFX Video Plug-Ins\`

关于 OFX 和 VEGAS 相关机制，可参考 [VegTips](https://zzzzzz9125.github.io/VegTips/) 的 OFX 章节。

典型 OFX 目录结构：

```
├── xxx.ofx.bundle/
│  └── Contents/
│    ├── Presets/
│    │  ├── PresetPackage.xml
│    │  ├── PresetPackage.de-DE.xml
│    │  ├── PresetPackage.es-ES.xml
│    │  ├── PresetPackage.fr-FR.xml
│    │  ├── PresetPackage.ja-JP.xml
│    │  ├── PresetPackage.ko-KR.xml
│    │  ├── PresetPackage.pl-PL.xml
│    │  ├── PresetPackage.pt-BR.xml
│    │  └── PresetPackage.zh-CN.xml
│    ├── Resources/
│    │  ├── xxx.xml
│    │  ├── xxx.de-DE.xml
│    │  ├── xxx.es-ES.xml
│    │  ├── xxx.fr-FR.xml
│    │  ├── xxx.ja-JP.xml
│    │  ├── xxx.ko-KR.xml
│    │  ├── xxx.pl-PL.xml
│    │  ├── xxx.pt-BR.xml
│    │  └── xxx.zh-CN.xml
│    └── Win64/
│       └── xxx.ofx
└── yyy.ofx.bundle/
   └── ...
```

说明：

- `Win64\xxx.ofx` 是 OFX 插件接口文件。
- `Presets\PresetPackage.xml` 是插件自带预设文件。
- 上述 XML 均属于 VEGAS Pro 可识别的本地化文件。
- 不带语言标识的 `xxx.xml` 一般是英文回退文件。
- 带语言标识的 XML（如 `xxx.zh-CN.xml`、`xxx.ko-KR.xml`）会优先读取。
- 若对应语言 XML 不存在或读取失败，VEGAS Pro 会回退到 `xxx.xml`。
- 如果你的语言不在列表里，也可以直接修改 `xxx.xml`。
- 如果你要向本仓库提交文件，请尽量使用规范的语言后缀命名。

OFX 目录通常需要管理员权限才能写入，不建议直接用无管理员权限的记事本编辑 XML。推荐使用 Visual Studio Code，保存时可触发提权保存提示。

## 教程

### 1）如何修改 VEGAS Pro 语言

参考 [VegTips](https://zzzzzz9125.github.io/VegTips/) 的 IV 章节。

### 2）如何清理 VEGAS Pro 的 OFX 效果名称缓存

1. 复制 `%localappdata%\VEGAS Pro\` 到文件资源管理器地址栏并回车。
2. VEGAS Pro 18 及以上版本，删除 `%localappdata%\VEGAS Pro\<版本号>\plugin_manager_cache.bin`。
   低版本删除 `%localappdata%\VEGAS Pro\<版本号>\svfx_plugin_cache.bin`。
3. 重启 VEGAS Pro，并等待视频插件工厂加载完成。

### 3）如何导出当前 VEGAS Pro 中所有 OFX 插件字符串

在 VEGAS Pro 中，通过“工具 → 脚本化（Tools → Scripting）”运行 `./Scripts/OFX_Translation_XML_Export.cs`。

该脚本可以导出当前 VEGAS Pro 中所有内置 OFX 和第三方 OFX 插件的本地化文本。

默认导出目录：`桌面\OFX_XML`。

若要导出特定语言字符串，请先修改 VEGAS Pro 语言并清理效果名称缓存，再执行导出。

### 4）如何翻译 XML 字符串

可使用任意文本编辑器编辑 XML。推荐 Visual Studio Code，便于左右对比翻译前后文本。

也可以使用任意 LLM 模型辅助翻译。

可翻译标签：

- `OfxPropLabel`：FX 显示名称与参数显示名称
- `OfxImageEffectPluginPropGrouping`：FX 分组
- `OfxPropPluginDescription`：FX 描述
- `OfxParamPropHint`：参数悬浮提示
- `OfxParamPropChoiceOption`：`OfxParamTypeChoice` 参数的下拉选项

不建议翻译（在本仓库中应注释或删除）：

- 涉及文件名的字符串，例如 `.bsp`、`.jpg`、`.config.ocio`
- 以 `OfxParamPropChoiceOption` 形式出现的字体名称（BCC、Ignite Pro 中常见）
- 已知可能导致 VEGAS Pro 异常的选项字符串

绝对不能翻译：

- `OfxPlugin` 的 `name`（FX GUID）
- `OfxParamTypeDouble` 的 `name`（参数内部名）

由于 XML 冗余较多，不适合作为 LLM 直接翻译载体。

本仓库提供 `./Scripts/xml_csv_tool.py`，可用于：

- 从 XML 提取可翻译文本到 CSV
- 将翻译后的 CSV 回填生成新 XML

某些插件（如 BCC）的 CSV 仍可能超过多数 LLM 上下文长度，请手动分段处理。

### 5）关于 Ignite Group Fix

Ignite Pro（`IgniteCore.ofx.bundle` 与 `IgnitePro.ofx.bundle`）采用了较特殊的 Group 加载机制。

其 `OfxParamTypeGroup` 的 `name` 会随当前 VEGAS 进程中 Ignite FX 的加载顺序动态变化，`./Scripts/OFX_Translation_XML_Export.cs` 也会受影响。

流程：

1. 启动一个全新的 VEGAS Pro 进程，不打开任何 Ignite FX，直接运行 `OFX_Translation_XML_Export.cs`。
   若仅导出 Ignite，可将 `White list` 设为 `HitFilm`。
2. 完成本地化后，在 `xml_csv_tool.py` 中执行 Ignite Group Fix。
   该功能会对 `OfxParamTypeGroup` 做多次复制。
   `Group Max` 决定复制次数，值越大文件越大。
   若过小，用户加载较多 Ignite FX 后本地化仍可能失效。
   默认值 `250` 在体积与有效性之间较平衡。
3. 交付使用前，请去掉文件名中的 `.GroupFix`，并按正确路径放置 XML。

### 6）关于 Crash Fix

某些插件的 `OfxParamPropChoiceOption` 会在 VEGAS Pro 首次重新扫描插件时触发启动报错：启动 VEGAS Pro 时发生错误。无法确定错误的原因。

常见影响范围：

- BCC 2025 及以下版本的 BCC+
- Sapphire 2025 及以下版本

较新版本（例如 BCC 2026、Sapphire 2026）通常不会出现该问题。

本仓库中标记为 CrashFix 的文件（如 `BCC+.CrashFix.zh-CN.xml`）移除了全部 `OfxParamPropChoiceOption`，用于确保首次重新扫描插件时不报错。

使用方式：

1. 去掉文件名中的 `.CrashFix` 并按路径放置。
2. 完成重新扫描后，可替换回本仓库中的完整版本。
3. 若再次清理插件缓存或安装新插件，可能复现同类问题，需要重复处理。

若希望一次配置后长期稳定，可直接持续使用 CrashFix 版本；代价是 `OfxParamPropChoiceOption` 的本地化会全部缺失。
