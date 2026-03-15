# -*- coding: utf-8 -*-
"""
Sprawdza format danych Anniversary
"""

from fable_anniversary_parser import FableAnniversaryParser
import os

ann_file = r"C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb"

print("Sprawdzanie formatu Anniversary...")
print("="*60)

parser = FableAnniversaryParser(ann_file)
texts = parser.parse_all_texts(limit=50)

print(f"\nZnaleziono {len(texts)} tekstów\n")
print("Przykładowe wpisy:\n")

for i, sub in enumerate(texts[:20], 1):
    print(f"{i}. Nazwa: {sub.name}")
    print(f"   Treść: {sub.content[:100]}")
    print()

# Sprawdź czy któryś ma format TEXT_*
text_format_count = sum(1 for sub in texts if sub.name.startswith('TEXT_'))
hash_format_count = sum(1 for sub in texts if sub.name.startswith('0x'))

print("="*60)
print("Analiza formatów nazw:")
print(f"  - Format TEXT_*: {text_format_count}")
print(f"  - Format 0x* (hash): {hash_format_count}")
print(f"  - Inne: {len(texts) - text_format_count - hash_format_count}")
print("="*60)

if hash_format_count > text_format_count:
    print("\n✗ Anniversary używa HASHÓW zamiast nazw tekstowych")
    print("  Potrzebujemy angielskiego text.big z TLC do mapowania")
else:
    print("\n✓ Anniversary używa tych samych nazw co TLC!")
    print("  Możliwa bezpośrednia migracja")
