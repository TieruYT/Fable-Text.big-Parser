# -*- coding: utf-8 -*-
"""
Czyści i filtruje teksty Anniversary - zostawia tylko sensowne angielskie teksty
"""

import re


def is_valid_text(text):
    """Sprawdza czy tekst jest sensownym angielskim tekstem"""

    # Minimum długość
    if len(text) < 10:
        return False

    # Maximum długość
    if len(text) > 2000:
        return False

    # Sprawdź czy większość znaków to ASCII
    ascii_count = sum(1 for c in text if ord(c) < 128)
    if ascii_count / len(text) < 0.8:  # Minimum 80% ASCII
        return False

    # Sprawdź czy nie ma dziwnych znaków
    # Dozwolone: litery, cyfry, podstawowa interpunkcja, spacje, newline
    allowed_pattern = re.compile(r'^[a-zA-Z0-9\s.,!?\'";\-:\[\]\(\)]+$')

    if not allowed_pattern.match(text):
        # Jeśli nie pasuje, sprawdź czy ma chociaż podstawowe angielskie słowa
        common_words = ['the', 'and', 'you', 'to', 'of', 'a', 'in', 'is', 'that', 'for']
        text_lower = text.lower()

        word_count = sum(1 for word in common_words if word in text_lower)
        if word_count < 2:
            return False

    # Sprawdź czy to nie jest sam kod/hash
    if text.startswith('0x') and len(text) < 20:
        return False

    # Sprawdź czy to nie jest nazwa pliku
    if text.endswith('.lug') or text.endswith('.bbb'):
        return False

    # Sprawdź czy zawiera przynajmniej jedno słowo z literami
    if not re.search(r'[a-zA-Z]{3,}', text):
        return False

    return True


def clean_texts(input_file, output_file):
    """Czyści teksty z pliku"""

    print("="*60)
    print("CZYSZCZENIE TEKSTÓW ANNIVERSARY")
    print("="*60)

    print(f"\nCzytanie: {input_file}")

    texts_raw = []
    current_text = None

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            if line.startswith('[') and '] Offset:' in line:
                # Nowy wpis
                if current_text:
                    texts_raw.append(current_text)
                current_text = ""
            elif current_text is not None and line and not line.startswith('='):
                current_text += line + "\n"

        # Dodaj ostatni
        if current_text:
            texts_raw.append(current_text)

    print(f"Wczytano {len(texts_raw)} surowych tekstów")

    # Filtruj
    print("\nFiltrowanie...")

    valid_texts = []
    seen = set()

    for text in texts_raw:
        text = text.strip()

        if is_valid_text(text):
            # Usuń duplikaty
            text_normalized = text.lower().replace(' ', '')

            if text_normalized not in seen:
                valid_texts.append(text)
                seen.add(text_normalized)

    print(f"Po filtrowaniu: {len(valid_texts)} unikalnych tekstów")

    # Zapisz
    print(f"\nZapisywanie do: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("OCZYSZCZONE TEKSTY Z FABLE ANNIVERSARY\n")
        f.write(f"Liczba tekstów: {len(valid_texts)}\n")
        f.write("="*80 + "\n\n")

        for i, text in enumerate(valid_texts, 1):
            f.write(f"[{i}]\n")
            f.write(f"{text}\n\n")

    print(f"Zapisano {len(valid_texts)} tekstów")

    # Statystyki
    total_chars = sum(len(t) for t in valid_texts)
    avg_length = total_chars / len(valid_texts) if valid_texts else 0

    print("\n" + "="*60)
    print("STATYSTYKI")
    print("="*60)
    print(f"Unikalne teksty: {len(valid_texts)}")
    print(f"Średnia długość: {avg_length:.1f} znaków")
    print(f"Najkrótszy: {min(len(t) for t in valid_texts)} znaków")
    print(f"Najdłuższy: {max(len(t) for t in valid_texts)} znaków")
    print("="*60)

    return valid_texts


def main():
    """Główna funkcja"""

    input_file = "anniversary_texts_all.txt"
    output_file = "anniversary_texts_clean.txt"

    texts = clean_texts(input_file, output_file)

    print("\n" + "="*60)
    print("SUKCES!")
    print("="*60)
    print(f"\nPlik: {output_file}")
    print(f"Teksty: {len(texts)}")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
