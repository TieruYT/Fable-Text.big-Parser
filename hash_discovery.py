# -*- coding: utf-8 -*-
"""
Odkrywa algorytm hashowania nazw TLC -> hashe Anniversary
"""

import struct
import binascii
from fable_text_parser import FableTextBigParser
from fable_anniversary_parser import FableAnniversaryParser


def crc32_hash(text):
    """CRC32 hash"""
    return binascii.crc32(text.encode('ascii')) & 0xFFFFFFFF


def fnv1a_32(text):
    """FNV-1a 32-bit hash"""
    hash_value = 0x811c9dc5
    for char in text.encode('ascii'):
        hash_value ^= char
        hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
    return hash_value


def simple_sum(text):
    """Simple sum hash"""
    return sum(ord(c) for c in text) & 0xFFFFFFFF


def try_hash_algorithms(name, target_hash):
    """Testuje różne algorytmy hashowania"""
    algorithms = [
        ('CRC32', crc32_hash),
        ('FNV-1a', fnv1a_32),
        ('Simple Sum', simple_sum),
    ]

    # Testuj różne warianty nazwy
    variants = [
        name,
        name.upper(),
        name.lower(),
        name.replace('_', ''),
        name.replace('TEXT_', ''),
        name.replace('TXT_', ''),
    ]

    for variant in variants:
        for algo_name, algo_func in algorithms:
            try:
                hash_val = algo_func(variant)
                if hash_val == target_hash:
                    return (algo_name, variant)
            except:
                pass

    return None


def main():
    """Funkcja główna"""
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    tlc_file = os.path.join(script_dir, "poprzednia praca", "text.big")
    ann_file = r"C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb"

    print("="*60)
    print("ODKRYWANIE ALGORYTMU HASHOWANIA")
    print("="*60)

    # Parsuj TLC
    print("\n1. Parsowanie TLC...")
    tlc_parser = FableTextBigParser(tlc_file)
    tlc_entries = tlc_parser.parse()

    tlc_texts = {}
    for entry in tlc_entries:
        for sub in entry.sub_entries:
            # Usuń białe znaki i normalizuj
            normalized = ' '.join(sub.content.split()).lower()
            if normalized and len(normalized) > 10:  # Minimum 10 znaków
                tlc_texts[normalized] = {
                    'name': sub.name,
                    'content': sub.content
                }

    print(f"   Załadowano {len(tlc_texts)} tekstów z TLC")

    # Parsuj Anniversary (ograniczona próbka dla szybkości)
    print("\n2. Parsowanie Anniversary (próbka 500)...")
    ann_parser = FableAnniversaryParser(ann_file)
    ann_texts = ann_parser.parse_all_texts(limit=500)

    print(f"   Załadowano {len(ann_texts)} tekstów z Anniversary")

    # Znajdź dopasowania
    print("\n3. Szukanie dopasowań...")

    matches = []

    for ann_sub in ann_texts:
        normalized_ann = ' '.join(ann_sub.content.split()).lower()

        if normalized_ann in tlc_texts:
            tlc_name = tlc_texts[normalized_ann]['name']
            ann_hash_str = ann_sub.name  # np. "0xEDA40F00"

            # Konwertuj hash do inta
            try:
                ann_hash_int = int(ann_hash_str, 16)
            except:
                continue

            matches.append({
                'tlc_name': tlc_name,
                'ann_hash_str': ann_hash_str,
                'ann_hash_int': ann_hash_int,
                'content': ann_sub.content[:80]
            })

    print(f"   Znaleziono {len(matches)} dopasowań!")

    # Testuj algorytmy hashowania
    print("\n4. Testowanie algorytmów hashowania...")

    found_algo = None

    for match in matches[:20]:  # Test na pierwszych 20
        result = try_hash_algorithms(match['tlc_name'], match['ann_hash_int'])

        if result:
            algo_name, variant = result
            print(f"\n   ✓ ZNALEZIONO!")
            print(f"     Algorytm: {algo_name}")
            print(f"     Nazwa TLC: {match['tlc_name']}")
            print(f"     Wariant: {variant}")
            print(f"     Hash Anniversary: {match['ann_hash_str']}")
            print(f"     Treść: {match['content']}")
            found_algo = (algo_name, variant)
            break

    if not found_algo:
        print("\n   ✗ Nie znaleziono algorytmu hashowania")
        print("   Anniversary może używać custom hash lub nie bazować na nazwach TLC")

        # Wyświetl przykłady do analizy
        print("\n5. Przykłady dopasowań (do ręcznej analizy):")
        print("="*60)

        for i, match in enumerate(matches[:10], 1):
            print(f"\n{i}. TLC Nazwa: {match['tlc_name']}")
            print(f"   Anniversary Hash: {match['ann_hash_str']} ({match['ann_hash_int']})")
            print(f"   Treść: {match['content']}")

            # Pokaż próby hashowania
            print(f"   CRC32(name): 0x{crc32_hash(match['tlc_name']):08X}")
            print(f"   FNV-1a(name): 0x{fnv1a_32(match['tlc_name']):08X}")

    else:
        print("\n" + "="*60)
        print("SUKCES!")
        print("="*60)
        print(f"\nAlgorytm: {found_algo[0]}")
        print(f"Format nazwy: {found_algo[1]}")

        # Zapisz mapowanie
        print("\n6. Tworzenie pełnego mapowania...")

        mapping_file = os.path.join(script_dir, "name_to_hash_mapping.txt")

        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write(f"Algorytm: {found_algo[0]}\n\n")

            for match in matches:
                f.write(f"{match['tlc_name']} -> {match['ann_hash_str']}\n")

        print(f"   Zapisano mapowanie do: {mapping_file}")

    print("\n" + "="*60)

    return matches


if __name__ == '__main__':
    matches = main()
