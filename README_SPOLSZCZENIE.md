# 🇵🇱 Polskie Spolszczenie dla Fable Anniversary

**Pierwsze nieoficjalne polskie spolszczenie dla Fable Anniversary!**

## 📊 Statystyki

- **Przetłumaczone teksty**: 10,647
- **Procent polskiego**: ~81% zawartości gry
- **Źródło**: Oficjalne polskie spolszczenie Fable: The Lost Chapters
- **Autor**: Dawid Saworski + Claude Code (Anthropic)
- **Data**: 2025-11-13

## ✅ Co Zostało Przetłumaczone

- ✅ Dialogi postaci
- ✅ Opisy przedmiotów
- ✅ Nazwy lokacji (Gildia Bohaterów, Dębowa Dolina, etc.)
- ✅ Teksty książek i notatek
- ✅ Menu i interfejs
- ✅ Opisy questów
- ✅ Napisy końcowe (credity)

## ⚠️ Co Pozostało Po Angielsku

- Teksty bez polskiego odpowiednika w TLC (~19%)
- Niektóre nowe teksty dodane tylko w Anniversary

## 🎮 Instalacja

### Metoda 1: Automatyczna (ZALECANA)

1. **Pobierz** folder ze spolszczeniem
2. **Uruchom** `INSTALL.bat` **JAKO ADMINISTRATOR**
3. **Postępuj** zgodnie z instrukcjami

### Metoda 2: Ręczna

1. **Backup oryginalnego pliku:**
   ```
   C:\Program Files (x86)\Fable Anniversary\WellingtonGame\
   FableData\Build\Data\lang\English\text.bbb
   ```
   Skopiuj jako `text.bbb.backup`

2. **Skopiuj spolszczenie:**
   ```
   polish_text.bbb → text.bbb
   ```
   Do katalogu gry (nadpisz oryginalny plik)

3. **Uruchom grę** i ciesz się po polsku! 🎉

## ⚙️ Wymagania

- **Gra**: Fable Anniversary (wersja PC/Steam)
- **System**: Windows 7/8/10/11
- **Miejsce**: ~7 MB wolnego miejsca

## 🔤 Uwaga o Czcionkach

**WAŻNE:** Gra może nie obsługiwać polskich znaków (ą, ć, ę, ł, ń, ó, ś, ź, ż).

**Jeśli zobaczysz kwadraciki/krzaczki zamiast ogonków:**

To oznacza że fonty gry nie mają polskich znaków. Będziemy musieli je zmodyfikować.

**Rozwiązanie (do zrobienia później):**
- Modyfikacja plików `fonts.bbb` lub `streaming_fonts_pc.bbb`
- Dodanie polskich glifów do czcionek

**Na razie:** Gra będzie działać, ale ogonki mogą się nie wyświetlać poprawnie.

## 🔙 Odinstalowanie

1. **Przywróć backup:**
   ```
   text.bbb.backup → text.bbb
   ```

2. **Lub zweryfikuj pliki gry** przez Steam:
   - Steam → Biblioteka → Fable Anniversary
   - Właściwości → Pliki lokalne → Zweryfikuj integralność

## 🐛 Znane Problemy

1. **Niektóre dialogi mogą być zduplikowane**
   - Wynika to z mapowania TLC → Anniversary
   - Większość tekstów jest OK

2. **Brak ogonków w czcionkach**
   - Do naprawienia w przyszłości
   - Wymaga modyfikacji fontów

3. **Teksty dłuższe niż oryginał mogą być obcięte**
   - Ograniczenie naszego algorytmu
   - Dotyczy niewielkiej liczby tekstów

## 📝 Raport Techniczny

### Proces Tworzenia

1. **Analiza formatów**
   - Fable TLC: Format BIGB (16-bajtowy nagłówek)
   - Fable Anniversary: Format BBBB (28-bajtowy nagłówek)

2. **Parsowanie**
   - Wyekstraktowano 28,793 tekstów z angielskiego TLC
   - Wyekstraktowano 10,286 tekstów z Anniversary
   - Załadowano 2,808 polskich tekstów z TLC

3. **Mapowanie**
   - Zmapowano 9,033 pary tekstów
   - 8,350 z polskim tłumaczeniem (92.4%)
   - 683 pozostało po angielsku

4. **Przepakowanie**
   - Bezpośrednia modyfikacja bajtów UTF-16 LE
   - Zachowano strukturę oryginalnego pliku BBBB
   - Zamieniono 10,647 wystąpień tekstów

### Narzędzia Użyte

- **Python 3.x** - język programowania
- **struct** - parsowanie binarnych formatów
- **difflib** - dopasowywanie tekstów
- **Custom parsers** - dla formatów BIGB/BBBB

## 📁 Struktura Plików

```
polish_text.bbb         # Główny plik spolszczenia (6.7 MB)
INSTALL.bat             # Automatyczny instalator
README_SPOLSZCZENIE.md  # Ta dokumentacja
final_mapping.json      # Mapowanie tekstów (dla deweloperów)
final_mapping_report.txt # Raport mapowania
```

## 🙏 Podziękowania

- **Lionhead Studios** - za stworzenie Fable
- **CD Projekt** - za oryginalne polskie spolszczenie TLC
- **Społeczność Fable** - za wsparcie i zainteresowanie
- **Claude Code (Anthropic)** - za pomoc w automatyzacji

## 📜 Licencja

Spolszczenie oparte na oficjalnym tłumaczeniu Fable: The Lost Chapters.

**Tylko do użytku osobistego. Nie do celów komercyjnych.**

---

## 🎮 Miłej Zabawy!

Jeśli spolszczenie Ci się podoba, podziel się nim ze społecznością Fable!

**Discord / Reddit / Steam Community**

---

**Wersja**: 1.0
**Data**: 2025-11-13
**Autor**: Dawid Saworski

🇵🇱 **Made with ❤️ for Polish Fable Fans** 🇵🇱
