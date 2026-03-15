# Fable Text.big Parser

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

Parser i eksporter tekstów z plików `text.big` i `text.bbb` gier **Fable: The Lost Chapters** oraz **Fable Anniversary**.

[English](#english) | [Polski](#polski)

</div>

---

## Polski

### Opis

**Fable Text.big Parser** to narzędzie open-source do wydobywania, przeglądania i eksportowania tekstów z plików `text.big` (Fable: The Lost Chapters) i `text.bbb` (Fable Anniversary). Program umożliwia dostęp do dialogów, opisów przedmiotów, questów i innych tekstów zawartych w grach.

### Funkcje

- 🔍 **Parsowanie formatów BIGB i BBBB** - Pełne wsparcie dla formatów obu wersji gry
  - `text.big` (BIGB) - Fable: The Lost Chapters
  - `text.bbb` (BBBB) - Fable Anniversary
- 🖥️ **Interfejs graficzny** - Przyjazny interfejs GUI oparty na Tkinter
- 📝 **Przeglądanie tekstów** - Hierarchiczna struktura wpisów z podglądem treści
- 🔎 **Wyszukiwanie** - Szybkie przeszukiwanie tekstów według nazwy lub treści
- 💾 **Eksport do wielu formatów**:
  - **JSON** - Pełna struktura danych z metadanymi
  - **TXT** - Proste listy tekstów (ogólne lub tylko dialogi)
  - **CSV** - Format tabelaryczny dla arkuszy kalkulacyjnych
- 🧹 **Czyszczenie danych** - Automatyczne usuwanie błędnych znaków i metadanych
- 🌍 **Wsparcie Unicode** - Poprawna obsługa tekstów UTF-16 LE

### Wymagania

- Python 3.7 lub nowszy
- Biblioteka `tkinter` (zazwyczaj dołączona do Pythona)

### Instalacja

```bash
# Sklonuj repozytorium
git clone https://github.com/TieruYT/Fable-Text.big-Parser.git
cd Fable-Text.big-Parser

# Uruchom GUI
python fable_text_gui.py
```

Lub użyj parsera jako biblioteki:

```python
from fable_text_parser import FableTextBigParser

parser = FableTextBigParser('text.big')
entries = parser.parse()

for entry in entries:
    print(f"Entry: {entry.name}")
    for sub_entry in entry.sub_entries:
        print(f"  - {sub_entry.name}: {sub_entry.content}")
```

### Jak używać

1. **Uruchom program GUI**: `python fable_text_gui.py`
2. **Otwórz plik**: Kliknij "Otwórz plik" i wybierz plik tekstowy z katalogu gry:
   - **The Lost Chapters**: `text.big` (zwykle w `Data\text.big`)
   - **Anniversary**: `text.bbb` (zwykle w `FableData\Build\Data\lang\English\text.bbb`)
3. **Przeglądaj**: Kliknij na wpisy w lewym panelu, aby zobaczyć ich zawartość
4. **Wyszukaj**: Użyj paska wyszukiwania, aby znaleźć konkretne teksty
5. **Eksportuj**: Wybierz format i zapisz dane do pliku

### Struktura plików

**Format BIGB** (Fable: The Lost Chapters - `text.big`):

```
[Header: 16 bajtów]
- Magic: "BIGB" (4 bajty)
- Version: uint32
- Index Offset: uint32
- Entry Count: uint32

[Index Table]
- Type ID: uint32
- Name: null-terminated string
- Text ID: uint32
- Offset: uint32
- Size: uint32
- Unknown: uint32

[Data Sections]
- Sub-entries w formacie UTF-16 LE
- Struktura: [Content][Padding][Name Length][Name][Padding]
```

**Format BBBB** (Fable Anniversary - `text.bbb`):

```
[Header: 28 bajtów]
- Magic: "BBBB" (4 bajty)
- Unknown1: uint32
- Unknown2: uint32 (prawdopodobnie Entry Count)
- Unknown3: uint32
- Unknown4: uint32
- Offset1: uint32 (prawdopodobnie Index Offset)
- Offset2: uint32

[Data Sections]
- Podobna struktura do BIGB
- Sub-entries w formacie UTF-16 LE
```

### Przykłady eksportu

**Tylko dialogi** (oczyszczone):
```bash
Menu > Plik > Eksportuj TYLKO DIALOGI do TXT
```

**Wszystkie teksty**:
```bash
Menu > Plik > Eksportuj wszystko do JSON/TXT/CSV
```

### Znane ograniczenia

- Niektóre wpisy mogą zawierać błędne znaki z powodu nieudokumentowanego formatu
- Parser automatycznie czyści większość artefaktów, ale niektóre mogą pozostać
- Format `text.big` nie jest oficjalnie udokumentowany przez twórców gry

### Autor

Dawid Saworski

### Licencja

Ten projekt jest udostępniony na licencji MIT. Zobacz plik `LICENSE` dla szczegółów.

---

## English

### Description

**Fable Text.big Parser** is an open-source tool for extracting, viewing, and exporting texts from `text.big` (Fable: The Lost Chapters) and `text.bbb` (Fable Anniversary) files. The program provides access to dialogues, item descriptions, quests, and other in-game texts from both versions of the game.

### Features

- 🔍 **BIGB and BBBB Format Parsing** - Full support for both game versions
  - `text.big` (BIGB) - Fable: The Lost Chapters
  - `text.bbb` (BBBB) - Fable Anniversary
- 🖥️ **Graphical Interface** - User-friendly Tkinter-based GUI
- 📝 **Text Browsing** - Hierarchical entry structure with content preview
- 🔎 **Search** - Fast text search by name or content
- 💾 **Multi-format Export**:
  - **JSON** - Complete data structure with metadata
  - **TXT** - Simple text lists (all entries or dialogues only)
  - **CSV** - Tabular format for spreadsheets
- 🧹 **Data Cleaning** - Automatic removal of malformed characters and metadata
- 🌍 **Unicode Support** - Proper handling of UTF-16 LE texts

### Requirements

- Python 3.7 or newer
- `tkinter` library (usually included with Python)

### Installation

```bash
# Clone the repository
git clone https://github.com/TieruYT/Fable-Text.big-Parser.git
cd Fable-Text.big-Parser

# Run the GUI
python fable_text_gui.py
```

Or use the parser as a library:

```python
from fable_text_parser import FableTextBigParser

parser = FableTextBigParser('text.big')
entries = parser.parse()

for entry in entries:
    print(f"Entry: {entry.name}")
    for sub_entry in entry.sub_entries:
        print(f"  - {sub_entry.name}: {sub_entry.content}")
```

### Usage

1. **Launch GUI**: `python fable_text_gui.py`
2. **Open File**: Click "Open File" and select the text file from your game directory:
   - **The Lost Chapters**: `text.big` (usually in `Data\text.big`)
   - **Anniversary**: `text.bbb` (usually in `FableData\Build\Data\lang\English\text.bbb`)
3. **Browse**: Click entries in the left panel to view their contents
4. **Search**: Use the search bar to find specific texts
5. **Export**: Choose a format and save data to file

### File Structure

**BIGB Format** (Fable: The Lost Chapters - `text.big`):

```
[Header: 16 bytes]
- Magic: "BIGB" (4 bytes)
- Version: uint32
- Index Offset: uint32
- Entry Count: uint32

[Index Table]
- Type ID: uint32
- Name: null-terminated string
- Text ID: uint32
- Offset: uint32
- Size: uint32
- Unknown: uint32

[Data Sections]
- Sub-entries in UTF-16 LE format
- Structure: [Content][Padding][Name Length][Name][Padding]
```

**BBBB Format** (Fable Anniversary - `text.bbb`):

```
[Header: 28 bytes]
- Magic: "BBBB" (4 bytes)
- Unknown1: uint32
- Unknown2: uint32 (likely Entry Count)
- Unknown3: uint32
- Unknown4: uint32
- Offset1: uint32 (likely Index Offset)
- Offset2: uint32

[Data Sections]
- Similar structure to BIGB
- Sub-entries in UTF-16 LE format
```

### Export Examples

**Dialogues only** (cleaned):
```bash
Menu > File > Export DIALOGUES ONLY to TXT
```

**All texts**:
```bash
Menu > File > Export all to JSON/TXT/CSV
```

### Known Limitations

- Some entries may contain malformed characters due to undocumented format
- Parser automatically cleans most artifacts, but some may remain
- The `text.big` format is not officially documented by the game developers

### Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

### Author

Dawid Saworski

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Game Information

**Fable: The Lost Chapters**
- Developer: Lionhead Studios
- Publisher: Microsoft Game Studios
- Year: 2005

**Fable Anniversary**
- Developer: Lionhead Studios
- Publisher: Microsoft Studios
- Year: 2014

This tool is an unofficial fan-made project and is not affiliated with or endorsed by Lionhead Studios or Microsoft.

---

<div align="center">

Made with ❤️ for the Fable community

</div>
