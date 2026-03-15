# -*- coding: utf-8 -*-
"""
Szybkie porównanie pierwszych N tekstów z obu wersji
"""

import sys
import os
from fable_text_parser import FableTextBigParser


def quick_compare(tlc_file, ann_file, sample_size=50):
    """Szybkie porównanie próbki tekstów"""

    print("="*60)
    print("SZYBKIE PORÓWNANIE TEKSTÓW")
    print("="*60)

    # Parsuj TLC
    print(f"\n1. Parsowanie TLC: {tlc_file}")
    tlc_parser = FableTextBigParser(tlc_file)
    tlc_entries = tlc_parser.parse()

    tlc_texts = {}
    for entry in tlc_entries:
        for i, sub in enumerate(entry.sub_entries):
            if i >= sample_size:
                break
            tlc_texts[sub.name] = sub.content

    print(f"   Pobrano {len(tlc_texts)} tekstów z TLC")

    # Parsuj Anniversary
    print(f"\n2. Parsowanie Anniversary: {ann_file}")
    ann_parser = FableTextBigParser(ann_file)
    ann_entries = ann_parser.parse()

    ann_texts = {}
    for entry in ann_entries:
        for i, sub in enumerate(entry.sub_entries):
            if i >= sample_size:
                break
            ann_texts[sub.name] = sub.content

    print(f"   Pobrano {len(ann_texts)} tekstów z Anniversary")

    # Porównaj
    print(f"\n3. Porównywanie...")

    common_keys = set(tlc_texts.keys()) & set(ann_texts.keys())
    tlc_only = set(tlc_texts.keys()) - set(ann_texts.keys())
    ann_only = set(ann_texts.keys()) - set(tlc_texts.keys())

    print(f"\n   Statystyki:")
    print(f"   - Wspólne klucze: {len(common_keys)}")
    print(f"   - Tylko w TLC: {len(tlc_only)}")
    print(f"   - Tylko w Anniversary: {len(ann_only)}")

    # Sprawdź identyczność treści
    identical = 0
    different = 0

    print(f"\n4. Przykłady porównania:\n")

    for i, key in enumerate(list(common_keys)[:10]):
        tlc_content = tlc_texts[key]
        ann_content = ann_texts[key]

        match_status = "✓ IDENTYCZNE" if tlc_content == ann_content else "✗ RÓŻNE"

        print(f"   [{i+1}] {key}")
        print(f"       Status: {match_status}")
        print(f"       TLC: {tlc_content[:80]}")
        print(f"       ANN: {ann_content[:80]}")
        print()

        if tlc_content == ann_content:
            identical += 1
        else:
            different += 1

    # Podsumowanie
    print("="*60)
    print("PODSUMOWANIE")
    print("="*60)

    if len(common_keys) > 0:
        match_percent = (identical / len(common_keys)) * 100
        print(f"\nIdentycznych tekstów: {identical}/{len(common_keys)} ({match_percent:.1f}%)")
        print(f"Różnych tekstów: {different}/{len(common_keys)}")

        if match_percent >= 80:
            print("\n✓ WNIOSEK: Teksty są bardzo podobne!")
            print("  Migracja spolszczenia powinna działać poprawnie.")
        elif match_percent >= 50:
            print("\n⚠ WNIOSEK: Teksty są częściowo podobne")
            print("  Migracja jest możliwa, ale wymaga weryfikacji.")
        else:
            print("\n✗ WNIOSEK: Teksty znacząco się różnią")
            print("  Migracja może nie działać poprawnie.")
    else:
        print("\n✗ BRAK WSPÓLNYCH KLUCZY!")
        print("  Formaty mogą być niezgodne lub używać innych nazw.")

    print("\n" + "="*60)

    return {
        'common': len(common_keys),
        'identical': identical,
        'different': different,
        'tlc_only': list(tlc_only)[:10],
        'ann_only': list(ann_only)[:10]
    }


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tlc_file = os.path.join(script_dir, "poprzednia praca", "text.big")
    ann_file = r"C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb"

    if not os.path.exists(tlc_file):
        print(f"BŁĄD: Nie znaleziono pliku TLC: {tlc_file}")
        sys.exit(1)

    if not os.path.exists(ann_file):
        print(f"BŁĄD: Nie znaleziono pliku Anniversary: {ann_file}")
        sys.exit(1)

    quick_compare(tlc_file, ann_file, sample_size=100)
