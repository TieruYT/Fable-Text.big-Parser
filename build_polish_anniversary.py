# -*- coding: utf-8 -*-
"""
Buduje polski text.bbb dla Fable Anniversary
Używa oryginalnego Anniversary + polskie mapowanie
"""

import json
import struct
import os
from fable_text_parser import FableTextBigParser


def normalize_text(text):
    """Normalizuje tekst do porównywania"""
    return ' '.join(text.split()).lower().strip().rstrip('.,!?;:')


def build_polish_anniversary():
    """Buduje polski text.bbb"""

    print("="*60)
    print("BUDOWANIE POLSKIEGO FABLE ANNIVERSARY")
    print("="*60)

    # 1. Załaduj mapowanie
    print("\n[1/4] Ładowanie mapowania...")

    with open('final_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Stwórz indeks: znormalizowany angielski -> polski
    eng_to_pol = {}

    for item in mapping:
        normalized = normalize_text(item['anniversary_english'])
        if normalized:
            eng_to_pol[normalized] = item['polish']

    print(f"   Mapowanie: {len(eng_to_pol)} par")

    polish_count = sum(1 for m in mapping if m['has_polish'])
    print(f"   Polskie: {polish_count}")
    print(f"   Angielskie: {len(mapping) - polish_count}")

    # 2. Parsuj oryginalny Anniversary
    print("\n[2/4] Parsowanie oryginalnego Anniversary text.bbb...")

    ann_file = "English/text.bbb"

    if not os.path.exists(ann_file):
        print(f"BŁĄD: Nie znaleziono {ann_file}")
        print("Upewnij się że katalog 'English' zawiera text.bbb")
        return

    parser = FableTextBigParser(ann_file)
    entries = parser.parse()

    total_subs = sum(len(entry.sub_entries) for entry in entries)
    print(f"   Wpisy: {len(entries)}")
    print(f"   Sub-wpisy: {total_subs}")

    # 3. Podmień teksty na polskie
    print("\n[3/4] Podmiana tekstów na polskie...")

    replaced_count = 0
    kept_english = 0

    for entry in entries:
        for sub in entry.sub_entries:
            normalized = normalize_text(sub.content)

            if normalized in eng_to_pol:
                # Mamy polskie tłumaczenie!
                sub.content = eng_to_pol[normalized]
                replaced_count += 1
            else:
                # Brak polskiego - zostaw angielski
                kept_english += 1

    print(f"   Zamieniono na polski: {replaced_count}")
    print(f"   Pozostało po angielsku: {kept_english}")
    print(f"   Procent polskiego: {replaced_count/(replaced_count+kept_english)*100:.1f}%")

    # 4. Zapisz nowy plik BBB
    print("\n[4/4] Zapisywanie polish_text.bbb...")

    output_file = "polish_text.bbb"

    # Nagłówek BBBB (28 bajtów)
    with open(output_file, 'wb') as f:
        # Magic
        f.write(b'BBBB')

        # Unknown values - skopiuj z oryginału
        with open(ann_file, 'rb') as orig:
            orig.seek(4)  # Pomiń magic
            unknown_data = orig.read(24)  # Reszta nagłówka
            f.write(unknown_data)

        # Dane tekstowe
        # Separator
        f.write(b'\x00\x00')

        # Zapisz wszystkie sub-entries
        for entry in entries:
            for sub in entry.sub_entries:
                # Treść UTF-16 LE
                content_bytes = sub.content.encode('utf-16-le') + b'\x00\x00'
                f.write(content_bytes)

                # Padding do 4 bajtów
                while f.tell() % 4 != 0:
                    f.write(b'\x00')

                # Długość nazwy
                name_bytes = sub.name.encode('ascii', errors='ignore') + b'\x00'
                name_length = len(name_bytes)
                f.write(struct.pack('<I', name_length))

                # Nazwa
                f.write(name_bytes)

                # Padding
                while f.tell() % 4 != 0:
                    f.write(b'\x00')

    file_size = os.path.getsize(output_file)
    print(f"   Zapisano: {output_file} ({file_size / 1024 / 1024:.2f} MB)")

    # Weryfikacja - spróbuj odczytać
    print("\n[WERYFIKACJA] Sprawdzanie polish_text.bbb...")

    try:
        verify_parser = FableTextBigParser(output_file)
        verify_entries = verify_parser.parse()

        verify_total = sum(len(e.sub_entries) for e in verify_entries)

        print(f"   ✓ Plik BBB odczytany poprawnie")
        print(f"   ✓ Znaleziono {verify_total} sub-wpisów")

        # Pokaż przykłady
        print("\n   Przykłady polskich tekstów:")
        count = 0
        for entry in verify_entries[:1]:
            for sub in entry.sub_entries:
                if any(c in sub.content for c in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'):
                    print(f"     - {sub.content[:80]}")
                    count += 1
                    if count >= 5:
                        break

    except Exception as e:
        print(f"   ✗ BŁĄD weryfikacji: {e}")

    return output_file


def main():
    """Główna funkcja"""

    output = build_polish_anniversary()

    if output:
        print("\n" + "="*60)
        print("SUKCES!")
        print("="*60)
        print(f"\nWygenerowano: {output}")
        print("\nKOLEJNE KROKI:")
        print("1. Backup oryginalnych plików:")
        print("   cd 'C:\\Program Files (x86)\\Fable Anniversary\\WellingtonGame\\FableData\\Build\\Data\\lang\\English'")
        print("   copy text.bbb text.bbb.backup")
        print("")
        print("2. Skopiuj polish_text.bbb do katalogu gry jako text.bbb")
        print("")
        print("3. Uruchom grę i sprawdź!")
        print("="*60)


if __name__ == '__main__':
    main()
