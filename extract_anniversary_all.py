# -*- coding: utf-8 -*-
"""
Wyciąga WSZYSTKIE teksty z Fable Anniversary text.bbb
Używa bezpośredniego parsowania bez parsera indeksowego dla pełnej zawartości
"""

import struct
import os


def read_utf16_string_at(data, offset, max_length=10000):
    """Czyta string UTF-16 LE z danego offsetu"""
    chars = []
    pos = offset

    while pos + 1 < len(data) and len(chars) < max_length:
        char_bytes = data[pos:pos+2]

        if char_bytes == b'\x00\x00':
            break

        try:
            char = char_bytes.decode('utf-16-le', errors='ignore')
            if char and ord(char) >= 32 and ord(char) != 0xFFFD:
                chars.append(char)
            elif ord(char) == 10 or ord(char) == 13:
                chars.append(char)
            else:
                if len(chars) > 5:  # Jeśli mamy już jakiś tekst, zakończ
                    break
        except:
            break

        pos += 2

    return ''.join(chars).strip()


def scan_for_texts(file_path):
    """Skanuje plik BBB i wyciąga wszystkie teksty"""

    print("="*60)
    print("SKANOWANIE PLIKU ANNIVERSARY text.bbb")
    print("="*60)

    file_size = os.path.getsize(file_path)
    print(f"\nRozmiar pliku: {file_size / 1024 / 1024:.2f} MB")

    with open(file_path, 'rb') as f:
        # Sprawdź nagłówek
        magic = f.read(4)
        print(f"Magic: {magic}")

        if magic != b'BBBB':
            print("BŁĄD: To nie jest plik BBBB!")
            return []

        # Czytaj cały plik do pamięci (6.6 MB to OK)
        f.seek(0)
        data = f.read()

    print("\nSkanowanie w poszukiwaniu tekstów UTF-16...")
    print("To może potrwać 1-2 minuty...\n")

    texts = []
    found_positions = set()

    # Skanuj co 2 bajty (wyrównanie UTF-16)
    # Zaczynamy od offsetu 28 (po nagłówku BBBB)
    offset = 28
    step = 2

    last_percent = -1

    while offset < len(data) - 20:
        # Progress bar
        percent = int((offset / len(data)) * 100)
        if percent != last_percent and percent % 5 == 0:
            print(f"  Postęp: {percent}%", flush=True)
            last_percent = percent

        # Sprawdź czy to początek tekstu UTF-16
        # Szukamy co najmniej 3 kolejnych drukowalnych znaków
        valid_start = True

        for i in range(3):
            char_offset = offset + (i * 2)
            if char_offset + 1 >= len(data):
                valid_start = False
                break

            char_bytes = data[char_offset:char_offset+2]

            if char_bytes == b'\x00\x00':
                valid_start = False
                break

            try:
                char = char_bytes.decode('utf-16-le', errors='strict')
                if not (32 <= ord(char) < 127 or ord(char) > 127):
                    valid_start = False
                    break
            except:
                valid_start = False
                break

        if valid_start and offset not in found_positions:
            # Spróbuj wyciągnąć pełny tekst
            text = read_utf16_string_at(data, offset)

            # Filtruj śmieci
            if len(text) >= 5 and len(text) < 5000:  # Min 5 znaków, max 5000
                # Sprawdź czy to nie jest sam hash/ID
                if not (text.startswith('0x') and len(text) < 15):
                    texts.append({
                        'offset': offset,
                        'length': len(text),
                        'content': text[:200]  # Pierwsze 200 znaków
                    })
                    found_positions.add(offset)

                    # Pomiń do końca tego tekstu
                    offset += len(text) * 2
                    continue

        offset += step

    print(f"\n  Postęp: 100%")
    print(f"\nZnaleziono {len(texts)} tekstów!")

    return texts


def export_texts(texts, output_file):
    """Eksportuje teksty do pliku"""

    print(f"\nEksportowanie do: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TEKSTY Z FABLE ANNIVERSARY\n")
        f.write(f"Znaleziono: {len(texts)} tekstów\n")
        f.write("="*80 + "\n\n")

        for i, text_data in enumerate(texts, 1):
            f.write(f"[{i}] Offset: {text_data['offset']}\n")
            f.write(f"{text_data['content']}\n\n")

    print(f"Zapisano {len(texts)} tekstów")


def main():
    """Główna funkcja"""

    # Ścieżka do pliku Anniversary
    ann_file = "English/text.bbb"

    if not os.path.exists(ann_file):
        print(f"BŁĄD: Nie znaleziono pliku: {ann_file}")
        print("Upewnij się, że katalog 'English' zawiera text.bbb")
        return

    # Skanuj plik
    texts = scan_for_texts(ann_file)

    # Eksportuj
    if texts:
        output_file = "anniversary_texts_all.txt"
        export_texts(texts, output_file)

        print("\n" + "="*60)
        print("SUKCES!")
        print("="*60)
        print(f"\nWyeksportowano {len(texts)} tekstów")
        print(f"Plik: {output_file}")
        print("\n" + "="*60)
    else:
        print("\nNie znaleziono żadnych tekstów!")


if __name__ == '__main__':
    main()
