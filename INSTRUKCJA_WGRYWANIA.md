# Jak Wgrać Polskie Teksty do Fable Anniversary

## 🎯 Problem

Mamy przetłumaczone teksty, ale są w formacie **BBBB** który jest:
- Binarny (nie zwykły tekst)
- Skompresowany/zapakowany
- Ma strukturę z hashami i offsetami
- Gra wymaga konkretnego formatu

## 📋 Opcje Wgrywania

### **Opcja 1: Przepakowanie text.bbb (NAJLEPSZE)**

Napiszemy skrypt Python który:

1. **Odczyta strukturę** oryginalnego `text.bbb` z Anniversary
2. **Podmieni** angielskie teksty na polskie (używając naszego mapowania)
3. **Przepakuje** z powrotem do formatu BBBB
4. **Zachowa** wszystkie offsety, hashe i strukturę

**Plusy:**
- Pełna kontrola nad procesem
- Działa automatycznie
- Można wielokrotnie modyfikować

**Minusy:**
- Trzeba dokładnie zrozumieć format BBBB
- Ryzyko błędów w strukturze

**Status:** Możliwe do zrobienia! Już mamy parser, więc możemy zrobić writer.

---

### **Opcja 2: Fable Explorer (RĘCZNE)**

Użycie narzędzia **Fable Explorer** do ręcznej edycji.

**Kroki:**
1. Pobierz Fable Explorer: `mediafire.com/file/4591h0sn7b6ip2a/FableExplorer_2020-30-14.zip`
2. Otwórz `text.bbb`
3. Ręcznie wklej polskie teksty używając naszego mapowania jako referencji

**Plusy:**
- Wizualne narzędzie
- Bezpieczniejsze (mniej ryzyko zepsucia pliku)

**Minusy:**
- Bardzo czasochłonne (10,000+ tekstów!)
- Monotonne
- Podatne na błędy ludzkie

**Status:** Rezerwa jeśli Opcja 1 zawiedzie

---

### **Opcja 3: Modyfikacja w Pamięci (ZAAWANSOWANE)**

Użycie CheatEngine lub podobnych narzędzi do podmiany tekstów w pamięci gry podczas działania.

**Plusy:**
- Nie modyfikuje plików gry
- Można testować na żywo

**Minusy:**
- Tymczasowe (tylko podczas sesji)
- Bardzo zaawansowane
- Trzeba za każdym razem włączać

**Status:** Nie polecane dla permanentnego spolszczenia

---

## 🛠️ Nasza Strategia: Opcja 1

Stworzymy **BBBB Writer** który przepakuje text.bbb:

### Struktura Pliku BBBB

```
[Nagłówek BBBB - 28 bajtów]
- Magic: "BBBB" (4 bajty)
- Unknown1-4: uint32 (16 bajtów)
- Offset1: uint32 (4 bajty) - wskaźnik na dane
- Offset2: uint32 (4 bajty)

[Dane Tekstowe]
- Sub-entries w formacie UTF-16 LE
- Każdy tekst: [Content][Padding][Name Length][Name][Padding]

[Plik Indeksowy - text.ipbe]
- Hash ID → Offset w pliku BBB
- 13,975 wpisów
```

### Plan Implementacji

**Krok 1: Parser** ✅ GOTOWE
- Mamy już `fable_text_parser.py`
- Potrafi odczytać BBBB

**Krok 2: Mapowanie** 🔄 W TRAKCIE
- Po otrzymaniu angielskiego text.big
- Stworzymy mapowanie angielski → polski

**Krok 3: Writer** 📝 DO ZROBIENIA
- Napiszemy `fable_bbb_writer.py`
- Odtworzy strukturę BBBB z polskimi tekstami

**Krok 4: Rebuild Index** 📝 DO ZROBIENIA
- Przebudujemy `text.ipbe` z nowymi offsetami
- Zachowamy oryginalne hashe

