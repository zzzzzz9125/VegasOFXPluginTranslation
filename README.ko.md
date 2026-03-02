# Vegas OFX Plugin Translation

[English](README.md) | [简体中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md)

이 프로젝트는 영어 원본 XML 문자열을 기반으로, VEGAS Pro에서 사용하는 서드파티 OFX 플러그인을 위한 다국어 로컬라이징 파일을 제공합니다.

## 법적 고지

이 저장소에는 플러그인의 불법 복제본, 크랙 버전, 수정된 바이너리가 **포함되지 않습니다**.

VEGAS Pro에서 읽을 수 있는 XML 로컬라이징 파일만 제공합니다.

## VEGAS Pro의 OFX란?

OFX(OpenFX)는 VEGAS Pro 및 다양한 서드파티 영상 효과 플러그인이 사용하는 표준입니다.

VEGAS Pro에서 OFX 플러그인은 보통 다음 경로 중 하나에 설치됩니다.

- 공용 OFX 경로:
  `C:\Program Files\Common Files\OFX\Plugins\`
- VEGAS 전용 OFX 경로:
  `...<VEGAS 설치 경로>\OFX Video Plug-Ins\`

OFX 기본 개념과 VEGAS 관련 설명은 [VegTips](https://zzzzzz9125.github.io/VegTips/) 의 OFX 섹션을 참고하세요.

일반적인 OFX 번들 구조:

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

설명:

- `Win64\xxx.ofx` 는 OFX 플러그인 인터페이스 바이너리입니다.
- `Presets\PresetPackage.xml` 는 플러그인 기본 프리셋 정의 파일입니다.
- 위 XML 파일들은 VEGAS Pro가 인식하는 로컬라이징 파일입니다.
- 언어 태그가 없는 `xxx.xml` 은 일반적으로 영어 폴백 파일입니다.
- `xxx.zh-CN.xml`, `xxx.ko-KR.xml` 같은 언어별 XML이 우선 로드됩니다.
- 언어별 XML이 없거나 로드 실패 시 `xxx.xml` 로 폴백됩니다.
- 목록에 없는 언어는 `xxx.xml` 을 직접 수정할 수 있습니다.
- 이 저장소에 기여할 때는 표준 로케일 접미사 파일명을 사용하세요.

OFX 경로는 보통 관리자 권한이 필요하므로, 권한 없는 메모장 편집은 권장하지 않습니다. Visual Studio Code 사용을 권장합니다(저장 시 권한 상승 저장 안내 가능).

## 튜토리얼

### 1) VEGAS Pro 언어 변경 방법

[VegTips](https://zzzzzz9125.github.io/VegTips/) 의 IV 장을 참고하세요.

### 2) VEGAS Pro OFX 효과 이름 캐시 삭제 방법

1. `%localappdata%\VEGAS Pro\` 를 파일 탐색기 주소창에 붙여넣고 Enter를 누릅니다.
2. VEGAS Pro 18 이상은 `%localappdata%\VEGAS Pro\<버전>\plugin_manager_cache.bin` 삭제.
   구버전은 `%localappdata%\VEGAS Pro\<버전>\svfx_plugin_cache.bin` 삭제.
3. VEGAS Pro를 재시작하고 Video Plug-Ins Factory 로딩 완료를 기다립니다.

### 3) 현재 VEGAS Pro의 모든 OFX 문자열 내보내기

VEGAS Pro에서 **Tools → Scripting** 메뉴로 `./Scripts/OFX_Translation_XML_Export.cs` 를 실행합니다.

이 스크립트는 현재 VEGAS 환경에서 감지되는 기본 OFX 및 서드파티 OFX의 로컬라이징 문자열을 내보냅니다.

기본 출력 폴더: `Desktop\OFX_XML`.

특정 언어 문자열이 필요하면 먼저 VEGAS 언어를 변경하고 캐시를 지운 뒤 다시 내보내세요.

### 4) XML 문자열 번역 방법

XML은 어떤 텍스트 편집기로도 수정할 수 있습니다. 번역 전후 비교를 위해 Visual Studio Code를 권장합니다.

LLM을 사용해 번역해도 됩니다.

번역 가능한 태그:

- `OfxPropLabel`: FX 표시 이름 및 파라미터 표시 이름
- `OfxImageEffectPluginPropGrouping`: FX 그룹/카테고리 이름
- `OfxPropPluginDescription`: FX 설명
- `OfxParamPropHint`: 파라미터 툴팁
- `OfxParamPropChoiceOption`: `OfxParamTypeChoice` 드롭다운 옵션

번역 비권장(이 저장소에서는 주석 처리 또는 삭제 권장):

- 파일명 관련 문자열(예: `.bsp`, `.jpg`, `.config.ocio`)
- `OfxParamPropChoiceOption` 형태의 폰트 이름(BCC, Ignite Pro에서 흔함)
- VEGAS Pro 문제를 일으킬 수 있는 것으로 알려진 옵션 문자열

절대 번역하면 안 되는 항목:

- `OfxPlugin` 의 `name`(FX GUID)
- `OfxParamTypeDouble` 의 `name`(파라미터 내부 키)

원본 XML은 중복 정보가 많아 LLM에 직접 넣어 번역하기에 비효율적입니다.

이 저장소의 `./Scripts/xml_csv_tool.py` 로 다음 작업이 가능합니다:

- XML에서 번역 대상 문자열을 CSV로 추출
- 번역된 CSV를 XML에 다시 반영해 새 XML 생성

BCC 등 일부 플러그인의 CSV는 LLM 컨텍스트 한도를 넘을 수 있으므로 수동 분할 처리하세요.

### 5) Ignite Group Fix 안내

Ignite Pro(`IgniteCore.ofx.bundle`, `IgnitePro.ofx.bundle`)는 특이한 Group 로딩 방식을 사용합니다.

`OfxParamTypeGroup` 의 `name` 이 같은 VEGAS 프로세스 내에서 Ignite FX 로딩 순서에 따라 동적으로 변합니다. `./Scripts/OFX_Translation_XML_Export.cs` 도 영향을 받습니다.

절차:

1. 새 VEGAS Pro 프로세스를 시작하고 Ignite FX를 하나도 열지 않은 상태에서 `OFX_Translation_XML_Export.cs` 실행.
   Ignite만 내보내려면 `White list` 를 `HitFilm` 으로 설정.
2. 로컬라이징 후 `xml_csv_tool.py` 의 Ignite Group Fix 실행.
   `OfxParamTypeGroup` 항목을 여러 번 복제합니다.
   `Group Max` 는 복제 횟수이며 값이 클수록 출력 파일이 커집니다.
   값이 너무 작으면 많은 Ignite FX 로딩 후 로컬라이징이 다시 깨질 수 있습니다.
   기본값 `250` 은 용량과 효과의 균형값입니다.
3. 배포 전에 파일명에서 `.GroupFix` 를 제거하고 올바른 OFX 경로에 배치하세요.

### 6) Crash Fix 안내

일부 플러그인의 `OfxParamPropChoiceOption` 은 첫 플러그인 재스캔 시 VEGAS Pro 시작 오류를 유발할 수 있습니다.

주요 대상:

- BCC 2025 이하의 BCC+
- Sapphire 2025 이하

신규 버전(예: BCC 2026, Sapphire 2026)에서는 보통 이 문제가 줄어듭니다.

이 저장소에서 CrashFix가 붙은 파일(예: `BCC+.CrashFix.zh-CN.xml`)은 초기 재스캔 안정성을 위해 `OfxParamPropChoiceOption` 을 전부 제거한 버전입니다.

사용 방법:

1. 파일명에서 `.CrashFix` 를 제거한 뒤 올바른 위치에 배치.
2. 재스캔 완료 후 필요하면 저장소의 전체 버전으로 교체.
3. 캐시를 다시 지우거나 새 플러그인을 설치하면 같은 문제가 재발할 수 있어 동일 절차를 반복해야 할 수 있습니다.

한 번 설정 후 안정성을 우선하려면 CrashFix 버전을 계속 사용할 수 있지만, `OfxParamPropChoiceOption` 로컬라이징은 누락됩니다.
