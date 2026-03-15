# -*- coding: utf-8 -*-
"""
SZYBKA wersja - bezpośrednia modyfikacja bajtów
"""

import json
import os


def normalize_text(text):
    """Normalizuje tekst"""
    return ' '.join(text.split()).lower().strip().rstrip('.,!?;:')


def build_polish_fast():
    """Szybkie budowanie - bezpośrednia podmiana w bajtach"""

    print("="*60)
    print("SZYBKIE BUDOWANIE POLSKIEGO BBB")
    print("="*60)

    # 1. Załaduj mapowanie
    print("\n[1/3] Ładowanie mapowania...")

    with open('final_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    # Stwórz mapowanie: angielski → polski
    replacements = {}

    for item in mapping:
        eng = item['anniversary_english']
        pol = item['polish']

        if item['has_polish'] and eng != pol:
            replacements[eng] = pol

    print(f"   Przygotowano {len(replacements)} zamian")

    # 2. Wczytaj oryginalny plik
    print("\n[2/3] Wczytywanie Anniversary text.bbb...")

    ann_file = "English/text.bbb"

    if not os.path.exists(ann_file):
        print(f"BŁĄD: Nie znaleziono {ann_file}")
        return

    with open(ann_file, 'rb') as f:
        data = bytearray(f.read())

    file_size = len(data) / 1024 / 1024
    print(f"   Rozmiar: {file_size:.2f} MB")

    # 3. Zamień teksty w bajtach
    print("\n[3/3] Podmiana tekstów...")

    replaced_count = 0

    # Sortuj zamiany od najdłuższych (aby uniknąć częściowych zamian)
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for eng_text, pol_text in sorted_replacements:
        # Konwertuj do UTF-16 LE
        eng_bytes = eng_text.encode('utf-16-le')
        pol_bytes = pol_text.encode('utf-16-le')

        # Szukaj i zamień
        pos = 0
        while True:
            pos = data.find(eng_bytes, pos)

            if pos == -1:
                break

            # Sprawdź czy to kompletny string (sprawdź null terminator)
            if pos + len(eng_bytes) + 1 < len(data):
                next_bytes = data[pos + len(eng_bytes):pos + len(eng_bytes) + 2]

                if next_bytes == b'\x00\x00':  # Null terminator
                    # Zamień!
                    data[pos:pos + len(eng_bytes)] = pol_bytes

                    # Jeśli polski jest krótszy, wypełnij zerami
                    if len(pol_bytes) < len(eng_bytes):
                        diff = len(eng_bytes) - len(pol_bytes)
                        data[pos + len(pol_bytes):pos + len(eng_bytes)] = b'\x00' * diff

                    # Jeśli polski jest dłuższy - problem!
                    # Musimy użyć prostego podejścia - obetnij
                    elif len(pol_bytes) > len(eng_bytes):
                        # Obetnij polski tekst do długości angielskiego
                        data[pos:pos + len(eng_bytes)] = pol_bytes[:len(eng_bytes)]

                    replaced_count += 1

            pos += 1

        if replaced_count % 100 == 0 and replaced_count > 0:
            print(f"   Zamieniono: {replaced_count}", flush=True)

    print(f"\n   Łącznie zamieniono: {replaced_count} tekstów")

    # 4. Zapisz
    output_file = "polish_text.bbb"

    with open(output_file, 'wb') as f:
        f.write(data)

    output_size = os.path.getsize(output_file) / 1024 / 1024
    print(f"\n   Zapisano: {output_file} ({output_size:.2f} MB)")

    return output_file


def main():
    """Główna funkcja"""

    print("UWAGA: To eksperymentalna wersja która bezpośrednio modyfikuje bajty.")
    print("Jeśli teksty są dłuższe niż oryginał, mogą być obcięte.\n")

    output = build_polish_fast()

    if output:
        print("\n" + "="*60)
        print("GOTOWE!")
        print("="*60)
        print(f"\nWygenerowano: {output}")
        print("\nKOLEJNE KROKI:")
        print("1. BACKUP:")
        print("   Skopiuj oryginalny text.bbb jako text.bbb.backup")
        print("")
        print("2. PODMIANA:")
        print("   Skopiuj polish_text.bbb do:")
        print("   C:\\Program Files (x86)\\Fable Anniversary\\WellingtonGame\\")
        print("   FableData\\Build\\Data\\lang\\English\\text.bbb")
        print("")
        print("3. TEST:")
        print("   Uruchom grę!")
        print("="*60)


if __name__ == '__main__':
    main()
