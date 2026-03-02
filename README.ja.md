# Vegas OFX Plugin Translation

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

このプロジェクトは、英語の元XML文字列をベースに、VEGAS Proで使用されるサードパーティ製OFXプラグイン向けの多言語ローカライズファイルを提供します。

## 法的注意事項

このリポジトリには、プラグインの海賊版・クラック版・改変バイナリは**含まれません**。

提供するのは、VEGAS Proで読み込めるXMLローカライズファイルのみです。

## VEGAS ProにおけるOFXとは

OFX（OpenFX）は、VEGAS Proおよび多くのサードパーティ映像エフェクトで使われるプラグイン標準です。

VEGAS Proでの一般的なOFXインストール先：

- 共有OFXパス：
  `C:\Program Files\Common Files\OFX\Plugins\`
- VEGAS専用OFXパス：
  `...<VEGAS インストールパス>\OFX Video Plug-Ins\`

OFXの基礎とVEGAS固有情報は、[VegTips](https://zzzzzz9125.github.io/VegTips/) のOFXセクションを参照してください。

典型的なOFXフォルダ構成：

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

補足：

- `Win64\xxx.ofx` はOFXプラグインのインターフェースバイナリです。
- `Presets\PresetPackage.xml` はプラグイン同梱プリセット定義です。
- 上記XMLはVEGAS Proが認識するローカライズファイルです。
- 言語タグなしの `xxx.xml` は通常英語のフォールバックです。
- `xxx.zh-CN.xml`、`xxx.ja-JP.xml` などは優先的に読み込まれます。
- 言語別XMLがない、または読込失敗時は `xxx.xml` にフォールバックします。
- 一覧にない言語は `xxx.xml` を直接編集可能です。
- 本リポジトリへ提出する場合は、適切なロケール接尾辞の命名を使用してください。

OFXフォルダの編集には管理者権限が必要なことが多いため、非昇格のメモ帳編集は推奨しません。Visual Studio Codeを推奨します（保存時に昇格保存を促せます）。

## チュートリアル

### 1) VEGAS Proの言語を変更する方法

[VegTips](https://zzzzzz9125.github.io/VegTips/) のIV章を参照してください。

### 2) VEGAS ProのOFXエフェクト名キャッシュを削除する方法

1. `%localappdata%\VEGAS Pro\` をエクスプローラーのアドレスバーに貼り付けてEnter。
2. VEGAS Pro 18以降：`%localappdata%\VEGAS Pro\<version>\plugin_manager_cache.bin` を削除。
   旧バージョン：`%localappdata%\VEGAS Pro\<version>\svfx_plugin_cache.bin` を削除。
3. VEGAS Proを再起動し、Video Plug-Ins Factoryの読み込み完了を待ちます。

### 3) 現在のVEGAS Proから全OFX文字列をエクスポートする方法

VEGAS Proで **Tools → Scripting** から `./Scripts/OFX_Translation_XML_Export.cs` を実行します。

このスクリプトは、現在のVEGAS環境で検出される内蔵OFXとサードパーティOFXのローカライズ文字列をエクスポートできます。

既定の出力先：`Desktop\OFX_XML`。

特定言語の文字列が必要な場合は、先にVEGASの言語変更とキャッシュ削除を行ってから再エクスポートしてください。

### 4) XML文字列を翻訳する方法

XMLは任意のテキストエディタで編集できます。翻訳前後比較がしやすいVisual Studio Codeを推奨します。

LLMを使った翻訳も可能です。

翻訳対象タグ：

- `OfxPropLabel`：FX表示名・パラメータ表示名
- `OfxImageEffectPluginPropGrouping`：FXグループ名
- `OfxPropPluginDescription`：FX説明文
- `OfxParamPropHint`：パラメータツールチップ
- `OfxParamPropChoiceOption`：`OfxParamTypeChoice` の選択肢

翻訳非推奨（本リポジトリではコメントアウトまたは削除推奨）：

- ファイル名関連文字列（例：`.bsp`、`.jpg`、`.config.ocio`）
- `OfxParamPropChoiceOption` に含まれるフォント名（BCC、Ignite Proで多い）
- VEGAS Proの不具合要因として既知の選択肢文字列

絶対に翻訳してはいけない項目：

- `OfxPlugin` の `name`（FX GUID）
- `OfxParamTypeDouble` の `name`（内部パラメータ名）

生XMLは冗長なため、LLMへ直接投入する翻訳素材としては非効率です。

本リポジトリの `./Scripts/xml_csv_tool.py` で次が可能です：

- XMLから翻訳対象文字列をCSVへ抽出
- 翻訳済みCSVをXMLへ再投入して新規XMLを生成

BCCなど一部プラグインのCSVはLLMのコンテキスト上限を超える場合があります。手動で分割して処理してください。

### 5) Ignite Group Fix について

Ignite Pro（`IgniteCore.ofx.bundle` と `IgnitePro.ofx.bundle`）は特殊なGroup読み込み方式を使います。

`OfxParamTypeGroup` の `name` は、同一VEGASプロセス内でのIgnite FX読み込み順によって変動します。`./Scripts/OFX_Translation_XML_Export.cs` も影響を受けます。

手順：

1. 新しいVEGASプロセスを起動し、Ignite FXを一切開かずに `OFX_Translation_XML_Export.cs` を実行。
   Igniteのみなら `White list` を `HitFilm` に設定。
2. ローカライズ後、`xml_csv_tool.py` の Ignite Group Fix を実行。
   `OfxParamTypeGroup` を複数回複製します。
   `Group Max` が複製回数で、値が大きいほど出力ファイルは大きくなります。
   小さすぎると、多数のIgnite FX読み込み後にローカライズが無効化される場合があります。
   既定値 `250` はサイズと有効性のバランスです。
3. 配布前にファイル名から `.GroupFix` を外し、正しいOFXパスへ配置してください。

### 6) Crash Fix について

一部プラグインの `OfxParamPropChoiceOption` は、初回プラグイン再スキャン時にVEGAS Pro起動エラーを引き起こす場合があります：An error occurred when starting VEGAS Pro. The cause of the error cannot be determined.

主な対象：

- BCC 2025以前のBCC+
- Sapphire 2025以前

新しい版（例：BCC 2026、Sapphire 2026）では発生しないことが多いです。

本リポジトリでCrashFixと付くファイル（例：`BCC+.CrashFix.zh-CN.xml`）は、初回再スキャンの安定性を優先して `OfxParamPropChoiceOption` を全削除しています。

使用手順：

1. ファイル名から `.CrashFix` を外して正しい場所に配置。
2. 再スキャン完了後、必要なら本リポジトリの完全版へ差し替え。
3. キャッシュ削除や新規プラグイン追加後は、同問題が再発し手順再実施が必要な場合があります。

恒久的な安定性を優先する場合はCrashFix版を使い続けることも可能ですが、`OfxParamPropChoiceOption` のローカライズは欠落します。
