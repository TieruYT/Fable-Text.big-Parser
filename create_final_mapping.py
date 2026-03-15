# -*- coding: utf-8 -*-
"""
Tworzy FINALNE MAPOWANIE do spolszczenia Anniversary
"""

import json
import re
from fable_text_parser import FableTextBigParser


def normalize_text(text):
    """Normalizuje tekst do porównywania"""
    normalized = ' '.join(text.split()).lower().strip()
    normalized = normalized.rstrip('.,!?;:')
    return normalized


def load_anniversary_texts(file_path):
    """Ładuje oczyszczone teksty Anniversary"""
    texts = []
    current_text = ""
    in_text = False

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
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


def create_complete_mapping():
    """Tworzy kompletne mapowanie Anniversary -> Polski"""

    print("="*60)
    print("TWORZENIE FINALNEGO MAPOWANIA")
    print("="*60)

    # 1. Załaduj angielski TLC
    print("\n[1/4] Parsowanie angielskiego TLC...")
    tlc_eng_file = r'C:\Gry\Fable The Lost ChaptersEN\data\lang\English\text.big'

    tlc_eng_parser = FableTextBigParser(tlc_eng_file)
    tlc_eng_entries = tlc_eng_parser.parse()

    tlc_eng_map = {}  # znormalizowany_tekst -> {name, content}

    for entry in tlc_eng_entries:
        for sub in entry.sub_entries:
            normalized = normalize_text(sub.content)
            if normalized and len(normalized) > 5:
                if normalized not in tlc_eng_map:
                    tlc_eng_map[normalized] = []

                tlc_eng_map[normalized].append({
                    'name': sub.name,
                    'content': sub.content
                })

    print(f"   TLC Angielski: {len(tlc_eng_map)} unikalnych tekstów")

    # 2. Załaduj polski TLC
    print("\n[2/4] Ładowanie polskiego TLC...")
    with open('polish_tlc_export.json', 'r', encoding='utf-8') as f:
        polish_data = json.load(f)

    polish_texts = polish_data['polish_texts']
    print(f"   TLC Polski: {len(polish_texts)} tekstów")

    # 3. Stwórz mapowanie: nazwa TLC -> polski tekst
    print("\n[3/4] Mapowanie TLC nazwa -> polski...")

    name_to_polish = {}
    for name, polish_text in polish_texts.items():
        name_to_polish[name] = polish_text

    print(f"   Mapowanie: {len(name_to_polish)} par")

    # 4. Załaduj Anniversary i zmapuj
    print("\n[4/4] Mapowanie Anniversary -> Polski...")

    anniversary_texts = load_anniversary_texts("anniversary_texts_clean.txt")
    print(f"   Anniversary: {len(anniversary_texts)} tekstów")

    # Mapowanie końcowe
    final_mapping = []
    exact_matches = 0
    polish_found = 0
    no_match = 0

    print("\n   Szukanie dopasowań...")

    for i, ann_text in enumerate(anniversary_texts):
        if i % 1000 == 0:
            print(f"     Postęp: {i}/{len(anniversary_texts)}", flush=True)

        normalized_ann = normalize_text(ann_text)

        # Szukaj w angielskim TLC
        if normalized_ann in tlc_eng_map:
            tlc_matches = tlc_eng_map[normalized_ann]
            tlc_data = tlc_matches[0]  # Użyj pierwszego dopasowania

            exact_matches += 1

            # Sprawdź czy mamy polską wersję
            if tlc_data['name'] in name_to_polish:
                polish_text = name_to_polish[tlc_data['name']]
                polish_found += 1
            else:
                # Nie ma polskiej - użyj angielskiej
                polish_text = ann_text

            final_mapping.append({
                'anniversary_english': ann_text,
                'tlc_name': tlc_data['name'],
                'tlc_english': tlc_data['content'],
                'polish': polish_text,
                'has_polish': tlc_data['name'] in name_to_polish
            })
        else:
            no_match += 1

    print(f"\n   WYNIKI:")
    print(f"     - Dopasowania TLC: {exact_matches}")
    print(f"     - Z polskim tłumaczeniem: {polish_found}")
    print(f"     - Bez polskiego (angielski): {exact_matches - polish_found}")
    print(f"     - Brak dopasowania: {no_match}")
    print(f"     - RAZEM zmapowanych: {len(final_mapping)}")

    return final_mapping


def export_mapping(mapping):
    """Eksportuje mapowanie"""

    print("\n" + "="*60)
    print("EKSPORT MAPOWANIA")
    print("="*60)

    # JSON z pełnymi danymi
    json_file = "final_mapping.json"
    print(f"\nZapisywanie: {json_file}")

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(mapping)} par")

    # Raport tekstowy
    report_file = "final_mapping_report.txt"
    print(f"\nGenerowanie raportu: {report_file}")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("FINALNE MAPOWANIE - RAPORT\n")
        f.write("="*80 + "\n\n")

        polish_count = sum(1 for m in mapping if m['has_polish'])
        english_count = len(mapping) - polish_count

        f.write(f"Zmapowanych tekstów: {len(mapping)}\n")
        f.write(f"  - Po polsku: {polish_count}\n")
        f.write(f"  - Po angielsku (brak PL): {english_count}\n\n")

        f.write("="*80 + "\n")
        f.write("PRZYKŁADY Z POLSKIM TŁUMACZENIEM (pierwsze 30)\n")
        f.write("="*80 + "\n\n")

        polish_examples = [m for m in mapping if m['has_polish']][:30]

        for i, m in enumerate(polish_examples, 1):
            f.write(f"{i}. Klucz: {m['tlc_name']}\n")
            f.write(f"   Anniversary (EN): {m['anniversary_english'][:120]}\n")
            f.write(f"   Polski:           {m['polish'][:120]}\n\n")

        f.write("="*80 + "\n")
        f.write("PRZYKŁADY BEZ POLSKIEGO (pierwsze 20)\n")
        f.write("="*80 + "\n\n")

        english_examples = [m for m in mapping if not m['has_polish']][:20]

        for i, m in enumerate(english_examples, 1):
            f.write(f"{i}. Klucz: {m['tlc_name']}\n")
            f.write(f"   Tekst (EN): {m['anniversary_english'][:120]}\n\n")

    print("Raport zapisany")


def main():
    """Główna funkcja"""

    # Stwórz mapowanie
    mapping = create_complete_mapping()

    # Eksportuj
    export_mapping(mapping)

    print("\n" + "="*60)
    print("SUKCES!")
    print("="*60)

    polish_count = sum(1 for m in mapping if m['has_polish'])
    english_count = len(mapping) - polish_count

    print(f"\nZMAPOWANO {len(mapping)} TEKSTÓW:")
    print(f"  ✓ Po polsku: {polish_count}")
    print(f"  ✓ Po angielsku: {english_count}")
    print(f"\nProcent polskiego: {polish_count/len(mapping)*100:.1f}%")

    print("\nPliki:")
    print("  - final_mapping.json")
    print("  - final_mapping_report.txt")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
