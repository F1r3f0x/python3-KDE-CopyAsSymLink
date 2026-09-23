#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
#       PasteAsSymLink
#
#       This script creates a symlink for a given path(s) on the clipboard
#
#       Copyright 2025 Patricio Labin Correa @f1r3f0x <plabin@outlook.cl>
#
import os
import sys
import subprocess
import shutil
import re
from urllib.parse import urlparse, unquote

TRANSLATIONS: dict[str, dict[str, str]] = {
    "title": {
        "en": "Paste as SymLink",
        "es": "Pegar como Enlace Simbólico",
        "ca": "Enganxa com a enllaç simbòlic",
        "cs": "Vložit jako symbolický odkaz",
        "de": "Als symbolische Verknüpfung einfügen",
        "fr": "Coller comme lien symbolique",
        "it": "Incolla come collegamento simbolico",
        "ja": "シンボリックリンクとして貼り付け",
        "ko": "심볼릭 링크로 붙여넣기",
        "nl": "Plakken als symbolische link",
        "pl": "Wklej jako dowiązanie symboliczne",
        "pt": "Colar como Ligação Simbólica",
        "pt_BR": "Colar como Link Simbólico",
        "ru": "Вставить как символическую ссылку",
        "sv": "Klistra in som symbolisk länk",
        "tr": "Sembolik Bağ Olarak Yapıştır",
        "uk": "Вставити як символічне посилання",
        "zh_CN": "粘贴为符号链接",
        "zh_TW": "貼上為符號連結",
    },
    "err_no_target": {
        "en": "Error: No target directory provided.",
        "es": "Error: No se proporcionó un directorio de destino.",
        "ca": "Error: No s'ha proporcionat cap directori de destinació.",
        "cs": "Chyba: Nebyl zadán žádný cílový adresář.",
        "de": "Fehler: Kein Zielverzeichnis angegeben.",
        "fr": "Erreur : Aucun répertoire cible fourni.",
        "it": "Errore: Nessuna cartella di destinazione fornita.",
        "ja": "エラー: 対象ディレクトリが指定されていません。",
        "ko": "오류: 대상 디렉터리가 지정되지 않았습니다.",
        "nl": "Fout: Geen doelmap opgegeven.",
        "pl": "Błąd: Nie podano katalogu docelowego.",
        "pt": "Erro: Nenhum diretório de destino fornecido.",
        "pt_BR": "Erro: Nenhum diretório de destino fornecido.",
        "ru": "Ошибка: Целевой каталог не указан.",
        "sv": "Fel: Ingen målkatalog angiven.",
        "tr": "Hata: Hedef dizin belirtilmedi.",
        "uk": "Помилка: Не вказано цільовий каталог.",
        "zh_CN": "错误：未提供目标目录。",
        "zh_TW": "錯誤：未提供目標目錄。",
    },
    "err_target_invalid": {
        "en": "Error: Target directory '{target}' does not exist or is not a directory.",
        "es": "Error: El directorio de destino '{target}' no existe o no es un directorio.",
        "ca": "Error: El directori de destinació '{target}' no existeix o no és un directori.",
        "cs": "Chyba: Cílový adresář '{target}' neexistuje nebo není adresářem.",
        "de": "Fehler: Zielverzeichnis '{target}' existiert nicht oder ist kein Verzeichnis.",
        "fr": "Erreur : Le répertoire cible « {target} » n'existe pas ou n'est pas un répertoire.",
        "it": "Errore: La cartella di destinazione '{target}' non esiste o non è una cartella.",
        "ja": "エラー: 対象ディレクトリ '{target}' は存在しないか、ディレクトリではありません。",
        "ko": "오류: 대상 디렉터리 '{target}'이(가) 존재하지 않거나 디렉터리가 아닙니다.",
        "nl": "Fout: Doelmap '{target}' bestaat niet of is geen map.",
        "pl": "Błąd: Katalog docelowy '{target}' nie istnieje lub nie jest katalogiem.",
        "pt": "Erro: O diretório de destino '{target}' não existe ou não é um diretório.",
        "pt_BR": "Erro: O diretório de destino '{target}' não existe ou não é um diretório.",
        "ru": "Ошибка: Целевой каталог '{target}' не существует или не является каталогом.",
        "sv": "Fel: Målkatalogen '{target}' finns inte eller är inte en katalog.",
        "tr": "Hata: Hedef dizin '{target}' mevcut değil veya bir dizin değil.",
        "uk": "Помилка: Цільовий каталог '{target}' не існує або не є каталогом.",
        "zh_CN": "错误：目标目录“{target}”不存在或不是目录。",
        "zh_TW": "錯誤：目標目錄「{target}」不存在或不是目錄。",
    },
    "err_clipboard_empty": {
        "en": "Error: Clipboard is empty or could not be read.",
        "es": "Error: El portapapeles está vacío o no se pudo leer.",
        "ca": "Error: El porta-retalls està buit o no s'ha pogut llegir.",
        "cs": "Chyba: Schránka je prázdná nebo ji nelze přečíst.",
        "de": "Fehler: Zwischenablage ist leer oder konnte nicht gelesen werden.",
        "fr": "Erreur : Le presse-papiers est vide ou n'a pas pu être lu.",
        "it": "Errore: Gli appunti sono vuoti o non è stato possibile leggerli.",
        "ja": "エラー: クリップボードが空であるか、読み取れませんでした。",
        "ko": "오류: 클립보드가 비어 있거나 읽을 수 없습니다.",
        "nl": "Fout: Klembord is leeg of kon niet worden gelezen.",
        "pl": "Błąd: Schowek jest pusty lub nie można go odczytać.",
        "pt": "Erro: A área de transferência está vazia ou não pôde ser lida.",
        "pt_BR": "Erro: A área de transferência está vazia ou não pôde ser lida.",
        "ru": "Ошибка: Буфер обмена пуст или не может быть прочитан.",
        "sv": "Fel: Urklipp är tomt eller kunde inte läsas.",
        "tr": "Hata: Pano boş veya okunamadı.",
        "uk": "Помилка: Буфер обміну порожній або його не вдалося прочитати.",
        "zh_CN": "错误：剪贴板为空或无法读取。",
        "zh_TW": "錯誤：剪貼簿為空或無法讀取。",
    },
    "created_symlinks": {
        "en": "Created {count} symbolic link(s).",
        "es": "Se crearon {count} enlace(s) simbólico(s).",
        "ca": "S'han creat {count} enllaç(os) simbòlic(s).",
        "cs": "Vytvořeno {count} symbolických odkazů.",
        "de": "{count} symbolische Verknüpfung(en) erstellt.",
        "fr": "{count} lien(s) symbolique(s) créé(s).",
        "it": "Creati {count} collegamenti simbolici.",
        "ja": "{count} 個のシンボリックリンクを作成しました。",
        "ko": "{count}개의 심볼릭 링크가 생성되었습니다.",
        "nl": "{count} symbolische link(s) aangemaakt.",
        "pl": "Utworzono {count} dowiązań symbolicznych.",
        "pt": "{count} ligação(ões) simbólica(s) criada(s).",
        "pt_BR": "{count} link(s) simbólico(s) criado(s).",
        "ru": "Создано {count} символических ссылок.",
        "sv": "Skapade {count} symbolisk(a) länk(ar).",
        "tr": "{count} sembolik bağ oluşturuldu.",
        "uk": "Створено {count} символічних посилань.",
        "zh_CN": "已创建 {count} 个符号链接。",
        "zh_TW": "已建立 {count} 個符號連結。",
    },
    "created_symlinks_skipped": {
        "en": "Created {count} symbolic link(s) ({skipped} skipped).",
        "es": "Se crearon {count} enlace(s) simbólico(s) ({skipped} omitidos).",
        "ca": "S'han creat {count} enllaç(os) simbòlic(s) ({skipped} omesos).",
        "cs": "Vytvořeno {count} symbolických odkazů ({skipped} přeskočeno).",
        "de": "{count} symbolische Verknüpfung(en) erstellt ({skipped} übersprungen).",
        "fr": "{count} lien(s) symbolique(s) créé(s) ({skipped} ignoré(s)).",
        "it": "Creati {count} collegamenti simbolici ({skipped} ignorati).",
        "ja": "{count} 個のシンボリックリンクを作成しました ({skipped} 個スキップ)。",
        "ko": "{count}개의 심볼릭 링크가 생성되었습니다 ({skipped}개 건너뜀).",
        "nl": "{count} symbolische link(s) aangemaakt ({skipped} overgeslagen).",
        "pl": "Utworzono {count} dowiązań symbolicznych (pominięto {skipped}).",
        "pt": "{count} ligação(ões) simbólica(s) criada(s) ({skipped} ignorada(s)).",
        "pt_BR": "{count} link(s) simbólico(s) criado(s) ({skipped} ignorado(s)).",
        "ru": "Создано {count} символических ссылок ({skipped} пропущено).",
        "sv": "Skapade {count} symbolisk(a) länk(ar) ({skipped} överhoppade).",
        "tr": "{count} sembolik bağ oluşturuldu ({skipped} atlandı).",
        "uk": "Створено {count} символічних посилань ({skipped} пропущено).",
        "zh_CN": "已创建 {count} 个符号链接（跳过 {skipped} 个）。",
        "zh_TW": "已建立 {count} 個符號連結（略過 {skipped} 個）。",
    },
    "err_same_dir": {
        "en": "Cannot create symlinks in the same folder as the source file(s).",
        "es": "No se pueden crear enlaces simbólicos en la misma carpeta que los archivos de origen.",
        "ca": "No es poden crear enllaços simbòlics a la mateixa carpeta que els fitxers d'origen.",
        "cs": "Symbolické odkazy nelze vytvořit ve stejné složce jako zdrojové soubory.",
        "de": "Symbolische Verknüpfungen können nicht im selben Ordner wie die Quelldatei(en) erstellt werden.",
        "fr": "Impossible de créer des liens symboliques dans le même dossier que le(s) fichier(s) source.",
        "it": "Impossibile creare collegamenti simbolici nella stessa cartella dei file di origine.",
        "ja": "元のファイルと同じフォルダーにシンボリックリンクを作成することはできません。",
        "ko": "원본 파일과 동일한 폴더에 심볼릭 링크를 만들 수 없습니다.",
        "nl": "Kan geen symbolische links maken in dezelfde map als het bronbestand / de bronbestanden.",
        "pl": "Nie można utworzyć dowiązań symbolicznych w tym samym folderze co pliki źródłowe.",
        "pt": "Não é possível criar ligações simbólicas na mesma pasta dos ficheiros de origem.",
        "pt_BR": "Não é possível criar links simbólicos na mesma pasta dos arquivos de origem.",
        "ru": "Невозможно создать символические ссылки в той же папке, где находятся исходные файлы.",
        "sv": "Kan inte skapa symboliska länkar i samma mapp som källfilen/källfilerna.",
        "tr": "Kaynak dosya(lar) ile aynı klasörde sembolik bağlar oluşturulamaz.",
        "uk": "Неможливо створити символічні посилання в тій самій папці, де містяться вихідні файли.",
        "zh_CN": "无法在源文件所在的相同文件夹中创建符号链接。",
        "zh_TW": "無法在與來源檔案相同的資料夾中建立符號連結。",
    },
    "err_exists": {
        "en": "Item(s) already exist in target directory.",
        "es": "El/los elemento(s) ya existen en el directorio de destino.",
        "ca": "Els elements ja existeixen al directori de destinació.",
        "cs": "Položky v cílovém adresáři již existují.",
        "de": "Element(e) existieren bereits im Zielverzeichnis.",
        "fr": "Le(s) élément(s) existe(nt) déjà dans le répertoire cible.",
        "it": "Gli elementi esistono già nella cartella di destinazione.",
        "ja": "対象ディレクトリに項目が既に存在します。",
        "ko": "대상 디렉터리에 항목이 이미 존재합니다.",
        "nl": "Item(s) bestaan al in de doelmap.",
        "pl": "Element(y) już istnieją w katalogu docelowym.",
        "pt": "Os itens já existem no diretório de destino.",
        "pt_BR": "O(s) item(ns) já existe(m) no diretório de destino.",
        "ru": "Элементы уже существуют в целевом каталоге.",
        "sv": "Objektet/objekten finns redan i målkatalogen.",
        "tr": "Öğe(ler) hedef dizinde zaten mevcut.",
        "uk": "Елементи вже існують у цільовому каталозі.",
        "zh_CN": "目标目录中已存在同名项目。",
        "zh_TW": "目標目錄中已存在同名項目。",
    },
    "err_invalid_path": {
        "en": "No valid file paths found on clipboard.",
        "es": "No se encontraron rutas de archivo válidas en el portapapeles.",
        "ca": "No s'han trobat camins de fitxer vàlids al porta-retalls.",
        "cs": "Ve schránce nebyly nalezeny žádné platné cesty k souborům.",
        "de": "Keine gültigen Dateipfade in der Zwischenablage gefunden.",
        "fr": "Aucun chemin de fichier valide trouvé dans le presse-papiers.",
        "it": "Nessun percorso di file valido trovato negli appunti.",
        "ja": "クリップボードに有効なファイルパスが見つかりません。",
        "ko": "클립보드에서 유효한 파일 경로를 찾을 수 없습니다.",
        "nl": "Geen geldige bestandspaden gevonden op het klembord.",
        "pl": "W schowku nie znaleziono prawidłowych ścieżek do plików.",
        "pt": "Nenhum caminho de ficheiro válido encontrado na área de transferência.",
        "pt_BR": "Nenhum caminho de arquivo válido encontrado na área de transferência.",
        "ru": "В буфере обмена не найдено допустимых путей к файлам.",
        "sv": "Inga giltiga filsökvägar hittades i urklipp.",
        "tr": "Panoda geçerli dosya yolu bulunamadı.",
        "uk": "У буфері обміну не знайдено дійсних шляхів до файлів.",
        "zh_CN": "剪贴板中未找到有效的文件路径。",
        "zh_TW": "剪貼簿中未找到有效檔案路徑。",
    },
    "err_not_found": {
        "en": "Source file(s) not found.",
        "es": "Archivo(s) de origen no encontrado(s).",
        "ca": "Fitxer(s) d'origen no trobat(s).",
        "cs": "Zdrojové soubory nebyly nalezeny.",
        "de": "Quelldatei(en) nicht gefunden.",
        "fr": "Fichier(s) source introuvable(s).",
        "it": "File di origine non trovati.",
        "ja": "元のファイルが見つかりません。",
        "ko": "원본 파일을 찾을 수 없습니다.",
        "nl": "Bronbestand(en) niet gevonden.",
        "pl": "Nie znaleziono plików źródłowych.",
        "pt": "Ficheiro(s) de origem não encontrado(s).",
        "pt_BR": "Arquivo(s) de origem não encontrado(s).",
        "ru": "Исходные файлы не найдены.",
        "sv": "Källfil(er) hittades inte.",
        "tr": "Kaynak dosya(lar) bulunamadı.",
        "uk": "Вихідні файли не знайдено.",
        "zh_CN": "未找到源文件。",
        "zh_TW": "找不到來源檔案。",
    },
    "err_failed_skipped": {
        "en": "Failed to create symbolic links ({skipped} skipped).",
        "es": "Error al crear enlaces simbólicos ({skipped} omitidos).",
        "ca": "No s'han pogut crear els enllaços simbòlics ({skipped} omesos).",
        "cs": "Nepodařilo se vytvořit symbolické odkazy ({skipped} přeskočeno).",
        "de": "Fehler beim Erstellen symbolischer Verknüpfungen ({skipped} übersprungen).",
        "fr": "Échec de la création des liens symboliques ({skipped} ignoré(s)).",
        "it": "Impossibile creare collegamenti simbolici ({skipped} ignorati).",
        "ja": "シンボリックリンクの作成に失敗しました ({skipped} 個スキップ)。",
        "ko": "심볼릭 링크 생성 실패 ({skipped}개 건너뜀).",
        "nl": "Kan geen symbolische links maken ({skipped} overgeslagen).",
        "pl": "Nie udało się utworzyć dowiązań symbolicznych (pominięto {skipped}).",
        "pt": "Falha ao criar ligações simbólicas ({skipped} ignorada(s)).",
        "pt_BR": "Falha ao criar links simbólicos ({skipped} ignorado(s)).",
        "ru": "Не удалось создать символические ссылки ({skipped} пропущено).",
        "sv": "Misslyckades med att skapa symboliska länkar ({skipped} överhoppade).",
        "tr": "Sembolik bağlar oluşturulamadı ({skipped} atlandı).",
        "uk": "Не вдалося створити символічні посилання ({skipped} пропущено).",
        "zh_CN": "创建符号链接失败（跳过 {skipped} 个）。",
        "zh_TW": "建立符號連結失敗（略過 {skipped} 個）。",
    },
}

