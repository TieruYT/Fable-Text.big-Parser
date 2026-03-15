# -*- coding: utf-8 -*-
"""
Buduje polski BBB z DOKŁADNIE tymi samymi długościami tekstów
Padding/obcinanie aby offsety pozostały identyczne
"""

import json
import os


def normalize_text(text):
    """Normalizuje tekst"""
    return ' '.join(text.split()).lower().strip().rstrip('.,!?;:')


def build_exact_length():
    """Buduje z zachowaniem dokładnych długości"""

    print("="*60)
    print("BUDOWANIE Z DOKŁADNYMI DŁUGOŚCIAMI")
    print("="*60)

    # 1. Załaduj mapowanie
    print("\n[1/3] Ładowanie mapowania...")

    with open('final_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    replacements = {}

    for item in mapping:
        eng = item['anniversary_english']
        pol = item['polish']

        if item['has_polish'] and eng != pol:
            replacements[eng] = pol

    print(f"   Przygotowano {len(replacements)} zamian")

    # 2. Wczytaj oryginalny
    print("\n[2/3] Wczytywanie Anniversary text.bbb...")

    ann_file = "English/text.bbb"

    with open(ann_file, 'rb') as f:
        data = bytearray(f.read())

    print(f"   Rozmiar: {len(data) / 1024 / 1024:.2f} MB")

    # 3. Zamień z ZACHOWANIEM DŁUGOŚCI
    print("\n[3/3] Podmiana z dokładnymi długościami...")

    replaced_count = 0
    padded_count = 0
    truncated_count = 0

    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for eng_text, pol_text in sorted_replacements:
        eng_bytes = eng_text.encode('utf-16-le')
        pol_bytes = pol_text.encode('utf-16-le')

        pos = 0
        while True:
            pos = data.find(eng_bytes, pos)

            if pos == -1:
                break

            # Sprawdź null terminator
            if pos + len(eng_bytes) + 1 < len(data):
                next_bytes = data[pos + len(eng_bytes):pos + len(eng_bytes) + 2]

                if next_bytes == b'\x00\x00':
                    # KLUCZOWE: Zachowaj DOKŁADNĄ długość
                    target_len = len(eng_bytes)

                    if len(pol_bytes) < target_len:
                        # Polski krótszy - dodaj padding (spacje)
                        # Oblicz ile znaków brakuje
                        missing_chars = (target_len - len(pol_bytes)) // 2
                        pol_text_padded = pol_text + (' ' * missing_chars)
                        pol_bytes = pol_text_padded.encode('utf-16-le')
                        padded_count += 1

                    elif len(pol_bytes) > target_len:
                        # Polski dłuższy - obetnij
                        # Zachowaj tylko tyle znaków ile się zmieści
                        chars_that_fit = target_len // 2
                        pol_text_truncated = pol_text[:chars_that_fit]
                        pol_bytes = pol_text_truncated.encode('utf-16-le')
                        truncated_count += 1

                    # Zamień - teraz długości się zgadzają!
                    data[pos:pos + target_len] = pol_bytes[:target_len]

                    replaced_count += 1

            pos += 1

        if replaced_count % 100 == 0 and replaced_count > 0:
            print(f"   Zamieniono: {replaced_count}", flush=True)

    print(f"\n   STATYSTYKI:")
    print(f"     - Zamieniono: {replaced_count}")
    print(f"     - Z paddingiem: {padded_count}")
    print(f"     - Obcięte: {truncated_count}")

    # 4. Zapisz
    output_file = "polish_text_exact.bbb"

    with open(output_file, 'wb') as f:
        f.write(data)

    output_size = os.path.getsize(output_file) / 1024 / 1024
    original_size = len(data) / 1024 / 1024

    print(f"\n   Zapisano: {output_file} ({output_size:.2f} MB)")
    print(f"   Oryginalny rozmiar: {original_size:.2f} MB")
    print(f"   Rozmiary identyczne: {output_size == original_size}")

    return output_file


def main():
    """Główna funkcja"""

    print("Ta wersja ZACHOWUJE dokładne długości tekstów.")
    print("Offsety pozostają identyczne - indeksy .ipbe/.iple będą działać!\n")

    output = build_exact_length()

    if output:
        print("\n" + "="*60)
        print("SUKCES!")
        print("="*60)
        print(f"\nWygenerowano: {output}")
        print("\nTa wersja ma IDENTYCZNE offsety co oryginał!")
        print("Pliki .ipbe/.iple NIE wymagają zmiany.\n")
        print("INSTALACJA:")
        print("  Skopiuj polish_text_exact.bbb jako text.bbb")
        print("="*60)


if __name__ == '__main__':
    main()
