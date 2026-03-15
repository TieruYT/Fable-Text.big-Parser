# -*- coding: utf-8 -*-
"""
Eksportuje polskie teksty z TLC do formatu gotowego do użycia
"""

import json
import re
from fable_text_parser import FableTextBigParser


def export_polish_texts():
    """Eksportuje wszystkie polskie teksty z TLC"""

    print("="*60)
    print("EKSPORT POLSKICH TEKSTÓW Z FABLE TLC")
    print("="*60)

    tlc_file = "poprzednia praca/text.big"

    print(f"\nParsowanie: {tlc_file}")
    parser = FableTextBigParser(tlc_file)
    entries = parser.parse()

    # Pattern dla polskich znaków
    polish_pattern = re.compile(r'[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]')

    polish_texts = {}
    english_texts = {}

    for entry in entries:
        for sub in entry.sub_entries:
            if polish_pattern.search(sub.content):
                polish_texts[sub.name] = sub.content
            else:
                english_texts[sub.name] = sub.content

    print(f"\nStatystyki:")
    print(f"  - Polskie teksty: {len(polish_texts)}")
    print(f"  - Angielskie teksty: {len(english_texts)}")
    print(f"  - Razem: {len(polish_texts) + len(english_texts)}")
    print(f"  - Procent polskiego: {len(polish_texts)/(len(polish_texts)+len(english_texts))*100:.1f}%")

    # Eksportuj do JSON
    output_data = {
        'polish_texts': polish_texts,
        'english_texts': english_texts,
        'stats': {
            'polish_count': len(polish_texts),
            'english_count': len(english_texts),
            'total': len(polish_texts) + len(english_texts)
        }
    }

    output_file = "polish_tlc_export.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nEksport zapisany do: {output_file}")

    # Stwórz też prosty format TXT dla przeglądu
    txt_file = "polish_tlc_export.txt"

    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("POLSKIE TEKSTY Z FABLE: THE LOST CHAPTERS\n")
        f.write("="*80 + "\n\n")

        for name, content in sorted(polish_texts.items())[:100]:  # Pierwsze 100
            f.write(f"[{name}]\n")
            f.write(f"{content}\n\n")

    print(f"Przykłady zapisane do: {txt_file}")

    print("\n" + "="*60)
    print("SUKCES!")
    print("="*60)
    print("\nWygenerowano:")
    print(f"  1. {output_file} - pełny eksport (JSON)")
    print(f"  2. {txt_file} - przykłady (TXT)")
    print("\n" + "="*60)

    return output_data


if __name__ == '__main__':
    export_polish_texts()