def get_language() -> str:
    """Detects current user language code from environment variables."""
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        if val:
            # Handle multi-language lists like 'es_CL:es:en'
            first = val.split(":")[0].strip()
            # Remove encoding and modifiers, e.g. 'es_CL.UTF-8@euro' -> 'es_CL'
            code = first.split(".")[0].split("@")[0].strip()
            if code and code.lower() not in ("c", "posix"):
                return code
    return "en"

def tr(key: str, lang: str | None = None, **kwargs) -> str:
    """Translates a message key according to the current or specified language."""
    if lang is None:
        lang = get_language()

    lang_clean = lang.replace("-", "_")
    base_lang = lang_clean.split("_")[0].lower()

    translations = TRANSLATIONS.get(key, {})

    # Candidate order:
    # 1. Exact match (e.g. 'pt_BR' or 'zh_CN')
    # 2. Case-insensitive exact match (e.g. 'pt_br')
    # 3. Base language (e.g. 'pt' or 'zh')
    # 4. English fallback ('en')
    # 5. Key itself as fallback
    msg = None
    for candidate in (lang_clean, lang_clean.lower(), base_lang):
        for k, v in translations.items():
            if k.lower() == candidate.lower():
                msg = v
                break
        if msg is not None:
            break

    if msg is None:
        msg = translations.get("en", key)

    if kwargs:
        try:
            return msg.format(**kwargs)
        except Exception:
            return msg
    return msg