**Krok 5: Backup & Test** 🧪 DO ZROBIENIA
- Backup oryginalnych plików
- Podmiana i test w grze

---

## 📝 Pseudo-kod BBBB Writer

```python
class FableBBBWriter:
    def __init__(self, template_bbb, translation_mapping):
        # Odczytaj strukturę z oryginalnego BBB
        self.template = parse_bbb(template_bbb)
        self.mapping = translation_mapping

    def replace_texts(self):
        # Dla każdego tekstu w template
        for entry in self.template.entries:
            # Znajdź polski odpowiednik
            if entry.english in self.mapping:
                entry.content = self.mapping[entry.english]['polish']

    def rebuild_bbb(self, output_file):
        # Nagłówek BBBB
        write_header()

        # Dla każdego sub-entry
        for entry in entries:
            # Zapisz w formacie UTF-16 LE
            write_utf16_string(entry.content)
            write_padding()
            write_name_length()
            write_name()
            write_padding()

    def rebuild_index(self, output_ipbe):
        # Dla każdego hash
        for hash_id, entry in index_map:
            # Przelicz nowy offset po podmianie tekstów
            new_offset = calculate_offset(entry)
            write_index_entry(hash_id, new_offset)
```

---

## ⚠️ Potencjalne Problemy

### 1. **Różna Długość Tekstów**

Polski tekst może być:
- Dłuższy niż angielski → offsety się zmieniają
- Krótszy → trzeba paddingu

**Rozwiązanie:**
- Przebudujemy wszystkie offsety od nowa
- Zachowamy padding alignment (2 bajty dla UTF-16)

### 2. **Polskie Znaki**

Polski ma znaki: ą, ć, ę, ł, ń, ó, ś, ź, ż

**Rozwiązanie:**
- UTF-16 LE obsługuje wszystkie znaki Unicode
- Format BBB używa UTF-16 LE ✅

### 3. **Checksuma / Weryfikacja**

Gra może sprawdzać:
- CRC plików
- Rozmiar pliku
- Wersję

**Rozwiązanie:**
- Test w grze - jeśli nie działa, trzeba zbadać czy są checksummy
- Możliwe że gra nie weryfikuje (wiele gier nie robi tego)

---

## 🎮 Procedura Wgrywania

### 1. **Backup**
```bash
cd "C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English"

# Kopia zapasowa
copy text.bbb text.bbb.backup
copy text.ipbe text.ipbe.backup
copy text.iple text.iple.backup
```

### 2. **Podmiana**
```bash
# Nasz plik polski
copy "C:\...\polish_text.bbb" text.bbb
copy "C:\...\polish_text.ipbe" text.ipbe
```

### 3. **Test**
- Uruchom grę
- Sprawdź czy:
  - Gra się uruchamia ✅
  - Teksty są po polsku ✅
  - Nie ma crashy ✅
  - Wszystkie dialogi działają ✅

### 4. **Rollback (jeśli coś pójdzie nie tak)**
```bash
copy text.bbb.backup text.bbb
copy text.ipbe.backup text.ipbe
```

---

## 📊 Timeline

1. ⏳ **Czekamy na angielski text.big** - w trakcie
2. 🔄 **Stworzenie mapowania** - 30 min po otrzymaniu pliku
3. 💻 **Napisanie BBBB Writer** - 2-3 godziny
4. 🧪 **Pierwszy test** - 30 min
5. 🐛 **Debug i poprawki** - 1-2 godziny (jeśli potrzebne)
6. ✅ **Gotowe spolszczenie** - tego samego dnia!

---

## 🎉 Po Wszystkim

Gdy wszystko zadziała:
- Podzielimy się na forum Fable
- Pierwszy polski mod dla Anniversary!
- Społeczność będzie zachwycona 🇵🇱

---

**Autor:** Claude Code + Dawid Saworski
**Data:** 2025-11-13
