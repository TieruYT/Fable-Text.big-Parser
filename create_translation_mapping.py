# -*- coding: utf-8 -*-
"""
Tworzy mapowanie: angielski tekst Anniversary -> polski tekst TLC
"""

import json
import re
from difflib import SequenceMatcher


def load_anniversary_texts(file_path):
    """Ładuje oczyszczone teksty Anniversary"""

    texts = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        current_text = ""
        in_text = False

        for line in f:
            line_stripped = line.strip()

            if line_stripped.startswith('[') and line_stripped.endswith(']'):
                # Nowy wpis
                if current_text:
                    texts.append(current_text.strip())
                current_text = ""
                in_text = True
            elif in_text and line_stripped and not line_stripped.startswith('='):
                current_text += line_stripped + " "

        # Ostatni
        if current_text:
            texts.append(current_text.strip())

    return texts


def normalize_text(text):
    """Normalizuje tekst do porównywania"""
    # Usuń białe znaki, lowercase
    normalized = ' '.join(text.split()).lower()
    # Usuń interpunkcję na końcu
    normalized = normalized.rstrip('.,!?;:')
    return normalized


def create_mapping(anniversary_texts, polish_data):
    """Tworzy mapowanie angielski -> polski"""

    print("="*60)
    print("TWORZENIE MAPOWANIA ANGIELSKI -> POLSKI")
    print("="*60)

    # Załaduj polskie i angielskie teksty z TLC
    polish_texts = polish_data['polish_texts']
    english_texts = polish_data['english_texts']

    print(f"\nDane wejściowe:")
    print(f"  - Teksty Anniversary (angielskie): {len(anniversary_texts)}")
    print(f"  - Polskie teksty TLC: {len(polish_texts)}")
    print(f"  - Angielskie teksty TLC: {len(english_texts)}")

    # Stwórz indeks: znormalizowany angielski TLC -> polski TLC
    tlc_eng_to_pol = {}

    for key, polish_text in polish_texts.items():
        if key in english_texts:
            # Mamy odpowiednik angielski
            english_text = english_texts[key]
        else:
            # Nie ma angielskiego - użyj polskiego jako klucza
            english_text = polish_text

        normalized_eng = normalize_text(english_text)

        if normalized_eng:
            tlc_eng_to_pol[normalized_eng] = {
                'polish': polish_text,
                'english': english_text,
                'key': key
            }

    print(f"\nMapowanie TLC (angielski -> polski): {len(tlc_eng_to_pol)} wpisów")

    # Mapuj Anniversary -> TLC
    mapping = []
    exact_matches = 0
    fuzzy_matches = 0
    no_match = 0

    print("\nSzukanie dopasowań...")

    for ann_text in anniversary_texts:
        normalized_ann = normalize_text(ann_text)

        # Szukaj dokładnego dopasowania
        if normalized_ann in tlc_eng_to_pol:
            mapping.append({
                'anniversary_english': ann_text,
                'tlc_english': tlc_eng_to_pol[normalized_ann]['english'],
                'polish': tlc_eng_to_pol[normalized_ann]['polish'],
                'tlc_key': tlc_eng_to_pol[normalized_ann]['key'],
                'match_type': 'exact'
            })
            exact_matches += 1

        else:
            # Szukaj fuzzy match (tylko dla krótszych tekstów)
            if len(ann_text) < 200:
                best_match = None
                best_ratio = 0.0

                for tlc_eng_norm, tlc_data in list(tlc_eng_to_pol.items())[:5000]:  # Ogranicz dla wydajności
                    ratio = SequenceMatcher(None, normalized_ann, tlc_eng_norm).ratio()

                    if ratio > best_ratio and ratio > 0.90:  # >90% podobieństwa
                        best_ratio = ratio
                        best_match = tlc_data

                if best_match:
                    mapping.append({
                        'anniversary_english': ann_text,
                        'tlc_english': best_match['english'],
                        'polish': best_match['polish'],
                        'tlc_key': best_match['key'],
                        'match_type': 'fuzzy',
                        'similarity': best_ratio
                    })
                    fuzzy_matches += 1
                else:
                    no_match += 1
            else:
                no_match += 1

    print(f"\nWyniki:")
    print(f"  - Dokładne dopasowania: {exact_matches}")
    print(f"  - Przybliżone dopasowania: {fuzzy_matches}")
    print(f"  - Brak dopasowania: {no_match}")
    print(f"  - Razem zmapowanych: {len(mapping)}")

    return mapping


def export_mapping(mapping, output_file):
    """Eksportuje mapowanie do JSON"""

    print(f"\nZapisywanie mapowania do: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(mapping)} par tłumaczeń")


def create_report(mapping, output_file):
    """Tworzy raport z przykładami"""

    print(f"\nGenerowanie raportu: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RAPORT MAPOWANIA TEKSTÓW\n")
        f.write("Fable Anniversary (EN) -> Fable TLC (PL)\n")
        f.write("="*80 + "\n\n")

        f.write(f"Liczba zmapowanych tekstów: {len(mapping)}\n\n")

        exact = [m for m in mapping if m['match_type'] == 'exact']
        fuzzy = [m for m in mapping if m['match_type'] == 'fuzzy']

        f.write(f"Dokładne dopasowania: {len(exact)}\n")
        f.write(f"Przybliżone dopasowania: {len(fuzzy)}\n\n")

        f.write("="*80 + "\n")
        f.write("PRZYKŁADY TŁUMACZEŃ (pierwsze 30)\n")
        f.write("="*80 + "\n\n")

        for i, m in enumerate(mapping[:30], 1):
            f.write(f"{i}. Typ: {m['match_type']}\n")
            f.write(f"   Klucz TLC: {m['tlc_key']}\n")
            f.write(f"   Anniversary (EN): {m['anniversary_english'][:100]}\n")
            f.write(f"   TLC (PL):         {m['polish'][:100]}\n")
            if 'similarity' in m:
                f.write(f"   Podobieństwo: {m['similarity']:.2%}\n")
            f.write("\n")

    print(f"Raport zapisany")


def main():
    """Główna funkcja"""

    # Wczytaj dane
    print("Ładowanie danych...")

    anniversary_texts = load_anniversary_texts("anniversary_texts_clean.txt")
    print(f"Załadowano {len(anniversary_texts)} tekstów Anniversary")

    with open("polish_tlc_export.json", 'r', encoding='utf-8') as f:
        polish_data = json.load(f)

    print(f"Załadowano {len(polish_data['polish_texts'])} polskich tekstów TLC")

    # Stwórz mapowanie
    mapping = create_mapping(anniversary_texts, polish_data)

    # Eksportuj
    export_mapping(mapping, "translation_mapping.json")
    create_report(mapping, "translation_report.txt")

    print("\n" + "="*60)
    print("SUKCES!")
    print("="*60)
    print(f"\nWygenerowano:")
    print(f"  1. translation_mapping.json - pełne mapowanie")
    print(f"  2. translation_report.txt - raport z przykładami")
    print(f"\nZmapowano {len(mapping)} tekstów na polski!")
    print("="*60)


if __name__ == '__main__':
    main()