def notify(
    message: str,
    title: str | None = None,
    is_error: bool = False,
    icon: str | None = None,
) -> None:
    """Sends a desktop notification using notify-send or kdialog if available."""
    if os.environ.get("PASTEASSYMLINK_NO_NOTIFY"):
        return

    if title is None:
        title = tr("title")

    if icon is None:
        icon = "dialog-error" if is_error else "special_paste-symbolic"

    if shutil.which("notify-send"):
        urgency = "critical" if is_error else "normal"
        try:
            subprocess.run(
                ["notify-send", "-u", urgency, "-a", title, "-i", icon, title, message],
                check=False,
                timeout=3,
            )
        except Exception:
            pass
    elif shutil.which("kdialog"):
        dialog_arg = "--error" if is_error else "--passivepopup"
        try:
            cmd = ["kdialog", "--icon", icon, dialog_arg, message]
            if not is_error:
                cmd.append("3")  # display for 3 seconds
            subprocess.run(cmd, check=False, timeout=3)
        except Exception:
            pass

def get_clipboard() -> tuple[str | None, str | None]:
    """Gets clipboard content from various backends."""
    commands = [
        ['qdbus', 'org.kde.klipper', '/klipper', 'org.kde.klipper.klipper.getClipboardContents'],
        ['wl-paste', '-t', 'text/uri-list'],
        ['wl-paste'],
        ['xclip', '-o', '-selection', 'clipboard', '-t', 'text/uri-list'],
        ['xclip', '-o', '-selection', 'clipboard'],
        ['xsel', '--clipboard', '--output']
    ]

    for command in commands:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, timeout=3, errors="replace"
            )
            output = result.stdout.strip()
            if output:
                return command[0], output
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

    print("Error: Could not get clipboard contents. Please make sure you are running KDE Plasma or have xclip, xsel or wl-paste installed.")
    return (None, None)

