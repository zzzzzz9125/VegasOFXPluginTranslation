# Vegas OFX Plugin Translation

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

This project provides localized translation files for third-party OFX plugins used in VEGAS Pro, based on the original English XML strings.

## Legal Notice

This repository does **not** include any pirated, cracked, or patched plugin binaries.

Only XML localization files that can be loaded by VEGAS Pro are provided.

## What is OFX in VEGAS Pro?

OFX (OpenFX) is a plugin standard used by VEGAS Pro and many third-party video effects.

In VEGAS Pro, OFX plugins are typically installed in one of these locations:

- Shared OFX path:
  `C:\Program Files\Common Files\OFX\Plugins\`
- Standalone VEGAS OFX path:
  `...<VEGAS installation path>\OFX Video Plug-Ins\`

For general OFX background and VEGAS-specific references, see the OFX section in [VegTips](https://zzzzzz9125.github.io/VegTips/).

Typical OFX bundle structure:

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

Notes:

- `Win64\xxx.ofx` is the OFX plugin interface binary.
- `Presets\PresetPackage.xml` is the built-in preset definition file.
- XML files listed above are language localization files recognized by VEGAS Pro.
- `xxx.xml` (without language tag) is usually the English fallback.
- `xxx.zh-CN.xml`, `xxx.ja-JP.xml`, etc. are language-specific files loaded with higher priority.
- If a localized file is not available or fails to load, VEGAS Pro falls back to `xxx.xml`.
- If your language is not in the list, you may edit `xxx.xml` directly.
- If you plan to contribute to this repository, use proper locale suffixes in file names.

Because OFX folders usually require administrator privileges, avoid editing XML files with non-elevated Notepad. Visual Studio Code is recommended (it can prompt for elevated save when needed).

## Tutorials

### 1) How to change VEGAS Pro language

Refer to Chapter IV on [VegTips](https://zzzzzz9125.github.io/VegTips/).

### 2) How to clear OFX effect-name cache in VEGAS Pro

1. Copy `%localappdata%\VEGAS Pro\` into File Explorer address bar and press Enter.
2. For VEGAS Pro 18 and newer, delete `%localappdata%\VEGAS Pro\<version>\plugin_manager_cache.bin`.
   For older versions, delete `%localappdata%\VEGAS Pro\<version>\svfx_plugin_cache.bin`.
3. Restart VEGAS Pro and wait until the Video Plug-Ins Factory finishes loading.

### 3) How to export all OFX strings from your current VEGAS Pro

In VEGAS Pro, run `./Scripts/OFX_Translation_XML_Export.cs` from **Tools → Scripting**.

This exports localized text from both built-in OFX effects and third-party OFX effects detected by your current VEGAS installation.

Default export folder: `Desktop\OFX_XML`.

If you need strings for a specific language, first change VEGAS Pro language and clear effect-name cache, then export again.

### 4) How to translate XML strings

You can use any text editor to edit XML. Visual Studio Code is recommended because side-by-side diff editing is useful for localization.

You can also use LLM tools for translation.

Translatable XML tags:

- `OfxPropLabel`: FX display name and parameter display name
- `OfxImageEffectPluginPropGrouping`: FX grouping/category name
- `OfxPropPluginDescription`: FX description
- `OfxParamPropHint`: parameter tooltip text
- `OfxParamPropChoiceOption`: dropdown options for `OfxParamTypeChoice`

Not recommended to translate (should be removed or commented in this repository):

- File name related strings, such as `.bsp`, `.jpg`, `.config.ocio`
- Font names stored as `OfxParamPropChoiceOption` (common in BCC and Ignite Pro)
- Known problematic options that may cause crashes in VEGAS Pro

Must never be translated:

- `OfxPlugin` attribute `name` (FX GUID)
- `OfxParamTypeDouble` attribute `name` (internal parameter key)

Because raw XML is verbose, it is not ideal for direct LLM translation input.

This repository provides `./Scripts/xml_csv_tool.py` to:

- extract translatable strings from XML to CSV
- write translated CSV back into XML and generate new XML files

Some plugin CSV files (for example BCC) can still exceed many LLM context limits. Split them manually into smaller segments.

### 5) About Ignite Group Fix

Ignite Pro (`IgniteCore.ofx.bundle` and `IgnitePro.ofx.bundle`) uses dynamic group loading behavior.

Its `OfxParamTypeGroup` `name` can change depending on the order in which Ignite FX are loaded in the current VEGAS process. This also affects `./Scripts/OFX_Translation_XML_Export.cs`.

Workflow:

1. Start a fresh VEGAS Pro process and do not open any Ignite FX. Run `OFX_Translation_XML_Export.cs`.
   If you only want Ignite effects, set `White list` to `HitFilm`.
2. After localization, run Ignite Group Fix in `xml_csv_tool.py`.
   It duplicates `OfxParamTypeGroup` entries multiple times.
   `Group Max` controls duplication count. Larger values increase output size.
   If too small, localization may still fail after many Ignite FX are loaded.
   Default `250` is a practical balance.
3. Before deployment, remove `.GroupFix` from file name and place the XML in the correct OFX path.

### 6) About Crash Fix

Some plugins have `OfxParamPropChoiceOption` values that may trigger VEGAS Pro startup errors during first plugin rescan: An error occurred when starting VEGAS Pro. The cause of the error cannot be determined.

Typical affected plugins include:

- BCC+ in BCC 2025 and earlier
- Sapphire in Sapphire 2025 and earlier

In many cases, newer versions (for example BCC 2026 and Sapphire 2026) do not show this issue.

Files marked as CrashFix in this repository (for example `BCC+.CrashFix.zh-CN.xml`) remove all `OfxParamPropChoiceOption` entries to avoid startup errors during initial rescan.

Usage:

1. Remove `.CrashFix` from file name and place it correctly.
2. After plugin rescan is complete, you may replace it with a full version from this repository.
3. If plugin cache is cleared again, or new plugins are installed, the same issue can return and the process must be repeated.

If you prefer a one-time stable setup, keep using the CrashFix variant, with the trade-off that all `OfxParamPropChoiceOption` localization is missing.
