# VegasOFXPluginTranslation_zh-CN
为 VEGAS Pro 中的第三方 OFX 插件提供简体中文（zh-CN）汉化。

详见：https://www.bilibili.com/read/cv43150917/

**注意，这里不提供任何插件的破解版本。这里只提供 VEGAS Pro 可以读取的 XML 翻译文件。**

***Note that no cracked versions of any plugins are provided here. Only XML translation files that can be read by VEGAS Pro are provided.***

目前包含的插件汉化，及其对应的汉化贡献者：
```
蓝宝石 Sapphire 插件：夜__晓、Grok 3
BCC 插件：夜__晓、Grok 3
Ignite Pro 插件：夜__晓、Grok 3
NewBlue 插件：夜__晓、Grok 3
红巨星 Universe 插件：夜__晓、官方汉化
Textuler 插件：Grok 3
MisczOFX 插件：zzzzzz9125
TextOFX 插件：zzzzzz9125
NTSC-rs 插件：zzzzzz9125
OFXClock 插件：zzzzzz9125
Gyroflow 插件：Grok 3
```

## 使用方法
1. 解压 .zip 文件。里边有很多按照特定路径保存的 xxx.zh-CN.xml 翻译文件。
2. 转到 OFX 文件夹路径 `C:\Program Files\Common Files\OFX\Plugins\`。
3. 找到你的插件的 `.ofx` 安装位置，确认你的文件夹路径是否能和我提供的路径完全对上。若能完全对上，则可以直接合并文件夹；否则，请根据你的 OFX 路径结构，放置 XML 翻译文件。
4. 重启 VEGAS Pro。

路径示例：`C:\Program Files\Common Files\OFX\Plugins\xxx.ofx.bundle\Contents\Resources\xxx.zh-CN.xml`

```
├── xxx.ofx.bundle/
│  └── Contents/
│    ├── Presets/
│    │  ├── PresetPackage.xml
│    │  ├── PresetPackage.zh-CN.xml
│    │  └── ...
│    ├── Resources/
│    │  ├── xxx.xml
│    │  ├── xxx.zh-CN.xml
│    │  └── ...
│    └── Win64/
│       └── xxx.ofx
└── yyy.ofx.bundle/
   └── ...
```

其中，`Resources\xxx.xml` 和 `Resources\xxx.zh-CN.xml` 均为翻译文件。

如果遇到没法读取 `xxx.zh-CN.xml` 翻译文件的问题，这可能说明你的 VEGAS Pro 的语言注册表值并不指向中文。你可以尝试[将语言注册表值修改为中文](https://docs.qq.com/doc/p/c1828ff31c5f03da27dd6c0c26d49ddd6d1d868b)，或者也可以将 `xxx.zh-CN.xml` 重命名为 `xxx.xml`。

如果你之前装的是英文版插件，在安装汉化后，插件效果名称仍然保持英文，请转到 VEGAS Pro 缓存目录 `%localappdata%\VEGAS Pro\`（粘贴到文件管理器的地址栏后回车），找到 `%localappdata%\VEGAS Pro\<版本号>\plugin_manager_cache.bin` 并删除，之后重启 VEGAS Pro。

这样的外置 XML 的汉化形式似乎只支持 VEGAS Pro，不支持其他 OFX 插件宿主。让 DaVinci Resolve 用户测试过，没用。


## 插件官网
```
蓝宝石 Sapphire、BCC 插件：https://borisfx.com/
Ignite Pro 插件：https://www.fxhome.com/（注：FXHome 已经倒闭了。）
NewBlue 插件：https://newbluefx.com/
红巨星 Universe 插件：https://www.maxon.net/red-giant/universe
MisczOFX 插件：https://github.com/zzzzzz9125/Miscz
Textuler 插件：https://textuler.io/
NTSC-rs 插件：https://github.com/valadaptive/ntsc-rs
OFXClock 插件：https://www.hlinke.de/dokuwiki/doku.php?id=en:vegas_pro_ofx
Gyroflow 插件：https://gyroflow.xyz/
```

