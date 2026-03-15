# -*- coding: utf-8 -*-
"""
Szybka wersja - głównie exact matches, bez fuzzy matchingu
"""

import json
import re


def load_anniversary_texts(file_path):
    """Ładuje oczyszczone teksty Anniversary"""

    texts = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_text = ""
        in_text = False

        for line in f:
            line_stripped = line.strip()

            if line_stripped.startswith('[') and line_stripped.endswith(']'):
                if current_text:
                    texts.append(current_text.strip())
                current_text = ""
                in_text = True
            elif in_text and line_stripped and not line_stripped.startswith('='):
                current_text += line_stripped + " "

        if current_text:
            texts.append(current_text.strip())

    return texts


def normalize_text(text):
    """Normalizuje tekst do porównywania"""
    normalized = ' '.join(text.split()).lower()
    normalized = normalized.rstrip('.,!?;:')
    return normalized


def create_mapping_fast(anniversary_texts, polish_data):
    """Tworzy mapowanie - TYLKO exact matches"""

    print("="*60)
    print("TWORZENIE MAPOWANIA (FAST - EXACT MATCHES ONLY)")
    print("="*60)

    polish_texts = polish_data['polish_texts']
    english_texts = polish_data['english_texts']

    print(f"\nDane wejściowe:")
    print(f"  - Teksty Anniversary: {len(anniversary_texts)}")
    print(f"  - Polskie teksty TLC: {len(polish_texts)}")
    print(f"  - Angielskie teksty TLC: {len(english_texts)}")

    # Stwórz indeks: znormalizowany angielski -> polski
    print("\nBudowanie indeksu TLC...")

    tlc_eng_to_pol = {}

    # Dodaj teksty które mają polską wersję
    for key, polish_text in polish_texts.items():
        if key in english_texts:
            english_text = english_texts[key]
        else:
            # Brak angielskiego - pomiń
            continue

        normalized_eng = normalize_text(english_text)

        if normalized_eng and len(normalized_eng) > 5:
            if normalized_eng not in tlc_eng_to_pol:
                tlc_eng_to_pol[normalized_eng] = []

            tlc_eng_to_pol[normalized_eng].append({
                'polish': polish_text,
                'english': english_text,
                'key': key
            })

    print(f"Indeks TLC: {len(tlc_eng_to_pol)} unikalnych angielskich tekstów")

    # Mapuj Anniversary -> TLC (TYLKO exact matches)
    print("\nSzukanie exact matches...")

    mapping = []
    exact_matches = 0
    no_match = 0

    for i, ann_text in enumerate(anniversary_texts):
        if i % 1000 == 0:
            print(f"  Przetworzono: {i}/{len(anniversary_texts)}", flush=True)

        normalized_ann = normalize_text(ann_text)

        if normalized_ann in tlc_eng_to_pol:
            # Znaleziono dopasowanie!
            tlc_data = tlc_eng_to_pol[normalized_ann][0]  # Użyj pierwszego

            mapping.append({
                'anniversary_english': ann_text,
                'tlc_english': tlc_data['english'],
                'polish': tlc_data['polish'],
                'tlc_key': tlc_data['key'],
                'match_type': 'exact'
            })
            exact_matches += 1
        else:
            no_match += 1

    print(f"\nWyniki:")
    print(f"  - Exact matches: {exact_matches}")
    print(f"  - Brak dopasowania: {no_match}")
    print(f"  - Procent dopasowanych: {exact_matches/len(anniversary_texts)*100:.1f}%")

    return mapping


def export_mapping(mapping, output_file):
    """Eksportuje mapowanie do JSON"""

    print(f"\nZapisywanie: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(mapping)} tłumaczeń")


def create_report(mapping, output_file):
    """Tworzy raport tekstowy"""

    print(f"\nGenerowanie raportu: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RAPORT MAPOWANIA TEKSTÓW\n")
        f.write("="*80 + "\n\n")

        f.write(f"Liczba zmapowanych tekstów: {len(mapping)}\n\n")

        f.write("="*80 + "\n")
        f.write("PRZYKŁADY (pierwsze 50)\n")
        f.write("="*80 + "\n\n")

        for i, m in enumerate(mapping[:50], 1):
            f.write(f"{i}. Klucz: {m['tlc_key']}\n")
            f.write(f"   EN: {m['anniversary_english'][:150]}\n")
            f.write(f"   PL: {m['polish'][:150]}\n\n")

    print("Raport zapisany")


def main():
    """Główna funkcja"""

    print("Ładowanie danych...")

    anniversary_texts = load_anniversary_texts("anniversary_texts_clean.txt")
    print(f"Anniversary: {len(anniversary_texts)} tekstów")

    with open("polish_tlc_export.json", 'r', encoding='utf-8') as f:
        polish_data = json.load(f)

    print(f"TLC: {len(polish_data['polish_texts'])} polskich tekstów")

    # Mapuj
    mapping = create_mapping_fast(anniversary_texts, polish_data)

    # Eksportuj
    export_mapping(mapping, "translation_mapping.json")
    create_report(mapping, "translation_report.txt")

    print("\n" + "="*60)
    print("SUKCES!")
    print("="*60)
    print(f"\nZmapowano: {len(mapping)} tekstów")
    print(f"\nPliki:")
    print(f"  - translation_mapping.json")
    print(f"  - translation_report.txt")
    print("="*60)


if __name__ == '__main__':
    main()
