#!/usr/bin/env python3
"""
XML/CSV Localization Tool with GUI
Supports:
- Extract specific tags from XML to CSV (xml2csv)
- Replace XML tag content from CSV (csv2xml)
- Batch file operations (rename, move, delete) with pattern matching
- Ignite Group Fix: Expand <OfxParamTypeGroup> elements with numbered names
"""

import os
import csv
import shutil
import fnmatch
import locale
import xml.etree.ElementTree as ET
import copy
from tkinter import (
    Tk, Frame, Label, Entry, Button, Listbox, Radiobutton,
    StringVar, IntVar, BooleanVar, Checkbutton, OptionMenu,
    Scrollbar, Text, messagebox, filedialog, Toplevel, simpledialog
)
from tkinter.ttk import Notebook, Progressbar
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("tkinterdnd2 not installed. Drag-and-drop disabled. Use file dialogs instead.\nUse \"pip install tkinterdnd2\" to install.")


class LocalizationTool:
    """Main GUI application with multilingual support."""

    # Target XML tags for extraction/replacement
    TARGET_TAGS = ['OfxPropLabel', 'OfxImageEffectPluginPropGrouping', 'OfxPropPluginDescription', 'OfxParamPropHint', 'OfxParamPropChoiceOption']

    # List of locale suffixes for dropdown presets (empty string = no suffix)
    LOCALE_SUFFIXES = ['', '.de-DE', '.es-ES', '.fr-FR',
                       '.ja-JP', '.ko-KR', '.pl-PL', '.pt-BR', '.zh-CN']

    # Translation dictionary: key -> {lang: translated_string}
    # Placeholders in curly braces (e.g., {count}) are kept as is.
    TRANSLATIONS = {
        # UI static texts
        "Function": {
            "en": "Function",
            "zh": "功能",
            "ja": "機能",
            "ko": "기능",
            "de": "Funktion",
            "es": "Función",
            "fr": "Fonction",
            "pl": "Funkcja",
            "pt": "Função"
        },
        "Extract XML to CSV (xml2csv)": {
            "en": "Extract XML to CSV (xml2csv)",
            "zh": "从XML提取到CSV (xml2csv)",
            "ja": "XMLをCSVに抽出 (xml2csv)",
            "ko": "XML에서 CSV로 추출 (xml2csv)",
            "de": "XML in CSV extrahieren (xml2csv)",
            "es": "Extraer XML a CSV (xml2csv)",
            "fr": "Extraire XML vers CSV (xml2csv)",
            "pl": "Wyodrębnij XML do CSV (xml2csv)",
            "pt": "Extrair XML para CSV (xml2csv)"
        },
        "Generate XML from CSV (csv2xml)": {
            "en": "Generate XML from CSV (csv2xml)",
            "zh": "从CSV生成XML (csv2xml)",
            "ja": "CSVからXMLを生成 (csv2xml)",
            "ko": "CSV에서 XML 생성 (csv2xml)",
            "de": "XML aus CSV generieren (csv2xml)",
            "es": "Generar XML desde CSV (csv2xml)",
            "fr": "Générer XML à partir de CSV (csv2xml)",
            "pl": "Generuj XML z CSV (csv2xml)",
            "pt": "Gerar XML a partir de CSV (csv2xml)"
        },
        "Batch Operations (rename/move/delete)": {
            "en": "Batch Operations (rename/move/delete)",
            "zh": "批量操作（重命名/移动/删除）",
            "ja": "一括操作（名前変更/移動/削除）",
            "ko": "일괄 작업(이름 바꾸기/이동/삭제)",
            "de": "Batch-Operationen (umbenennen/verschieben/löschen)",
            "es": "Operaciones por lotes (renombrar/mover/eliminar)",
            "fr": "Opérations par lots (renommer/déplacer/supprimer)",
            "pl": "Operacje wsadowe (zmiana nazwy/przenoszenie/usuwanie)",
            "pt": "Operações em lote (renomear/mover/excluir)"
        },
        "Ignite Group Fix": {
            "en": "Ignite Group Fix",
            "zh": "Ignite组修复",
            "ja": "Igniteグループ修正",
            "ko": "Ignite 그룹 수정",
            "de": "Ignite-Gruppenkorrektur",
            "es": "Corrección de grupos Ignite",
            "fr": "Correction de groupe Ignite",
            "pl": "Poprawa grup Ignite",
            "pt": "Correção de grupo Ignite"
        },
        "Input Files/Folders": {
            "en": "Input Files/Folders",
            "zh": "输入文件/文件夹",
            "ja": "入力ファイル/フォルダ",
            "ko": "입력 파일/폴더",
            "de": "Eingabedateien/-ordner",
            "es": "Archivos/Carpetas de entrada",
            "fr": "Fichiers/Dossiers d'entrée",
            "pl": "Pliki/Foldery wejściowe",
            "pt": "Arquivos/Pastas de entrada"
        },
        "Add Files...": {
            "en": "Add Files...",
            "zh": "添加文件...",
            "ja": "ファイルを追加...",
            "ko": "파일 추가...",
            "de": "Dateien hinzufügen...",
            "es": "Agregar archivos...",
            "fr": "Ajouter des fichiers...",
            "pl": "Dodaj pliki...",
            "pt": "Adicionar arquivos..."
        },
        "Add Folder...": {
            "en": "Add Folder...",
            "zh": "添加文件夹...",
            "ja": "フォルダを追加...",
            "ko": "폴더 추가...",
            "de": "Ordner hinzufügen...",
            "es": "Agregar carpeta...",
            "fr": "Ajouter un dossier...",
            "pl": "Dodaj folder...",
            "pt": "Adicionar pasta..."
        },
        "Remove Selected": {
            "en": "Remove Selected",
            "zh": "移除所选",
            "ja": "選択を削除",
            "ko": "선택 제거",
            "de": "Ausgewählte entfernen",
            "es": "Eliminar seleccionados",
            "fr": "Supprimer la sélection",
            "pl": "Usuń zaznaczone",
            "pt": "Remover selecionados"
        },
        "Clear All": {
            "en": "Clear All",
            "zh": "全部清除",
            "ja": "すべてクリア",
            "ko": "모두 지우기",
            "de": "Alle löschen",
            "es": "Limpiar todo",
            "fr": "Tout effacer",
            "pl": "Wyczyść wszystko",
            "pt": "Limpar tudo"
        },
        "File Filters & Options": {
            "en": "File Filters & Options",
            "zh": "文件筛选与选项",
            "ja": "ファイルフィルタとオプション",
            "ko": "파일 필터 및 옵션",
            "de": "Dateifilter und Optionen",
            "es": "Filtros de archivo y opciones",
            "fr": "Filtres de fichiers et options",
            "pl": "Filtry plików i opcje",
            "pt": "Filtros de arquivo e opções"
        },
        "Include pattern:": {
            "en": "Include pattern:",
            "zh": "包含模式:",
            "ja": "含むパターン:",
            "ko": "포함 패턴:",
            "de": "Einschlussmuster:",
            "es": "Patrón de inclusión:",
            "fr": "Modèle d'inclusion :",
            "pl": "Wzorzec dołączania:",
            "pt": "Padrão de inclusão:"
        },
        "Exclude pattern:": {
            "en": "Exclude pattern:",
            "zh": "排除模式:",
            "ja": "除外パターン:",
            "ko": "제외 패턴:",
            "de": "Ausschlussmuster:",
            "es": "Patrón de exclusión:",
            "fr": "Modèle d'exclusion :",
            "pl": "Wzorzec wykluczania:",
            "pt": "Padrão de exclusão:"
        },
        "Process subfolders recursively": {
            "en": "Process subfolders recursively",
            "zh": "递归处理子文件夹",
            "ja": "サブフォルダを再帰的に処理",
            "ko": "하위 폴더 재귀 처리",
            "de": "Unterordner rekursiv verarbeiten",
            "es": "Procesar subcarpetas recursivamente",
            "fr": "Traiter les sous-dossiers récursivement",
            "pl": "Przetwarzaj podfoldery rekurencyjnie",
            "pt": "Processar subpastas recursivamente"
        },
        "Function Parameters": {
            "en": "Function Parameters",
            "zh": "功能参数",
            "ja": "機能パラメータ",
            "ko": "기능 매개변수",
            "de": "Funktionsparameter",
            "es": "Parámetros de función",
            "fr": "Paramètres de fonction",
            "pl": "Parametry funkcji",
            "pt": "Parâmetros da função"
        },
        "Output file name pattern:": {
            "en": "Output file name pattern:",
            "zh": "输出文件名模式:",
            "ja": "出力ファイル名パターン:",
            "ko": "출력 파일 이름 패턴:",
            "de": "Muster für Ausgabedateinamen:",
            "es": "Patrón de nombre de archivo de salida:",
            "fr": "Modèle de nom de fichier de sortie :",
            "pl": "Wzorzec nazwy pliku wyjściowego:",
            "pt": "Padrão de nome de arquivo de saída:"
        },
        "Use {name} (base name) and {ext} (original extension)": {
            "en": "Use {name} (base name) and {ext} (original extension)",
            "zh": "使用 {name} (基本名) 和 {ext} (原始扩展名)",
            "ja": "{name} (ベース名) と {ext} (元の拡張子) を使用",
            "ko": "{name}(기본 이름) 및 {ext}(원래 확장자) 사용",
            "de": "Verwenden Sie {name} (Basisname) und {ext} (ursprüngliche Erweiterung)",
            "es": "Use {name} (nombre base) y {ext} (extensión original)",
            "fr": "Utilisez {name} (nom de base) et {ext} (extension d'origine)",
            "pl": "Użyj {name} (nazwa podstawowa) i {ext} (oryginalne rozszerzenie)",
            "pt": "Use {name} (nome base) e {ext} (extensão original)"
        },
        "CSV input pattern:": {
            "en": "CSV input pattern:",
            "zh": "CSV输入模式:",
            "ja": "CSV入力パターン:",
            "ko": "CSV 입력 패턴:",
            "de": "CSV-Eingabemuster:",
            "es": "Patrón de entrada CSV:",
            "fr": "Modèle d'entrée CSV :",
            "pl": "Wzorzec wejściowy CSV:",
            "pt": "Padrão de entrada CSV:"
        },
        "XML output pattern:": {
            "en": "XML output pattern:",
            "zh": "XML输出模式:",
            "ja": "XML出力パターン:",
            "ko": "XML 출력 패턴:",
            "de": "XML-Ausgabemuster:",
            "es": "Patrón de salida XML:",
            "fr": "Modèle de sortie XML :",
            "pl": "Wzorzec wyjściowy XML:",
            "pt": "Padrão de saída XML:"
        },
        "Patterns support {name} and {ext}": {
            "en": "Patterns support {name} and {ext}",
            "zh": "模式支持 {name} 和 {ext}",
            "ja": "パターンは {name} と {ext} をサポート",
            "ko": "패턴은 {name} 및 {ext} 지원",
            "de": "Muster unterstützen {name} und {ext}",
            "es": "Los patrones admiten {name} y {ext}",
            "fr": "Les modèles prennent en charge {name} et {ext}",
            "pl": "Wzorce obsługują {name} i {ext}",
            "pt": "Os padrões suportam {name} e {ext}"
        },
        "Operation:": {
            "en": "Operation:",
            "zh": "操作:",
            "ja": "操作:",
            "ko": "작업:",
            "de": "Operation:",
            "es": "Operación:",
            "fr": "Opération :",
            "pl": "Operacja:",
            "pt": "Operação:"
        },
        "Rename": {
            "en": "Rename",
            "zh": "重命名",
            "ja": "名前変更",
            "ko": "이름 바꾸기",
            "de": "Umbenennen",
            "es": "Renombrar",
            "fr": "Renommer",
            "pl": "Zmień nazwę",
            "pt": "Renomear"
        },
        "Move": {
            "en": "Move",
            "zh": "移动",
            "ja": "移動",
            "ko": "이동",
            "de": "Verschieben",
            "es": "Mover",
            "fr": "Déplacer",
            "pl": "Przenieś",
            "pt": "Mover"
        },
        "Delete": {
            "en": "Delete",
            "zh": "删除",
            "ja": "削除",
            "ko": "삭제",
            "de": "Löschen",
            "es": "Eliminar",
            "fr": "Supprimer",
            "pl": "Usuń",
            "pt": "Excluir"
        },
        "New name pattern:": {
            "en": "New name pattern:",
            "zh": "新名称模式:",
            "ja": "新しい名前パターン:",
            "ko": "새 이름 패턴:",
            "de": "Muster für neuen Namen:",
            "es": "Patrón de nuevo nombre:",
            "fr": "Modèle de nouveau nom :",
            "pl": "Wzorzec nowej nazwy:",
            "pt": "Padrão de novo nome:"
        },
        "Target folder:": {
            "en": "Target folder:",
            "zh": "目标文件夹:",
            "ja": "対象フォルダ:",
            "ko": "대상 폴더:",
            "de": "Zielordner:",
            "es": "Carpeta de destino:",
            "fr": "Dossier de destination :",
            "pl": "Folder docelowy:",
            "pt": "Pasta de destino:"
        },
        "Output Directory (optional)": {
            "en": "Output Directory (optional)",
            "zh": "输出目录（可选）",
            "ja": "出力ディレクトリ（オプション）",
            "ko": "출력 디렉터리(선택 사항)",
            "de": "Ausgabeverzeichnis (optional)",
            "es": "Directorio de salida (opcional)",
            "fr": "Répertoire de sortie (optionnel)",
            "pl": "Katalog wyjściowy (opcjonalny)",
            "pt": "Diretório de saída (opcional)"
        },
        "Browse...": {
            "en": "Browse...",
            "zh": "浏览...",
            "ja": "参照...",
            "ko": "찾아보기...",
            "de": "Durchsuchen...",
            "es": "Examinar...",
            "fr": "Parcourir...",
            "pl": "Przeglądaj...",
            "pt": "Procurar..."
        },
        "Keep folder structure relative to input": {
            "en": "Keep folder structure relative to input",
            "zh": "保持相对于输入的文件夹结构",
            "ja": "入力に対するフォルダ構造を保持",
            "ko": "입력 기준 폴더 구조 유지",
            "de": "Ordnerstruktur relativ zur Eingabe beibehalten",
            "es": "Mantener estructura de carpetas relativa a la entrada",
            "fr": "Conserver la structure de dossiers relative à l'entrée",
            "pl": "Zachowaj strukturę folderów względem wejścia",
            "pt": "Manter estrutura de pastas relativa à entrada"
        },
        "Log": {
            "en": "Log",
            "zh": "日志",
            "ja": "ログ",
            "ko": "로그",
            "de": "Protokoll",
            "es": "Registro",
            "fr": "Journal",
            "pl": "Dziennik",
            "pt": "Registro"
        },
        "Start Processing": {
            "en": "Start Processing",
            "zh": "开始处理",
            "ja": "処理開始",
            "ko": "처리 시작",
            "de": "Verarbeitung starten",
            "es": "Iniciar procesamiento",
            "fr": "Démarrer le traitement",
            "pl": "Rozpocznij przetwarzanie",
            "pt": "Iniciar processamento"
        },
        "Exit": {
            "en": "Exit",
            "zh": "退出",
            "ja": "終了",
            "ko": "종료",
            "de": "Beenden",
            "es": "Salir",
            "fr": "Quitter",
            "pl": "Wyjście",
            "pt": "Sair"
        },
        # Dialog titles and messages
        "Error": {
            "en": "Error",
            "zh": "错误",
            "ja": "エラー",
            "ko": "오류",
            "de": "Fehler",
            "es": "Error",
            "fr": "Erreur",
            "pl": "Błąd",
            "pt": "Erro"
        },
        "No input files/folders selected.": {
            "en": "No input files/folders selected.",
            "zh": "未选择输入文件/文件夹。",
            "ja": "入力ファイル/フォルダが選択されていません。",
            "ko": "입력 파일/폴더가 선택되지 않았습니다.",
            "de": "Keine Eingabedateien/-ordner ausgewählt.",
            "es": "No se seleccionaron archivos/carpetas de entrada.",
            "fr": "Aucun fichier/dossier d'entrée sélectionné.",
            "pl": "Nie wybrano plików/folderów wejściowych.",
            "pt": "Nenhum arquivo/pasta de entrada selecionado."
        },
        "Target folder for move operation is required.": {
            "en": "Target folder for move operation is required.",
            "zh": "移动操作需要目标文件夹。",
            "ja": "移動操作には対象フォルダが必要です。",
            "ko": "이동 작업에는 대상 폴더가 필요합니다.",
            "de": "Zielordner für Verschiebeoperation erforderlich.",
            "es": "Se requiere la carpeta de destino para la operación de mover.",
            "fr": "Le dossier de destination pour l'opération de déplacement est requis.",
            "pl": "Folder docelowy dla operacji przenoszenia jest wymagany.",
            "pt": "A pasta de destino para a operação de mover é obrigatória."
        },
        "New name pattern for rename is required.": {
            "en": "New name pattern for rename is required.",
            "zh": "重命名操作需要新名称模式。",
            "ja": "名前変更操作には新しい名前パターンが必要です。",
            "ko": "이름 바꾸기 작업에는 새 이름 패턴이 필요합니다.",
            "de": "Muster für neuen Namen für Umbenennung erforderlich.",
            "es": "Se requiere el patrón de nuevo nombre para renombrar.",
            "fr": "Le modèle de nouveau nom pour renommer est requis.",
            "pl": "Wzorzec nowej nazwy dla zmiany nazwy jest wymagany.",
            "pt": "O padrão de novo nome para renomear é obrigatório."
        },
        "Done": {
            "en": "Done",
            "zh": "完成",
            "ja": "完了",
            "ko": "완료",
            "de": "Fertig",
            "es": "Hecho",
            "fr": "Terminé",
            "pl": "Gotowe",
            "pt": "Concluído"
        },
        "Processed {count} files with {errors} errors.": {
            "en": "Processed {count} files with {errors} errors.",
            "zh": "已处理 {count} 个文件，{errors} 个错误。",
            "ja": "{count} ファイルを処理し、{errors} エラーがありました。",
            "ko": "{count}개 파일 처리, {errors}개 오류 발생.",
            "de": "{count} Dateien verarbeitet, {errors} Fehler.",
            "es": "Procesados {count} archivos con {errors} errores.",
            "fr": "{count} fichiers traités avec {errors} erreurs.",
            "pl": "Przetworzono {count} plików, {errors} błędów.",
            "pt": "Processados {count} arquivos com {errors} erros."
        },
        # Log messages
        "Starting processing...": {
            "en": "Starting processing...",
            "zh": "开始处理...",
            "ja": "処理を開始しています...",
            "ko": "처리 시작 중...",
            "de": "Verarbeitung wird gestartet...",
            "es": "Iniciando procesamiento...",
            "fr": "Démarrage du traitement...",
            "pl": "Rozpoczynanie przetwarzania...",
            "pt": "Iniciando processamento..."
        },
        "No files match the pattern.": {
            "en": "No files match the pattern.",
            "zh": "没有文件匹配模式。",
            "ja": "パターンに一致するファイルはありません。",
            "ko": "패턴과 일치하는 파일이 없습니다.",
            "de": "Keine Dateien entsprechen dem Muster.",
            "es": "Ningún archivo coincide con el patrón.",
            "fr": "Aucun fichier ne correspond au modèle.",
            "pl": "Żadne pliki nie pasują do wzorca.",
            "pt": "Nenhum arquivo corresponde ao padrão."
        },
        "Found {count} files to process.": {
            "en": "Found {count} files to process.",
            "zh": "找到 {count} 个文件待处理。",
            "ja": "{count} 個の処理対象ファイルが見つかりました。",
            "ko": "처리할 파일 {count}개를 찾았습니다.",
            "de": "{count} zu verarbeitende Dateien gefunden.",
            "es": "Se encontraron {count} archivos para procesar.",
            "fr": "{count} fichiers à traiter trouvés.",
            "pl": "Znaleziono {count} plików do przetworzenia.",
            "pt": "Encontrados {count} arquivos para processar."
        },
        "Processing XML: {path}": {
            "en": "Processing XML: {path}",
            "zh": "正在处理XML: {path}",
            "ja": "XMLを処理中: {path}",
            "ko": "XML 처리 중: {path}",
            "de": "Verarbeite XML: {path}",
            "es": "Procesando XML: {path}",
            "fr": "Traitement du XML : {path}",
            "pl": "Przetwarzanie XML: {path}",
            "pt": "Processando XML: {path}"
        },
        "  Extracted {count} values to {path}": {
            "en": "  Extracted {count} values to {path}",
            "zh": "  已提取 {count} 个值到 {path}",
            "ja": "  {count} 個の値を {path} に抽出しました",
            "ko": "  {count}개 값을 {path}에 추출했습니다",
            "de": "  {count} Werte extrahiert nach {path}",
            "es": "  Se extrajeron {count} valores a {path}",
            "fr": "  {count} valeurs extraites vers {path}",
            "pl": "  Wyodrębniono {count} wartości do {path}",
            "pt": "  Extraídos {count} valores para {path}"
        },
        "  CSV file not found: {path}, skipping.": {
            "en": "  CSV file not found: {path}, skipping.",
            "zh": "  找不到CSV文件：{path}，已跳过。",
            "ja": "  CSVファイルが見つかりません：{path}、スキップします。",
            "ko": "  CSV 파일을 찾을 수 없음: {path}, 건너뜁니다.",
            "de": "  CSV-Datei nicht gefunden: {path}, überspringe.",
            "es": "  Archivo CSV no encontrado: {path}, omitiendo.",
            "fr": "  Fichier CSV introuvable : {path}, ignoré.",
            "pl": "  Nie znaleziono pliku CSV: {path}, pomijanie.",
            "pt": "  Arquivo CSV não encontrado: {path}, ignorando."
        },
        "  CSV file too small (likely empty): {path}, skipping.": {
            "en": "  CSV file too small (likely empty): {path}, skipping.",
            "zh": "  CSV文件太小（可能为空）：{path}，已跳过。",
            "ja": "  CSVファイルが小さすぎます（空の可能性あり）：{path}、スキップします。",
            "ko": "  CSV 파일이 너무 작습니다(비어 있을 가능성 있음): {path}, 건너뜁니다.",
            "de": "  CSV-Datei zu klein (wahrscheinlich leer): {path}, überspringe.",
            "es": "  Archivo CSV demasiado pequeño (probablemente vacío): {path}, omitiendo.",
            "fr": "  Fichier CSV trop petit (probablement vide) : {path}, ignoré.",
            "pl": "  Plik CSV jest zbyt mały (prawdopodobnie pusty): {path}, pomijanie.",
            "pt": "  Arquivo CSV muito pequeno (provavelmente vazio): {path}, ignorando."
        },
        "  Output XML already exists: {path}, skipping (overwrite not implemented).": {
            "en": "  Output XML already exists: {path}, skipping (overwrite not implemented).",
            "zh": "  输出XML已存在：{path}，已跳过（未实现覆盖）。",
            "ja": "  出力XMLは既に存在します：{path}、スキップします（上書きは実装されていません）。",
            "ko": "  출력 XML이 이미 존재함: {path}, 건너뜁니다(덮어쓰기 미구현).",
            "de": "  Ausgabe-XML existiert bereits: {path}, überspringe (Überschreiben nicht implementiert).",
            "es": "  El XML de salida ya existe: {path}, omitiendo (sobrescritura no implementada).",
            "fr": "  Le XML de sortie existe déjà : {path}, ignoré (écrasement non implémenté).",
            "pl": "  Wyjściowy XML już istnieje: {path}, pomijanie (nadpisywanie niezaimplementowane).",
            "pt": "  XML de saída já existe: {path}, ignorando (sobrescrita não implementada)."
        },
        "  Warning: CSV has {csv_count} values, XML has {xml_count} target tags.": {
            "en": "  Warning: CSV has {csv_count} values, XML has {xml_count} target tags.",
            "zh": "  警告：CSV有 {csv_count} 个值，XML有 {xml_count} 个目标标签。",
            "ja": "  警告：CSVには {csv_count} 個の値、XMLには {xml_count} 個の対象タグがあります。",
            "ko": "  경고: CSV에 {csv_count}개 값, XML에 {xml_count}개 대상 태그가 있습니다.",
            "de": "  Warnung: CSV hat {csv_count} Werte, XML hat {xml_count} Ziel-Tags.",
            "es": "  Advertencia: CSV tiene {csv_count} valores, XML tiene {xml_count} etiquetas objetivo.",
            "fr": "  Attention : le CSV a {csv_count} valeurs, le XML a {xml_count} balises cibles.",
            "pl": "  Ostrzeżenie: CSV ma {csv_count} wartości, XML ma {xml_count} znaczników docelowych.",
            "pt": "  Aviso: CSV tem {csv_count} valores, XML tem {xml_count} tags alvo."
        },
        "  Warning: CSV values exhausted, leaving remaining tags unchanged.": {
            "en": "  Warning: CSV values exhausted, leaving remaining tags unchanged.",
            "zh": "  警告：CSV值已耗尽，剩余标签保持不变。",
            "ja": "  警告：CSVの値が尽きました。残りのタグは変更されません。",
            "ko": "  경고: CSV 값이 소진되어 나머지 태그는 변경되지 않습니다.",
            "de": "  Warnung: CSV-Werte erschöpft, verbleibende Tags bleiben unverändert.",
            "es": "  Advertencia: Valores de CSV agotados, las etiquetas restantes se dejan sin cambios.",
            "fr": "  Attention : valeurs CSV épuisées, les balises restantes sont inchangées.",
            "pl": "  Ostrzeżenie: Wartości CSV wyczerpane, pozostałe znaczniki pozostawione bez zmian.",
            "pt": "  Aviso: Valores de CSV esgotados, as tags restantes permanecem inalteradas."
        },
        "  Replaced {count} values, saved to {path}": {
            "en": "  Replaced {count} values, saved to {path}",
            "zh": "  已替换 {count} 个值，保存至 {path}",
            "ja": "  {count} 個の値を置換し、{path} に保存しました",
            "ko": "  {count}개 값을 바꾸고 {path}에 저장했습니다",
            "de": "  {count} Werte ersetzt, gespeichert unter {path}",
            "es": "  Se reemplazaron {count} valores, guardados en {path}",
            "fr": "  {count} valeurs remplacées, enregistrées dans {path}",
            "pl": "  Zastąpiono {count} wartości, zapisano do {path}",
            "pt": "  Substituídos {count} valores, salvos em {path}"
        },
        "Deleted: {path}": {
            "en": "Deleted: {path}",
            "zh": "已删除：{path}",
            "ja": "削除しました：{path}",
            "ko": "삭제됨: {path}",
            "de": "Gelöscht: {path}",
            "es": "Eliminado: {path}",
            "fr": "Supprimé : {path}",
            "pl": "Usunięto: {path}",
            "pt": "Excluído: {path}"
        },
        "Renamed: {old} -> {new}": {
            "en": "Renamed: {old} -> {new}",
            "zh": "已重命名：{old} -> {new}",
            "ja": "名前変更：{old} -> {new}",
            "ko": "이름 바꿈: {old} -> {new}",
            "de": "Umbenannt: {old} -> {new}",
            "es": "Renombrado: {old} -> {new}",
            "fr": "Renommé : {old} -> {new}",
            "pl": "Zmieniono nazwę: {old} -> {new}",
            "pt": "Renomeado: {old} -> {new}"
        },
        "Moved: {old} -> {new}": {
            "en": "Moved: {old} -> {new}",
            "zh": "已移动：{old} -> {new}",
            "ja": "移動：{old} -> {new}",
            "ko": "이동됨: {old} -> {new}",
            "de": "Verschoben: {old} -> {new}",
            "es": "Movido: {old} -> {new}",
            "fr": "Déplacé : {old} -> {new}",
            "pl": "Przeniesiono: {old} -> {new}",
            "pt": "Movido: {old} -> {new}"
        },
        "  No target directory for move, skipping {path}": {
            "en": "  No target directory for move, skipping {path}",
            "zh": "  未指定移动目标目录，跳过 {path}",
            "ja": "  移動先ディレクトリが指定されていないため、{path} をスキップします",
            "ko": "  이동 대상 디렉터리가 없어 {path} 건너뜁니다",
            "de": "  Kein Zielverzeichnis für Verschiebung, überspringe {path}",
            "es": "  No hay directorio de destino para mover, omitiendo {path}",
            "fr": "  Aucun répertoire de destination pour le déplacement, ignoré {path}",
            "pl": "  Brak katalogu docelowego dla przenoszenia, pomijanie {path}",
            "pt": "  Nenhum diretório de destino para mover, ignorando {path}"
        },
        "Processing completed.": {
            "en": "Processing completed.",
            "zh": "处理完成。",
            "ja": "処理が完了しました。",
            "ko": "처리가 완료되었습니다.",
            "de": "Verarbeitung abgeschlossen.",
            "es": "Procesamiento completado.",
            "fr": "Traitement terminé.",
            "pl": "Przetwarzanie zakończone.",
            "pt": "Processamento concluído."
        },
        "Encountered {count} error(s).": {
            "en": "Encountered {count} error(s).",
            "zh": "遇到 {count} 个错误。",
            "ja": "{count} エラーが発生しました。",
            "ko": "{count}개 오류가 발생했습니다.",
            "de": "{count} Fehler aufgetreten.",
            "es": "Se encontraron {count} error(es).",
            "fr": "{count} erreur(s) rencontrée(s).",
            "pl": "Napotkano {count} błędów.",
            "pt": "Encontrados {count} erro(s)."
        },
        # Ignite Group Fix specific
        "Group Max:": {
            "en": "Group Max:",
            "zh": "组最大值:",
            "ja": "グループ最大値:",
            "ko": "그룹 최대값:",
            "de": "Gruppenmaximum:",
            "es": "Máx. de grupo:",
            "fr": "Max de groupe :",
            "pl": "Maks. grupy:",
            "pt": "Máx. do grupo:"
        },
        "Maximum number for generated groups (e.g., 250)": {
            "en": "Maximum number for generated groups (e.g., 250)",
            "zh": "生成组数的最大值（例如 250）",
            "ja": "生成するグループの最大数（例：250）",
            "ko": "생성할 그룹의 최대 개수 (예: 250)",
            "de": "Maximale Anzahl generierter Gruppen (z.B. 250)",
            "es": "Número máximo de grupos generados (p.ej. 250)",
            "fr": "Nombre maximum de groupes générés (ex. 250)",
            "pl": "Maksymalna liczba generowanych grup (np. 250)",
            "pt": "Número máximo de grupos gerados (ex: 250)"
        },
        "Processing group fix for: {path}": {
            "en": "Processing group fix for: {path}",
            "zh": "正在处理组修复：{path}",
            "ja": "グループ修正を処理中：{path}",
            "ko": "그룹 수정 처리 중: {path}",
            "de": "Verarbeite Gruppenkorrektur für: {path}",
            "es": "Procesando corrección de grupo para: {path}",
            "fr": "Traitement de la correction de groupe pour : {path}",
            "pl": "Przetwarzanie poprawy grupy dla: {path}",
            "pt": "Processando correção de grupo para: {path}"
        },
        "  Found {count} contexts to process.": {
            "en": "  Found {count} contexts to process.",
            "zh": "  找到 {count} 个上下文待处理。",
            "ja": "  {count} 個のコンテキストが見つかりました。",
            "ko": "  처리할 컨텍스트 {count}개를 찾았습니다.",
            "de": "  {count} Kontexte zu verarbeiten gefunden.",
            "es": "  Se encontraron {count} contextos para procesar.",
            "fr": "  {count} contextes à traiter trouvés.",
            "pl": "  Znaleziono {count} kontekstów do przetworzenia.",
            "pt": "  Encontrados {count} contextos para processar."
        },
        "  Processed {count} groups in context {idx}.": {
            "en": "  Processed {count} groups in context {idx}.",
            "zh": "  在上下文 {idx} 中处理了 {count} 个组。",
            "ja": "  コンテキスト {idx} で {count} グループを処理しました。",
            "ko": "  컨텍스트 {idx}에서 {count}개 그룹을 처리했습니다.",
            "de": "  {count} Gruppen in Kontext {idx} verarbeitet.",
            "es": "  Se procesaron {count} grupos en el contexto {idx}.",
            "fr": "  {count} groupes traités dans le contexte {idx}.",
            "pl": "  Przetworzono {count} grup w kontekście {idx}.",
            "pt": "  Processados {count} grupos no contexto {idx}."
        },
        "  Total groups added: {total}.": {
            "en": "  Total groups added: {total}.",
            "zh": "  总共添加了 {total} 个组。",
            "ja": "  合計 {total} グループを追加しました。",
            "ko": "  총 {total}개 그룹이 추가되었습니다.",
            "de": "  Insgesamt {total} Gruppen hinzugefügt.",
            "es": "  Se agregaron {total} grupos en total.",
            "fr": "  Total de groupes ajoutés : {total}.",
            "pl": "  Łącznie dodano {total} grup.",
            "pt": "  Total de grupos adicionados: {total}."
        },
        "Saved fixed XML to {path}": {
            "en": "Saved fixed XML to {path}",
            "zh": "已保存修复后的XML到 {path}",
            "ja": "修正されたXMLを保存しました：{path}",
            "ko": "수정된 XML을 저장했습니다: {path}",
            "de": "Korrigierte XML gespeichert unter {path}",
            "es": "XML corregido guardado en {path}",
            "fr": "XML corrigé enregistré sous {path}",
            "pl": "Zapisano poprawiony XML do {path}",
            "pt": "XML corrigido salvo em {path}"
        },
        # New button for Exclude All Other Languages
        "Exclude All Other Languages": {
            "en": "Exclude All Other Languages",
            "zh": "排除其他所有语言",
            "ja": "他のすべての言語を除外",
            "ko": "다른 모든 언어 제외",
            "de": "Alle anderen Sprachen ausschließen",
            "es": "Excluir todos los demás idiomas",
            "fr": "Exclure toutes les autres langues",
            "pl": "Wyklucz wszystkie inne języki",
            "pt": "Excluir todos os outros idiomas"
        }
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Localization Tool")

        self.root.geometry("800x750")
        self.root.resizable(True, True)

        # Detect system language
        self.lang = self.detect_language()

        # Enable drag-and-drop if available
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)

        # Variables
        self.function = StringVar(value="xml2csv")
        self.input_paths = []
        self.file_pattern = StringVar(value="*.xml")
        self.exclude_pattern = StringVar(value="")
        # Base patterns (without locale suffix)
        self.base_output_name_pattern = "{name}.xml.csv"
        self.base_csv_input_pattern = "{name}.xml.csv"
        self.base_xml_output_pattern = "{name}.xml"
        # Actual pattern variables (initialized with base)
        self.output_name_pattern = StringVar(value=self.base_output_name_pattern)
        self.csv_input_pattern = StringVar(value=self.base_csv_input_pattern)
        self.xml_output_pattern = StringVar(value=self.base_xml_output_pattern)
        self.output_dir = StringVar()
        self.recursive = BooleanVar(value=True)
        self.batch_operation = StringVar(value="rename")
        self.batch_new_name = StringVar(value="{name}_new{ext}")
        self.batch_target_dir = StringVar()
        self.keep_structure = BooleanVar(value=True)
        # Ignite Group Fix variable
        self.group_max = IntVar(value=250)

        # Build UI
        self.create_widgets()
        self.update_ui_for_function()

    def detect_language(self):
        """
        Detect system language from locale.
        """
        try:
            locale_str, _ = locale.getdefaultlocale()
            if locale_str:
                lang_code = locale_str.split('_')[0].lower()
                if lang_code in ('zh', 'ja', 'ko', 'de', 'es', 'fr', 'pl', 'pt'):
                    return lang_code
        except Exception:
            pass
        # Default to English
        return 'en'

    def _(self, key, **kwargs):
        """
        Translate a string key into the current language.
        If key is not found, return the key itself.
        If kwargs are provided, perform str.format(**kwargs) on the translated string.
        """
        translations = self.TRANSLATIONS.get(key)
        if translations:
            text = translations.get(self.lang, translations.get('en', key))
        else:
            text = key  # fallback to key if not in dictionary
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                # If formatting fails (missing placeholder), return raw text
                return text
        return text

    def create_widgets(self):
        """Create all UI elements with translated texts and compact layout."""
        action_frame = Frame(self.root)
        action_frame.pack(fill="x", padx=5, pady=5)
        Button(action_frame, text=self._("Start Processing"),
            command=self.start_processing, bg="lightblue").pack(side="right", padx=2)
        Button(action_frame, text=self._("Exit"),
            command=self.root.quit).pack(side="right", padx=2)

        # Function selection
        func_frame = LabelFrame(self.root, text=self._("Function"), padx=5, pady=5)
        func_frame.pack(fill="x", padx=5, pady=2)
        Radiobutton(func_frame.content, text=self._("Extract XML to CSV (xml2csv)"), variable=self.function,
                    value="xml2csv", command=self.update_ui_for_function).grid(row=0, column=0, sticky="w", pady=1)
        Radiobutton(func_frame.content, text=self._("Generate XML from CSV (csv2xml)"), variable=self.function,
                    value="csv2xml", command=self.update_ui_for_function).grid(row=1, column=0, sticky="w", pady=1)
        Radiobutton(func_frame.content, text=self._("Batch Operations (rename/move/delete)"), variable=self.function,
                    value="batch", command=self.update_ui_for_function).grid(row=2, column=0, sticky="w", pady=1)
        Radiobutton(func_frame.content, text=self._("Ignite Group Fix"), variable=self.function,
                    value="ignite_group_fix", command=self.update_ui_for_function).grid(row=3, column=0, sticky="w", pady=1)

        # Input selection
        input_frame = LabelFrame(self.root, text=self._("Input Files/Folders"), padx=5, pady=5)
        input_frame.pack(fill="x", padx=5, pady=2)
        listbox_frame = Frame(input_frame.content)
        listbox_frame.pack(fill="both", expand=True, pady=2)
        self.input_listbox = Listbox(listbox_frame, height=4, selectmode="extended")
        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=self.input_listbox.yview)
        self.input_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.input_listbox.pack(side="left", fill="both", expand=True)
        btn_frame = Frame(input_frame.content)
        btn_frame.pack(fill="x", pady=2)
        Button(btn_frame, text=self._("Add Files..."), command=self.add_files).pack(side="left", padx=2)
        Button(btn_frame, text=self._("Add Folder..."), command=self.add_folder).pack(side="left", padx=2)
        Button(btn_frame, text=self._("Remove Selected"), command=self.remove_selected).pack(side="left", padx=2)
        Button(btn_frame, text=self._("Clear All"), command=self.clear_inputs).pack(side="left", padx=2)

        # File pattern and options
        pattern_frame = LabelFrame(self.root, text=self._("File Filters & Options"), padx=5, pady=5)
        pattern_frame.pack(fill="x", padx=5, pady=2)

        # Include pattern row with dropdown
        Label(pattern_frame.content, text=self._("Include pattern:")).grid(row=0, column=0, sticky="w", padx=2, pady=1)
        include_entry = Entry(pattern_frame.content, textvariable=self.file_pattern, width=30)
        include_entry.grid(row=0, column=1, sticky="w", padx=2)
        # Generate include pattern presets
        include_presets = ["*.xml"] + [f"*{suffix}.xml" for suffix in self.LOCALE_SUFFIXES[1:]]
        OptionMenu(pattern_frame.content, self.file_pattern, *include_presets).grid(row=0, column=2, padx=2)

        # Exclude pattern row with button
        Label(pattern_frame.content, text=self._("Exclude pattern:")).grid(row=1, column=0, sticky="w", padx=2, pady=1)
        exclude_entry = Entry(pattern_frame.content, textvariable=self.exclude_pattern, width=30)
        exclude_entry.grid(row=1, column=1, sticky="w", padx=2)
        Button(pattern_frame.content, text=self._("Exclude All Other Languages"),
               command=self.set_exclude_other_languages).grid(row=1, column=2, padx=2, pady=1)

        # Recursive checkbox
        Checkbutton(pattern_frame.content, text=self._("Process subfolders recursively"), variable=self.recursive).grid(row=2, column=0, columnspan=3, sticky="w", padx=2)

        # Dynamic parameters frame (changes with function)
        self.params_frame = LabelFrame(self.root, text=self._("Function Parameters"), padx=5, pady=5)
        self.params_frame.pack(fill="x", padx=5, pady=2)

        # Output directory (common for all functions)
        outdir_frame = LabelFrame(self.root, text=self._("Output Directory (optional)"), padx=5, pady=5)
        outdir_frame.pack(fill="x", padx=5, pady=2)
        Entry(outdir_frame.content, textvariable=self.output_dir, width=50).pack(side="left", padx=2, fill="x", expand=True)
        Button(outdir_frame.content, text=self._("Browse..."), command=self.browse_output_dir).pack(side="right", padx=2)
        Checkbutton(outdir_frame.content, text=self._("Keep folder structure relative to input"), variable=self.keep_structure).pack(anchor="w", padx=2)

        # Log output
        log_frame = LabelFrame(self.root, text=self._("Log"), padx=5, pady=5)
        log_frame.pack(fill="both", expand=True, padx=5, pady=2)
        self.log_text = Text(log_frame.content, height=5, wrap="word")
        log_scroll = Scrollbar(log_frame.content, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        # Progress bar
        self.progress = Progressbar(self.root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", padx=5, pady=2)

    def set_exclude_other_languages(self):
        """
        Set exclude pattern to exclude all language-specific XML files
        that are NOT included by the current include pattern.
        """
        include = self.file_pattern.get().strip()
        # If include is exactly "*.xml", we want to exclude all language-specific XML files
        if include == "*.xml":
            # Exclude all language-specific XML files
            exclude_patterns = [f"*{suffix}.xml" for suffix in self.LOCALE_SUFFIXES[1:]]
            self.exclude_pattern.set(";".join(exclude_patterns))
            return

        # Determine which language suffixes are present in the include pattern
        included_suffixes = set()
        # Check for each language suffix
        for suffix in self.LOCALE_SUFFIXES[1:]:  # skip empty
            if suffix in include:
                included_suffixes.add(suffix)

        # Build exclude patterns for suffixes NOT in included_suffixes
        exclude_patterns = []
        for suffix in self.LOCALE_SUFFIXES[1:]:
            if suffix not in included_suffixes:
                exclude_patterns.append(f"*{suffix}.xml")

        # Join with semicolons
        self.exclude_pattern.set(";".join(exclude_patterns))

    def get_presets(self, base_pattern):
        """
        Generate a list of preset strings for a given base pattern.
        Each suffix is inserted before the '.xml' part.
        Example: base "{name}.xml.csv" + suffix ".de-DE" -> "{name}.de-DE.xml.csv"
        """
        presets = [base_pattern]  # no suffix (empty) is just the base
        for suffix in self.LOCALE_SUFFIXES[1:]:  # skip the first empty string
            # Replace the first occurrence of '.xml' with suffix + '.xml'
            # This works for patterns like "{name}.xml.csv" and "{name}.xml"
            if '.xml' in base_pattern:
                preset = base_pattern.replace('.xml', suffix + '.xml', 1)
                presets.append(preset)
        return presets

    def update_ui_for_function(self):
        """Update the parameters frame based on selected function."""
        # Clear previous content
        for widget in self.params_frame.content.winfo_children():
            widget.destroy()

        func = self.function.get()

        if func == "xml2csv":
            # Output file name pattern with dropdown
            Label(self.params_frame.content, text=self._("Output file name pattern:")).grid(row=0, column=0, sticky="w", padx=2, pady=1)
            entry = Entry(self.params_frame.content, textvariable=self.output_name_pattern, width=40)
            entry.grid(row=0, column=1, sticky="w", padx=2)
            # Dropdown for presets
            presets = self.get_presets(self.base_output_name_pattern)
            var = self.output_name_pattern
            OptionMenu(self.params_frame.content, var, *presets).grid(row=0, column=2, padx=2)
            # Help text
            Label(self.params_frame.content, text=self._("Use {name} (base name) and {ext} (original extension)")).grid(row=1, column=0, columnspan=3, sticky="w", padx=2)

        elif func == "csv2xml":
            # CSV input pattern with dropdown
            Label(self.params_frame.content, text=self._("CSV input pattern:")).grid(row=0, column=0, sticky="w", padx=2, pady=1)
            entry_csv = Entry(self.params_frame.content, textvariable=self.csv_input_pattern, width=40)
            entry_csv.grid(row=0, column=1, sticky="w", padx=2)
            presets_csv = self.get_presets(self.base_csv_input_pattern)
            OptionMenu(self.params_frame.content, self.csv_input_pattern, *presets_csv).grid(row=0, column=2, padx=2)

            # XML output pattern with dropdown
            Label(self.params_frame.content, text=self._("XML output pattern:")).grid(row=1, column=0, sticky="w", padx=2, pady=1)
            entry_xml = Entry(self.params_frame.content, textvariable=self.xml_output_pattern, width=40)
            entry_xml.grid(row=1, column=1, sticky="w", padx=2)
            presets_xml = self.get_presets(self.base_xml_output_pattern)
            OptionMenu(self.params_frame.content, self.xml_output_pattern, *presets_xml).grid(row=1, column=2, padx=2)

            # Help text
            Label(self.params_frame.content, text=self._("Patterns support {name} and {ext}")).grid(row=2, column=0, columnspan=3, sticky="w", padx=2)

        elif func == "batch":
            Label(self.params_frame.content, text=self._("Operation:")).grid(row=0, column=0, sticky="w", padx=2, pady=1)
            op_frame = Frame(self.params_frame.content)
            op_frame.grid(row=0, column=1, sticky="w")
            Radiobutton(op_frame, text=self._("Rename"), variable=self.batch_operation, value="rename").pack(side="left", padx=1)
            Radiobutton(op_frame, text=self._("Move"), variable=self.batch_operation, value="move").pack(side="left", padx=1)
            Radiobutton(op_frame, text=self._("Delete"), variable=self.batch_operation, value="delete").pack(side="left", padx=1)

            self.rename_label = Label(self.params_frame.content, text=self._("New name pattern:"))
            self.rename_label.grid(row=1, column=0, sticky="w", padx=2, pady=1)
            self.rename_entry = Entry(self.params_frame.content, textvariable=self.batch_new_name, width=40)
            self.rename_entry.grid(row=1, column=1, sticky="w", padx=2)

            self.move_label = Label(self.params_frame.content, text=self._("Target folder:"))
            self.move_label.grid(row=2, column=0, sticky="w", padx=2, pady=1)
            move_frame = Frame(self.params_frame.content)
            move_frame.grid(row=2, column=1, sticky="w")
            self.move_entry = Entry(move_frame, textvariable=self.batch_target_dir, width=30)
            self.move_entry.pack(side="left")
            Button(move_frame, text=self._("Browse..."), command=self.browse_target_dir).pack(side="left", padx=2)

            self.update_batch_ui()
            self.batch_operation.trace('w', lambda *args: self.update_batch_ui())

        elif func == "ignite_group_fix":
            # Group max input
            Label(self.params_frame.content, text=self._("Group Max:")).grid(row=0, column=0, sticky="w", padx=2, pady=1)
            Entry(self.params_frame.content, textvariable=self.group_max, width=10).grid(row=0, column=1, sticky="w", padx=2)
            Label(self.params_frame.content, text=self._("Maximum number for generated groups (e.g., 250)")).grid(row=1, column=0, columnspan=2, sticky="w", padx=2)
            # Automatically set exclude pattern to avoid processing previously generated GroupFix files
            self.exclude_pattern.set("*.GroupFix.xml;*.GroupFix.*.xml")

    def update_batch_ui(self):
        """Show/hide batch operation specific widgets."""
        op = self.batch_operation.get()
        if op == "rename":
            self.rename_label.grid()
            self.rename_entry.grid()
            self.move_label.grid_remove()
            self.move_entry.master.grid_remove()
        elif op == "move":
            self.rename_label.grid_remove()
            self.rename_entry.grid_remove()
            self.move_label.grid()
            self.move_entry.master.grid()
        else:  # delete
            self.rename_label.grid_remove()
            self.rename_entry.grid_remove()
            self.move_label.grid_remove()
            self.move_entry.master.grid_remove()

    def browse_target_dir(self):
        """Browse for target directory in batch move."""
        dirname = filedialog.askdirectory(title=self._("Select Target Folder"))
        if dirname:
            self.batch_target_dir.set(dirname)

    def browse_output_dir(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title=self._("Select Output Directory"))
        if dirname:
            self.output_dir.set(dirname)

    def add_files(self):
        """Add files via file dialog."""
        files = filedialog.askopenfilenames(title=self._("Select Files"))
        for f in files:
            if f not in self.input_paths:
                self.input_paths.append(f)
                self.input_listbox.insert("end", f)

    def add_folder(self):
        """Add folder via directory dialog."""
        folder = filedialog.askdirectory(title=self._("Select Folder"))
        if folder and folder not in self.input_paths:
            self.input_paths.append(folder)
            self.input_listbox.insert("end", folder)

    def remove_selected(self):
        """Remove selected items from listbox."""
        selected = self.input_listbox.curselection()
        for i in reversed(selected):
            path = self.input_listbox.get(i)
            self.input_paths.remove(path)
            self.input_listbox.delete(i)

    def clear_inputs(self):
        """Clear all input paths."""
        self.input_paths.clear()
        self.input_listbox.delete(0, "end")

    def on_drop(self, event):
        """Handle drag-and-drop event."""
        files = self.root.tk.splitlist(event.data)
        for f in files:
            # Remove curly braces if present (Windows sometimes adds them)
            f = f.strip('{}')
            if f not in self.input_paths:
                self.input_paths.append(f)
                self.input_listbox.insert("end", f)

    def log(self, message):
        """Append message to log widget."""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def start_processing(self):
        """Start the selected function."""
        if not self.input_paths:
            messagebox.showerror(self._("Error"), self._("No input files/folders selected."))
            return

        # Validate batch parameters
        if self.function.get() == "batch":
            op = self.batch_operation.get()
            if op == "move" and not self.batch_target_dir.get():
                messagebox.showerror(self._("Error"), self._("Target folder for move operation is required."))
                return
            if op == "rename" and not self.batch_new_name.get():
                messagebox.showerror(self._("Error"), self._("New name pattern for rename is required."))
                return

        # Clear log
        self.log_text.delete(1.0, "end")
        self.log(self._("Starting processing..."))
        self.progress['value'] = 0
        self.root.update()

        # Collect all files to process
        all_files = []
        for path in self.input_paths:
            if os.path.isfile(path):
                # Single file: check pattern manually
                if self.matches_pattern(os.path.basename(path)):
                    all_files.append((path, os.path.dirname(path)))  # (full_path, base_dir)
            elif os.path.isdir(path):
                # Folder: walk if recursive
                if self.recursive.get():
                    for root_dir, _, files in os.walk(path):
                        for f in files:
                            full = os.path.join(root_dir, f)
                            if self.matches_pattern(f):
                                all_files.append((full, path))  # base_dir is the top input folder
                else:
                    for f in os.listdir(path):
                        full = os.path.join(path, f)
                        if os.path.isfile(full) and self.matches_pattern(f):
                            all_files.append((full, path))

        if not all_files:
            self.log(self._("No files match the pattern."))
            self.progress['value'] = 100
            return

        self.log(self._("Found {count} files to process.", count=len(all_files)))

        # Process according to function
        func = self.function.get()
        self.progress['maximum'] = len(all_files)

        errors = 0
        for idx, (file_path, base_dir) in enumerate(all_files):
            try:
                if func == "xml2csv":
                    self.process_xml2csv(file_path, base_dir)
                elif func == "csv2xml":
                    self.process_csv2xml(file_path, base_dir)
                elif func == "batch":
                    self.process_batch(file_path, base_dir)
                elif func == "ignite_group_fix":
                    self.process_ignite_group_fix(file_path, base_dir)
            except Exception as e:
                self.log(f"Error processing {file_path}: {str(e)}")
                errors += 1

            self.progress['value'] = idx + 1
            self.root.update()

        self.log(self._("Processing completed."))
        if errors:
            self.log(self._("Encountered {count} error(s).", count=errors))
        messagebox.showinfo(self._("Done"), self._("Processed {count} files with {errors} errors.", count=len(all_files), errors=errors))

    def matches_pattern(self, filename):
        """
        Check if filename matches include pattern(s) and does not match exclude pattern(s).
        Patterns can be separated by semicolons.
        """
        include_raw = self.file_pattern.get().strip()
        exclude_raw = self.exclude_pattern.get().strip()

        # Split patterns by semicolon, ignore empty strings
        include_patterns = [p.strip() for p in include_raw.split(';') if p.strip()] if include_raw else []
        exclude_patterns = [p.strip() for p in exclude_raw.split(';') if p.strip()] if exclude_raw else []

        # If no include patterns, file is considered included by default
        included = True
        if include_patterns:
            included = any(fnmatch.fnmatch(filename, pat) for pat in include_patterns)

        # Exclude takes precedence: if any exclude pattern matches, file is excluded
        excluded = any(fnmatch.fnmatch(filename, pat) for pat in exclude_patterns) if exclude_patterns else False

        return included and not excluded

    def get_output_path(self, original_path, base_dir, pattern, default_ext=""):
        """
        Generate output path based on pattern and output directory settings.
        original_path: full path of input file
        base_dir: the root folder of the input (for relative path calculation)
        pattern: naming pattern with {name} and {ext}
        Returns full output path.
        """
        dirname, filename = os.path.split(original_path)
        name, ext = os.path.splitext(filename)
        # Remove leading dot from extension for pattern
        ext_no_dot = ext[1:] if ext.startswith('.') else ext

        # Generate new filename
        new_filename = pattern.replace("{name}", name).replace("{ext}", ext_no_dot)
        if not new_filename:
            new_filename = name + default_ext

        # Determine output directory
        out_root = self.output_dir.get().strip()
        if out_root:
            if self.keep_structure.get():
                # Preserve relative path from base_dir
                rel_path = os.path.relpath(dirname, base_dir)
                if rel_path == '.':
                    out_dir = out_root
                else:
                    out_dir = os.path.join(out_root, rel_path)
            else:
                out_dir = out_root
        else:
            out_dir = dirname  # default to same folder

        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, new_filename)

    def process_xml2csv(self, xml_path, base_dir):
        """Extract target tags from XML to CSV."""
        self.log(self._("Processing XML: {path}", path=xml_path))
        # Generate CSV output path
        csv_path = self.get_output_path(xml_path, base_dir, self.output_name_pattern.get(), ".csv")

        # Parse XML and extract values
        tree = ET.parse(xml_path)
        root = tree.getroot()
        values = []
        for elem in root.iter():
            if elem.tag in self.TARGET_TAGS and elem.text:
                values.append([elem.text])

        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(values)

        self.log(self._("  Extracted {count} values to {path}", count=len(values), path=csv_path))

    def process_csv2xml(self, xml_path, base_dir):
        """Replace XML tag content from corresponding CSV."""
        # Generate CSV input path (using csv_input_pattern)
        csv_path = self.get_output_path(xml_path, base_dir, self.csv_input_pattern.get(), ".csv")
        if not os.path.exists(csv_path):
            self.log(self._("  CSV file not found: {path}, skipping.", path=csv_path))
            return
        if os.path.getsize(csv_path) < 4:  # at least BOM + one char
            self.log(self._("  CSV file too small (likely empty): {path}, skipping.", path=csv_path))
            return

        # Generate output XML path
        out_xml_path = self.get_output_path(xml_path, base_dir, self.xml_output_pattern.get(), ".xml")
        if os.path.exists(out_xml_path):
            self.log(self._("  Output XML already exists: {path}, skipping (overwrite not implemented).", path=out_xml_path))
            return

        # Read CSV values
        csv_values = []
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    csv_values.append(row[0])

        # Parse XML and replace values. Try to preserve XML comments when possible.
        try:
            # TreeBuilder(insert_comments=True) preserves <!-- comments --> nodes
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(xml_path, parser=parser)
        except Exception:
            # Fallback for older Python versions where insert_comments might not be supported
            tree = ET.parse(xml_path)
        root = tree.getroot()
        target_count = 0
        for elem in root.iter():
            if elem.tag in self.TARGET_TAGS and elem.text:
                target_count += 1

        if len(csv_values) < target_count:
            self.log(self._("  Warning: CSV has {csv_count} values, XML has {xml_count} target tags.",
                           csv_count=len(csv_values), xml_count=target_count))

        value_index = 0
        for elem in root.iter():
            if elem.tag in self.TARGET_TAGS and elem.text:
                if value_index < len(csv_values):
                    elem.text = csv_values[value_index]
                    value_index += 1
                else:
                    self.log(self._("  Warning: CSV values exhausted, leaving remaining tags unchanged."))
                    break

        # Save modified XML
        tree.write(out_xml_path, encoding='utf-8', xml_declaration=True)
        self.log(self._("  Replaced {count} values, saved to {path}", count=value_index, path=out_xml_path))

    def process_batch(self, file_path, base_dir):
        """Perform batch operation on a single file."""
        op = self.batch_operation.get()
        if op == "delete":
            os.remove(file_path)
            self.log(self._("Deleted: {path}", path=file_path))
        elif op == "rename":
            # Generate new name using pattern
            dirname, filename = os.path.split(file_path)
            name, ext = os.path.splitext(filename)
            ext_no_dot = ext[1:] if ext.startswith('.') else ''
            new_name = self.batch_new_name.get().replace("{name}", name).replace("{ext}", ext_no_dot)
            if not new_name:
                new_name = filename  # fallback
            new_path = os.path.join(dirname, new_name)
            # Avoid overwriting if exists
            counter = 1
            base_new, new_ext = os.path.splitext(new_path)
            while os.path.exists(new_path):
                new_path = f"{base_new}_{counter}{new_ext}"
                counter += 1
            os.rename(file_path, new_path)
            self.log(self._("Renamed: {old} -> {new}", old=file_path, new=new_path))
        elif op == "move":
            target_dir = self.batch_target_dir.get().strip()
            if not target_dir:
                self.log(self._("  No target directory for move, skipping {path}", path=file_path))
                return
            # Preserve relative path structure if keep_structure is checked
            if self.keep_structure.get():
                rel_path = os.path.relpath(os.path.dirname(file_path), base_dir)
                if rel_path == '.':
                    dest_dir = target_dir
                else:
                    dest_dir = os.path.join(target_dir, rel_path)
            else:
                dest_dir = target_dir
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, os.path.basename(file_path))
            # Avoid overwrite
            counter = 1
            base_dest, ext_dest = os.path.splitext(dest_path)
            while os.path.exists(dest_path):
                dest_path = f"{base_dest}_{counter}{ext_dest}"
                counter += 1
            shutil.move(file_path, dest_path)
            self.log(self._("Moved: {old} -> {new}", old=file_path, new=dest_path))

    def process_ignite_group_fix(self, xml_path, base_dir):
        """
        Fix Ignite group elements:
        For each <OfxImageEffectContext>, find all <OfxParamTypeGroup> whose name ends with a number.
        Replace each such group with (group_max+1) copies, with names numbered consecutively from the current start.
        The start resets to 0 at the beginning of each context and increments by (group_max+1) after each group.
        """
        self.log(self._("Processing group fix for: {path}", path=xml_path))

        # Parse XML
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Find all contexts
        contexts = root.findall(".//OfxImageEffectContext")
        self.log(self._("  Found {count} contexts to process.", count=len(contexts)))

        total_groups_added = 0
        group_max = self.group_max.get()  # user-specified max value (inclusive)

        for ctx_idx, context in enumerate(contexts):
            # We'll process children in order; we need to replace groups while iterating.
            # Collect all group elements (as list of (index, element)) to avoid modification during iteration.
            groups = []
            for i, child in enumerate(context):
                if child.tag == "OfxParamTypeGroup":
                    groups.append((i, child))

            if not groups:
                continue

            # Starting number for this context
            start_num = 0
            groups_processed = 0

            # We'll rebuild the children list from scratch or modify in place with insert/delete.
            # Simpler: collect all children as list, replace groups with expanded lists, then clear and re-extend.
            children = list(context)
            new_children = []
            idx = 0
            while idx < len(children):
                child = children[idx]
                if child.tag == "OfxParamTypeGroup":
                    name = child.get("name", "")
                    # Check if name ends with a number
                    if name and name[-1].isdigit():
                        # Find where digits end (from the end)
                        i = len(name) - 1
                        while i >= 0 and name[i].isdigit():
                            i -= 1
                        base_name = name[:i+1]  # includes any trailing non-digit
                        # Generate new groups from start_num to start_num+group_max
                        for num in range(start_num, start_num + group_max + 1):
                            new_elem = copy.deepcopy(child)
                            new_elem.set("name", f"{base_name}{num}")
                            new_children.append(new_elem)
                        # Update start for next group in this context
                        start_num += group_max + 1
                        groups_processed += 1
                    else:
                        # Not a numbered group, keep as is
                        new_children.append(child)
                else:
                    new_children.append(child)
                idx += 1

            # Replace context children
            context.clear()
            context.extend(new_children)
            total_groups_added += groups_processed * (group_max + 1)  # each replaced group expands to (max+1) copies
            self.log(self._("  Processed {count} groups in context {idx}.", count=groups_processed, idx=ctx_idx))

        self.log(self._("  Total groups added: {total}.", total=total_groups_added))

        # Determine output path
        # Use pattern: {name}.GroupFix.{ext} to produce filename like "IgnitePro.GroupFix.xml"
        out_pattern = "{name}.GroupFix.{ext}"
        out_path = self.get_output_path(xml_path, base_dir, out_pattern, ".xml")

        # Save the modified XML
        tree.write(out_path, encoding='utf-8', xml_declaration=True)
        self.log(self._("Saved fixed XML to {path}", path=out_path))


class LabelFrame(Frame):
    """Simple labeled frame (like tkinter.LabelFrame but without extra import)."""
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.label = Label(self, text=text, anchor="w", bg="lightgray")
        self.label.pack(fill="x", padx=1, pady=1)
        self.content = Frame(self)
        self.content.pack(fill="both", expand=True, padx=2, pady=2)


def main():
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = Tk()
    app = LocalizationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()