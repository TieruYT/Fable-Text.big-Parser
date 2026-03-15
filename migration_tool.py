# -*- coding: utf-8 -*-
"""
Narzędzie do migracji polskiego spolszczenia z TLC do Anniversary
Mapowanie oparte na zawartości tekstów angielskich
"""

import json
import os
from fable_text_parser import FableTextBigParser
from fable_anniversary_parser import FableAnniversaryParser
from collections import defaultdict
import difflib


class PolishMigrationTool:
    """Narzędzie do migracji polskiego spolszczenia"""

    def __init__(self, polish_tlc_file, english_tlc_file, english_ann_file):
        self.polish_tlc_file = polish_tlc_file
        self.english_tlc_file = english_tlc_file
        self.english_ann_file = english_ann_file

        self.polish_texts = {}  # nazwa -> polski tekst
        self.english_tlc = {}  # nazwa -> angielski tekst
        self.english_ann = {}  # hash -> angielski tekst

    def extract_tlc_texts(self, file_path, name="TLC"):
        """Ekstraktuje teksty z pliku TLC (format BIGB)"""
        print(f"\nParsowanie {name}: {file_path}")

        parser = FableTextBigParser(file_path)
        entries = parser.parse()

        texts = {}
        for entry in entries:
            for sub_entry in entry.sub_entries:
                texts[sub_entry.name] = sub_entry.content

        print(f"  Znaleziono {len(texts)} tekstów")
        return texts

    def extract_anniversary_texts(self):
        """Ekstraktuje teksty z Anniversary używając parsera indeksowego"""
        print(f"\nParsowanie Anniversary: {self.english_ann_file}")

        parser = FableAnniversaryParser(self.english_ann_file)
        sub_entries = parser.parse_all_texts(limit=None)  # Wszystkie teksty

        texts = {}
        for sub_entry in sub_entries:
            texts[sub_entry.name] = sub_entry.content

        print(f"  Znaleziono {len(texts)} tekstów")
        return texts

    def load_all_texts(self):
        """Ładuje wszystkie teksty z plików"""
        print("="*60)
        print("ETAP 1: Ładowanie tekstów")
        print("="*60)

        self.polish_texts = self.extract_tlc_texts(self.polish_tlc_file, "Polski TLC")
        self.english_tlc = self.extract_tlc_texts(self.english_tlc_file, "Angielski TLC")
        self.english_ann = self.extract_anniversary_texts()

    def create_content_mapping(self):
        """Tworzy mapowanie oparte na zawartości tekstów"""
        print("\n" + "="*60)
        print("ETAP 2: Tworzenie mapowania treść -> hash")
        print("="*60)

        # Stwórz mapowanie: angielski tekst TLC -> nazwa TLC
        eng_to_name = {}
        for name, content in self.english_tlc.items():
            # Normalizuj tekst (usuń białe znaki, lowercase)
            normalized = content.strip().lower()
            if normalized:
                if normalized not in eng_to_name:
                    eng_to_name[normalized] = []
                eng_to_name[normalized].append(name)

        print(f"  Utworzono mapowanie dla {len(eng_to_name)} unikalnych tekstów angielskich")

        # Znajdź dopasowania Anniversary -> TLC
        matches = {}
        exact_matches = 0
        fuzzy_matches = 0
        no_matches = 0

        print("\n  Szukanie dopasowań...")

        for ann_hash, ann_content in self.english_ann.items():
            normalized_ann = ann_content.strip().lower()

            # Szukaj dokładnego dopasowania
            if normalized_ann in eng_to_name:
                tlc_names = eng_to_name[normalized_ann]
                tlc_name = tlc_names[0]  # Użyj pierwszego dopasowania

                # Sprawdź czy mamy polski odpowiednik
                if tlc_name in self.polish_texts:
                    matches[ann_hash] = {
                        'tlc_name': tlc_name,
                        'english': self.english_tlc[tlc_name],
                        'polish': self.polish_texts[tlc_name],
                        'match_type': 'exact'
                    }
                    exact_matches += 1

            # Jeśli nie znaleziono dokładnego, spróbuj fuzzy matching (tylko dla krótkich tekstów)
            elif len(ann_content) < 200 and len(ann_content) > 10:
                best_match = None
                best_ratio = 0.0

                # Szukaj najbardziej podobnego
                for eng_text, tlc_names in list(eng_to_name.items())[:1000]:  # Ogranicz do 1000 dla wydajności
                    ratio = difflib.SequenceMatcher(None, normalized_ann, eng_text).ratio()
                    if ratio > best_ratio and ratio > 0.95:  # >95% podobieństwa
                        best_ratio = ratio
                        best_match = tlc_names[0]

                if best_match and best_match in self.polish_texts:
                    matches[ann_hash] = {
                        'tlc_name': best_match,
                        'english': self.english_tlc[best_match],
                        'polish': self.polish_texts[best_match],
                        'match_type': 'fuzzy',
                        'similarity': best_ratio
                    }
                    fuzzy_matches += 1
                else:
                    no_matches += 1
            else:
                no_matches += 1

        print(f"\n  Wyniki dopasowania:")
        print(f"    - Dokładne dopasowania: {exact_matches}")
        print(f"    - Przybliżone dopasowania: {fuzzy_matches}")
        print(f"    - Brak dopasowania: {no_matches}")

        return matches

    def export_polish_translation(self, mapping, output_file):
        """Eksportuje polskie tłumaczenie dla Anniversary"""
        print("\n" + "="*60)
        print("ETAP 3: Eksport polskiego tłumaczenia")
        print("="*60)

        # Format: hash Anniversary -> polski tekst
        translation = {}

        for ann_hash, match_data in mapping.items():
            translation[ann_hash] = {
                'polish': match_data['polish'],
                'english_original': match_data['english'],
                'tlc_name': match_data['tlc_name'],
                'match_type': match_data.get('match_type', 'exact')
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translation, f, ensure_ascii=False, indent=2)

        print(f"  Zapisano {len(translation)} polskich tłumaczeń do: {output_file}")

        return translation

    def generate_report(self, mapping, output_file):
        """Generuje raport z przykładami tłumaczeń"""
        print("\n" + "="*60)
        print("ETAP 4: Generowanie raportu")
        print("="*60)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RAPORT MIGRACJI POLSKIEGO SPOLSZCZENIA\n")
            f.write("Fable: The Lost Chapters -> Fable Anniversary\n")
            f.write("="*80 + "\n\n")

            f.write(f"Liczba zmapowanych tekstów: {len(mapping)}\n\n")

            f.write("="*80 + "\n")
            f.write("PRZYKŁADY TŁUMACZEŃ (pierwsze 20)\n")
            f.write("="*80 + "\n\n")

            for i, (ann_hash, data) in enumerate(list(mapping.items())[:20], 1):
                f.write(f"{i}. {ann_hash}\n")
                f.write(f"   TLC Nazwa: {data['tlc_name']}\n")
                f.write(f"   Typ dopasowania: {data['match_type']}\n")
                f.write(f"   Angielski: {data['english'][:100]}\n")
                f.write(f"   Polski:    {data['polish'][:100]}\n")
                f.write("\n")

        print(f"  Raport zapisany do: {output_file}")


