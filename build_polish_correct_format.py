# -*- coding: utf-8 -*-
"""
POPRAWNA wersja - zamienia TYLKO treści UTF-16, nie nazwy ASCII!
"""

import json
import struct


def normalize_text(text):
    """Normalizuje tekst"""
    return ' '.join(text.split()).lower().strip().rstrip('.,!?;:')


def find_and_replace_content_only(data, replacements):
    """Zamienia TYLKO treści UTF-16, pomija nazwy ASCII"""

    print("Zamiana TYLKO treści (nie nazw)...")

    data = bytearray(data)
    replaced_count = 0

    # Sortuj od najdłuższych
    sorted_repl = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for eng_text, pol_text in sorted_repl:
        eng_bytes = eng_text.encode('utf-16-le')
        pol_bytes = pol_text.encode('utf-16-le')

        pos = 0
        while True:
            pos = data.find(eng_bytes, pos)

            if pos == -1:
                break

            # Sprawdź czy to jest faktycznie treść UTF-16 (nie nazwa ASCII)
            # UTF-16 powinno mieć co drugi bajt jako 0x00
            is_utf16 = True

            # Sprawdź pierwsze 6 bajtów
            for i in range(0, min(6, len(eng_bytes)), 2):
                if i+1 < len(eng_bytes):
                    # W UTF-16 LE dla ASCII, drugi bajt powinien być 0x00
                    if eng_bytes[i+1] != 0x00:
                        is_utf16 = False
                        break

            if is_utf16:
                # Sprawdź czy po tekście jest null terminator UTF-16
                if pos + len(eng_bytes) + 1 < len(data):
                    next_bytes = data[pos + len(eng_bytes):pos + len(eng_bytes) + 2]

                    if next_bytes == b'\x00\x00':
                        # To jest poprawny string UTF-16!

                        # Zachowaj długość
                        target_len = len(eng_bytes)

                        if len(pol_bytes) < target_len:
                            # Dodaj spacje
                            missing_chars = (target_len - len(pol_bytes)) // 2
                            pol_text_padded = pol_text + (' ' * missing_chars)
                            pol_bytes = pol_text_padded.encode('utf-16-le')

                        elif len(pol_bytes) > target_len:
                            # Obetnij
                            chars_fit = target_len // 2
                            pol_text_cut = pol_text[:chars_fit]
                            pol_bytes = pol_text_cut.encode('utf-16-le')

                        # Zamień
                        data[pos:pos + target_len] = pol_bytes[:target_len]
                        replaced_count += 1

            pos += 1

        if replaced_count % 100 == 0 and replaced_count > 0:
            print(f"  Zamieniono: {replaced_count}", flush=True)

    print(f"\nŁącznie zamieniono: {replaced_count} tekstów")

    return bytes(data)


def main():
    """Główna funkcja"""

    print("="*60)
    print("BUDOWANIE Z POPRAWNYM FORMATEM")
    print("Zamienia TYLKO treści UTF-16, nie nazwy ASCII")
    print("="*60)

    # Załaduj mapowanie
    print("\n[1/3] Ładowanie mapowania...")

    with open('final_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    replacements = {}

    for item in mapping:
        eng = item['anniversary_english']
        pol = item['polish']

        if item['has_polish'] and eng != pol:
            replacements[eng] = pol

    print(f"  Przygotowano {len(replacements)} zamian")

    # Wczytaj oryginalny
    print("\n[2/3] Wczytywanie Anniversary...")

    with open('English/text.bbb', 'rb') as f:
        data = f.read()

    print(f"  Rozmiar: {len(data) / 1024 / 1024:.2f} MB")

    # Zamień
    print("\n[3/3] Podmiana treści...")

    new_data = find_and_replace_content_only(data, replacements)

    # Zapisz
    output_file = "polish_text_FIXED.bbb"

    with open(output_file, 'wb') as f:
        f.write(new_data)

    print(f"\nZapisano: {output_file}")
    print(f"Rozmiar: {len(new_data) / 1024 / 1024:.2f} MB")

    print("\n" + "="*60)
    print("GOTOWE!")
    print("="*60)
    print(f"\nPlik: {output_file}")
    print("\nTa wersja:")
    print("✓ Zachowuje nazwy ASCII (TEXT_GUI_*)")
    print("✓ Zamienia treści na polskie")
    print("✓ Gra powinna wyświetlać polskie teksty!")
    print("="*60)


if __name__ == '__main__':
    main()