def parse_clipboard_items(clipboard_text: str) -> list[str]:
    """Extracts file paths or URIs from clipboard content."""
    if not clipboard_text:
        return []
    if "file://" in clipboard_text:
        return re.findall(r'file://[^\s\r\n]+', clipboard_text)
    return [line.strip() for line in clipboard_text.splitlines() if line.strip()]

def parse_source_path(file_path: str) -> str | None:
    """Parses and normalizes a file path or file:// URI into an absolute path."""
    file_path = file_path.strip()
    if not file_path:
        return None

    if file_path.startswith('file://'):
        parsed_uri = urlparse(file_path)
        source_path = unquote(parsed_uri.path)
    else:
        source_path = file_path

    # Normalize path and strip trailing slashes to prevent empty basename for directories
    source_path = os.path.normpath(source_path)

    if not os.path.isabs(source_path):
        print(f"Skipping (not an absolute path): '{source_path}'")
        return None

    return source_path

class SymlinkResult(tuple):
    """Result tuple of (success_count, error_count) with detailed category stats."""
    def __new__(cls, success_count: int, error_count: int, stats: dict[str, int]):
        return super().__new__(cls, (success_count, error_count))

    def __init__(self, success_count: int, error_count: int, stats: dict[str, int]):
        self.success_count = success_count
        self.error_count = error_count
        self.stats = stats

