# -*- coding: utf-8 -*-
"""
Narzędzie do porównania tekstów z Fable TLC i Anniversary
oraz migracji polskiego spolszczenia
"""

import json
import os
from fable_text_parser import FableTextBigParser
from collections import defaultdict
import difflib


class FableMigrationTool:
    """Narzędzie do migracji spolszczenia między wersjami Fable"""

    def __init__(self, tlc_file, anniversary_file):
        self.tlc_file = tlc_file
        self.anniversary_file = anniversary_file
        self.tlc_texts = {}
        self.anniversary_texts = {}

    def extract_texts_from_file(self, file_path, game_name):
        """Ekstraktuje wszystkie teksty z pliku"""
        print(f"\n{'='*60}")
        print(f"Parsowanie {game_name}: {file_path}")
        print(f"{'='*60}")

        parser = FableTextBigParser(file_path)
        entries = parser.parse()

        texts = {}
        total_count = 0

        for entry in entries:
            for sub_entry in entry.sub_entries:
                # Używamy nazwy jako klucza
                key = sub_entry.name
                texts[key] = {
                    'name': sub_entry.name,
                    'content': sub_entry.content,
                    'entry': entry.name
                }
                total_count += 1

        print(f"Znaleziono {total_count} tekstów w {len(entries)} głównych wpisach")
        return texts

    def extract_tlc_texts(self):
        """Ekstraktuje teksty z The Lost Chapters"""
        print("\n" + "="*60)
        print("ETAP 1: Ekstrakcja tekstów z Fable: The Lost Chapters")
        print("="*60)
        self.tlc_texts = self.extract_texts_from_file(self.tlc_file, "The Lost Chapters")

    def extract_anniversary_texts(self):
        """Ekstraktuje teksty z Anniversary"""
        print("\n" + "="*60)
        print("ETAP 2: Ekstrakcja tekstów z Fable Anniversary")
        print("="*60)
        self.anniversary_texts = self.extract_texts_from_file(self.anniversary_file, "Anniversary")

    def compare_texts(self):
        """Porównuje teksty z obu wersji"""
        print("\n" + "="*60)
        print("ETAP 3: Porównywanie tekstów")
        print("="*60)

        # Znajdź wspólne klucze (nazwy)
        tlc_keys = set(self.tlc_texts.keys())
        ann_keys = set(self.anniversary_texts.keys())

        common_keys = tlc_keys & ann_keys
        tlc_only = tlc_keys - ann_keys
        ann_only = ann_keys - tlc_keys

        print(f"\nStatystyki porównania:")
        print(f"  - Teksty w TLC: {len(tlc_keys)}")
        print(f"  - Teksty w Anniversary: {len(ann_keys)}")
        print(f"  - Wspólne klucze: {len(common_keys)}")
        print(f"  - Tylko w TLC: {len(tlc_only)}")
        print(f"  - Tylko w Anniversary: {len(ann_only)}")

        # Sprawdź ile wspólnych kluczy ma identyczne treści
        identical_count = 0
        different_count = 0
        similar_count = 0

        differences = []

        for key in list(common_keys)[:100]:  # Sprawdź pierwsze 100 dla próbki
            tlc_content = self.tlc_texts[key]['content']
            ann_content = self.anniversary_texts[key]['content']

            if tlc_content == ann_content:
                identical_count += 1
            else:
                # Oblicz podobieństwo
                similarity = difflib.SequenceMatcher(None, tlc_content, ann_content).ratio()

                if similarity > 0.9:
                    similar_count += 1
                else:
                    different_count += 1

                    if len(differences) < 10:  # Zapisz pierwsze 10 różnic
                        differences.append({
                            'key': key,
                            'tlc': tlc_content[:100],
                            'ann': ann_content[:100],
                            'similarity': similarity
                        })

        print(f"\nPorównanie treści (próbka 100 tekstów):")
        print(f"  - Identyczne: {identical_count}")
        print(f"  - Bardzo podobne (>90%): {similar_count}")
        print(f"  - Różne: {different_count}")

        if differences:
            print(f"\nPrzykłady różnic:")
            for i, diff in enumerate(differences[:5], 1):
                print(f"\n  {i}. {diff['key']} (podobieństwo: {diff['similarity']:.2%})")
                print(f"     TLC: {diff['tlc'][:80]}...")
                print(f"     ANN: {diff['ann'][:80]}...")

        return {
            'common_keys': len(common_keys),
            'tlc_only': len(tlc_only),
            'ann_only': len(ann_only),
            'identical': identical_count,
            'similar': similar_count,
            'different': different_count,
            'total_compared': 100
        }

    def export_comparison_report(self, output_file):
        """Eksportuje raport porównawczy do JSON"""
        print(f"\n" + "="*60)
        print(f"ETAP 4: Eksport raportu porównawczego")
        print(f"="*60)

        report = {
            'tlc_file': self.tlc_file,
            'anniversary_file': self.anniversary_file,
            'tlc_text_count': len(self.tlc_texts),
            'anniversary_text_count': len(self.anniversary_texts),
            'common_keys': list(set(self.tlc_texts.keys()) & set(self.anniversary_texts.keys()))[:100],
            'tlc_only_sample': list(set(self.tlc_texts.keys()) - set(self.anniversary_texts.keys()))[:50],
            'anniversary_only_sample': list(set(self.anniversary_texts.keys()) - set(self.tlc_texts.keys()))[:50]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"Raport zapisany do: {output_file}")

    def create_migration_mapping(self, output_file):
        """Tworzy mapowanie do migracji spolszczenia"""
        print(f"\n" + "="*60)
        print(f"ETAP 5: Tworzenie mapowania migracji")
        print(f"="*60)

        # Znajdź wspólne klucze
        common_keys = set(self.tlc_texts.keys()) & set(self.anniversary_texts.keys())

        # Stwórz mapowanie: klucz -> (tekst_TLC, tekst_Anniversary)
        mapping = {}

        for key in common_keys:
            mapping[key] = {
                'tlc_content': self.tlc_texts[key]['content'],
                'ann_content': self.anniversary_texts[key]['content'],
                'entry_name': self.tlc_texts[key]['entry']
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        print(f"Mapowanie zapisane do: {output_file}")
        print(f"Utworzono mapowanie dla {len(mapping)} tekstów")

        return mapping


def main():
    """Funkcja główna"""
    import sys

    # Domyślne ścieżki
    if len(sys.argv) >= 3:
        tlc_file = sys.argv[1]
        ann_file = sys.argv[2]
    else:
        # Ścieżki względem katalogu skryptu
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tlc_file = os.path.join(script_dir, "poprzednia praca", "text.big")
        ann_file = r"C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb"

    print("="*60)
    print("FABLE TEXT MIGRATION TOOL")
    print("="*60)
    print(f"\nThe Lost Chapters: {tlc_file}")
    print(f"Anniversary: {ann_file}")

    # Sprawdź czy pliki istnieją
    if not os.path.exists(tlc_file):
        print(f"\nBŁĄD: Nie znaleziono pliku TLC: {tlc_file}")
        return

    if not os.path.exists(ann_file):
        print(f"\nBŁĄD: Nie znaleziono pliku Anniversary: {ann_file}")
        return

    # Utwórz narzędzie migracji
    tool = FableMigrationTool(tlc_file, ann_file)

    # Ekstraktuj teksty
    tool.extract_tlc_texts()
    tool.extract_anniversary_texts()

    # Porównaj
    comparison_stats = tool.compare_texts()

    # Eksportuj raport
    output_dir = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(output_dir, "comparison_report.json")
    tool.export_comparison_report(report_file)

    # Stwórz mapowanie
    mapping_file = os.path.join(output_dir, "migration_mapping.json")
    tool.create_migration_mapping(mapping_file)

    print("\n" + "="*60)
    print("PODSUMOWANIE")
    print("="*60)
    print(f"\nProcentowo identycznych tekstów: {comparison_stats['identical'] / comparison_stats['total_compared'] * 100:.1f}%")
    print(f"Podobnych: {comparison_stats['similar'] / comparison_stats['total_compared'] * 100:.1f}%")
    print(f"Różnych: {comparison_stats['different'] / comparison_stats['total_compared'] * 100:.1f}%")

    if comparison_stats['identical'] >= 80:  # Jeśli >80% jest identycznych
        print("\n✓ WNIOSEK: Teksty są wystarczająco podobne do migracji!")
        print("  Możesz użyć tego narzędzia do przeniesienia polskiego spolszczenia.")
    elif comparison_stats['identical'] + comparison_stats['similar'] >= 80:
        print("\n⚠ WNIOSEK: Teksty są podobne, ale mogą wymagać przeglądu.")
        print("  Migracja jest możliwa, ale zaleca się ręczną weryfikację.")
    else:
        print("\n✗ WNIOSEK: Teksty różnią się znacząco.")
        print("  Migracja może nie działać poprawnie.")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
