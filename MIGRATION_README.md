# Migracja Polskiego Spolszczenia Fable TLC → Anniversary

## 📋 Podsumowanie Projektu

Projekt ma na celu przeniesienie polskiego spolszczenia z **Fable: The Lost Chapters** do **Fable Anniversary**.

## 🔍 Analiza Wykonana

### 1. Struktura Plików

**Fable: The Lost Chapters (`text.big`)**
- Format: BIGB (16-bajtowy nagłówek)
- Nazwy tekstowe: `TEXT_GUI_*`, `TXT_OBJT_*`, `ScriptDialogue.lug` itp.
- Kodowanie: UTF-16 LE
- Rozmiar: ~6.7 MB
- **Zawartość**: Częściowo spolszczony (41% polskich tekstów = 2808 wpisów)

**Fable Anniversary (`text.bbb`)**
- Format: BBBB (28-bajtowy nagłówek)
- Nazwy: Hashe w formacie `0xEDA40F00` (zamiast nazw tekstowych!)
- Plik indeksowy: `text.ipbe` (1.3 MB) - mapuje hashe na offsety
- Kodowanie: UTF-16 LE
- Rozmiar: ~6.6 MB
- **Zawartość**: Tylko angielskie teksty

### 2. Kluczowy Problem

**Anniversary używa hashów zamiast nazw tekstowych!**

```
TLC:        TEXT_OBJECT_SWORD → "Miecz"
Anniversary: 0x12AB34CD        → "Sword"
```

Brak bezpośredniego mapowania nazwa → hash.

## 📊 Co Udało Się Zrobić

✅ **Wyeksportowano polskie teksty z TLC**
- Plik: `polish_tlc_export.json`
- Zawiera: 2808 polskich tekstów + 4047 angielskich
- Format JSON z nazwami TLC jako klucze

✅ **Stworzono narzędzia parsujące**
- `fable_text_parser.py` - parser dla BIGB i BBBB
- `fable_anniversary_parser.py` - parser z obsługą plików indeksowych `.ipbe`
- `export_polish_tlc.py` - eksporter polskich tekstów

✅ **Zbadano formaty plików**
- Udokumentowano strukturę BIGB i BBBB
- Zidentyfikowano pliki indeksowe Anniversary

## ❌ Problem Do Rozwiązania

**Nie udało się odkryć algorytmu hashowania nazwa→hash**

Próbowano:
- CRC32
- FNV-1a
- Simple sum
- Różne warianty nazw (uppercase, lowercase, bez prefiksów)

**Wynik:** Żaden nie pasuje. Anniversary prawdopodobnie używa custom algorytmu hashowania lub hashe nie bazują na nazwach TLC.

## 🎯 Możliwe Rozwiązania

### Rozwiązanie 1: Mapowanie Po Zawartości (ZALECANE)

Skoro mamy angielskie teksty w obu wersjach:

```
1. Wyeksportuj WSZYSTKIE teksty z Anniversary (angielskie)
2. Dla każdego angielskiego tekstu TLC:
   - Znajdź identyczny tekst w Anniversary
   - Zapisz mapowanie: nazwa_TLC → hash_Anniversary → polski_tekst
3. Stwórz nowy text.bbb z polskimi tekstami
```

**Problem:** Parsowanie Anniversary trwa bardzo długo (6.6 MB).

**Rozwiązanie:** Użyć szybszego algorytmu lub parsować w częściach.

### Rozwiązanie 2: Reverse Engineering (ZAAWANSOWANE)

Użyć **Fable Explorer** lub **hex editor**:

1. Pobierz Fable Explorer: `mediafire.com/file/4591h0sn7b6ip2a/FableExplorer_2020-30-14.zip`
2. Otwórz `text.bbb` w programie
3. Ręcznie podmień teksty angielskie na polskie

**Wady:**
- Czasochłonne (13975 wpisów w indeksie!)
- Wymaga ręcznej pracy

### Rozwiązanie 3: Odkrycie Algorytmu Hashowania

Należałoby:
1. Zdekompilować biblioteki gry (DLL)
2. Znaleźć funkcję hashującą nazwy
3. Replikować ją w Pythonie

**Wady:**
- Bardzo zaawansowane
- Może naruszać licencję
- Czasochłonne

## 📁 Wygenerowane Pliki

```
Programy/Fable-Text.big-Parser/
├── polish_tlc_export.json       # 2808 polskich tekstów (695 KB)
├── polish_tlc_export.txt        # Przykłady (8.5 KB)
├── fable_text_parser.py         # Parser BIGB/BBBB
├── fable_anniversary_parser.py  # Parser z .ipbe
├── export_polish_tlc.py         # Eksporter PL tekstów
├── migration_tool.py            # Narzędzie migracji (WIP)
├── hash_discovery.py            # Odkrywanie hashy (nieudane)
└── MIGRATION_README.md          # Ta dokumentacja
```

## 🚀 Następne Kroki

### Opcja A: Kontynuacja Automatyczna

Jeśli chcesz kontynuować automatyczną migrację:

1. **Zoptymalizuj parser Anniversary**
   - Przyspiesz parsowanie dużego pliku BBB
   - Użyj wielowątkowości

2. **Stwórz mapowanie po zawartości**
   ```python
   python migration_tool.py
   ```

3. **Wygeneruj polski text.bbb**
   - Użyj struktury Anniversary
   - Podmień angielskie teksty na polskie
   - Przepakuj do formatu BBB

### Opcja B: Ręczna Edycja

1. Pobierz **Fable Explorer**
2. Otwórz `text.bbb`
3. Użyj `polish_tlc_export.json` jako referencji
4. Ręcznie podmień teksty

### Opcja C: Community Help

Zapytaj na forach modderskich:
- Steam Community - Fable Anniversary Modding
- Fable Community Forums
- Reddit r/Fable

Ktoś mógł już odkryć algorytm hashowania lub mieć narzędzia.

## 💡 Rekomendacje

**Najlepsze podejście:**

1. Spróbuj najpierw znaleźć gotowe narzędzie lub community mod tool
2. Jeśli nie ma → użyj **Opcji A** (mapowanie po zawartości)
3. W ostateczności → **Opcja B** (ręczna edycja w Fable Explorer)

## 📞 Dalsze Pytania

- Czy Anniversary ma identyczne teksty jak TLC?
- Czy można podmienić cały plik `text.bbb`?
- Czy gra weryfikuje checksumę plików?

---

## 🎮 Rezultat

Jeśli uda się stworzyć polski `text.bbb`, **będziesz pierwszą osobą która stworzy polskie spolszczenie dla Fable Anniversary!** 🎉

To niszowy projekt, ale społeczność Fable z pewnością doceni Twój wkład.

---

**Autor narzędzi:** Claude Code (Anthropic)
**Data:** 2025-11-13
**Projekt:** Dawid Saworski