def create_symlinks(target_directory: str, clipboard_items: list[str]) -> SymlinkResult:
    """Creates symlinks in target_directory for the provided clipboard items."""
    success_count = 0
    error_count = 0
    stats = {
        "same_dir": 0,
        "exists": 0,
        "not_found": 0,
        "invalid_path": 0,
        "other": 0,
    }

    target_dir_real = os.path.realpath(target_directory)

    for raw_item in clipboard_items:
        source_path = parse_source_path(raw_item)
        if not source_path:
            stats["invalid_path"] += 1
            error_count += 1
            continue

        if not os.path.exists(source_path):
            print(f"Skipping (not found): '{source_path}'")
            stats["not_found"] += 1
            error_count += 1
            continue

        link_name = os.path.basename(source_path)
        if not link_name:
            print(f"Skipping (invalid link name): '{source_path}'")
            stats["invalid_path"] += 1
            error_count += 1
            continue

        # Prevent creating a symlink in the exact same directory as the source file
        if os.path.dirname(os.path.realpath(source_path)) == target_dir_real:
            print(f"Skipping (same directory): '{link_name}'")
            stats["same_dir"] += 1
            error_count += 1
            continue

        link_path = os.path.join(target_directory, link_name)

        try:
            os.symlink(source_path, link_path)
            print(f"Link created: {link_name}")
            success_count += 1
        except FileExistsError:
            print(f"Skipping (already exists): '{link_name}'")
            stats["exists"] += 1
            error_count += 1
        except Exception as e:
            print(f"An unexpected error occurred for '{link_name}': {e}")
            stats["other"] += 1
            error_count += 1

    return SymlinkResult(success_count, error_count, stats)