def main():
    """Funkcja główna"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Ścieżki plików
    polish_tlc = os.path.join(script_dir, "poprzednia praca", "text.big")
    english_tlc = os.path.join(script_dir, "poprzednia praca", "text.big")  # Ten sam plik
    english_ann = r"C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb"

    print("="*60)
    print("NARZĘDZIE DO MIGRACJI POLSKIEGO SPOLSZCZENIA")
    print("Fable: The Lost Chapters -> Fable Anniversary")
    print("="*60)

    # Sprawdź czy mamy polski TLC
    # UWAGA: Użytkownik musi podać plik z polskim TLC!
    if not os.path.exists(polish_tlc):
        print("\nBŁĄD: Nie znaleziono polskiego pliku TLC")
        print("Proszę podać ścieżkę do polskiego text.big z Fable TLC")
        return

    # Utwórz narzędzie
    tool = PolishMigrationTool(polish_tlc, english_tlc, english_ann)

    # Załaduj teksty
    tool.load_all_texts()

    # Stwórz mapowanie
    mapping = tool.create_content_mapping()

    # Eksportuj
    output_dir = script_dir
    translation_file = os.path.join(output_dir, "polish_anniversary_translation.json")
    tool.export_polish_translation(mapping, translation_file)

    # Generuj raport
    report_file = os.path.join(output_dir, "migration_report.txt")
    tool.generate_report(mapping, report_file)

    print("\n" + "="*60)
    print("GOTOWE!")
    print("="*60)
    print(f"\nWygenerowane pliki:")
    print(f"  1. {translation_file}")
    print(f"  2. {report_file}")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