def main() -> None:
    """Creates symbolic links in a target directory based on file paths from the clipboard."""
    # Dolphin passes the file path in the args
    if len(sys.argv) < 2:
        msg = tr("err_no_target")
        print(msg)
        notify(msg, is_error=True)
        sys.exit(1)

    target_directory = sys.argv[1]
    if not os.path.isdir(target_directory):
        msg = tr("err_target_invalid", target=target_directory)
        print(msg)
        notify(msg, is_error=True)
        sys.exit(1)

    command, clipboard_text = get_clipboard()

    if not clipboard_text:
        msg = tr("err_clipboard_empty")
        print(msg)
        notify(msg, is_error=True)
        sys.exit(1)

    clipboard_items = parse_clipboard_items(clipboard_text)
    result = create_symlinks(target_directory, clipboard_items)
    success_count, error_count = result

    print(f"\nOperation complete. {success_count} links created, {error_count} items skipped.")

    if success_count > 0:
        if error_count > 0:
            notify(tr("created_symlinks_skipped", count=success_count, skipped=error_count))
        else:
            notify(tr("created_symlinks", count=success_count))
    elif error_count > 0:
        stats = getattr(result, "stats", {})
        if stats.get("same_dir", 0) > 0 and stats["same_dir"] == error_count:
            notify(tr("err_same_dir"), is_error=True)
        elif stats.get("exists", 0) > 0 and stats["exists"] == error_count:
            notify(tr("err_exists"), is_error=True)
        elif stats.get("invalid_path", 0) > 0 and stats["invalid_path"] == error_count:
            notify(tr("err_invalid_path"), is_error=True)
        elif stats.get("not_found", 0) > 0 and stats["not_found"] == error_count:
            notify(tr("err_not_found"), is_error=True)
        else:
            notify(tr("err_failed_skipped", skipped=error_count), is_error=True)

if __name__ == "__main__":
    main()