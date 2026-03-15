# -*- coding: utf-8 -*-
"""
Diagnozuje strukturę pliku BBB - porównuje oryginalny z naszym
"""

import struct
import os


def analyze_bbb_structure(file_path, name):
    """Analizuje strukturę pliku BBB"""

    print("="*60)
    print(f"ANALIZA: {name}")
    print("="*60)

    with open(file_path, 'rb') as f:
        # Nagłówek
        print("\n[NAGŁÓWEK]")
        magic = f.read(4)
        print(f"Magic: {magic}")

        if magic == b'BBBB':
            unknown1 = struct.unpack('<I', f.read(4))[0]
            unknown2 = struct.unpack('<I', f.read(4))[0]
            unknown3 = struct.unpack('<I', f.read(4))[0]
            unknown4 = struct.unpack('<I', f.read(4))[0]
            offset1 = struct.unpack('<I', f.read(4))[0]
            offset2 = struct.unpack('<I', f.read(4))[0]

            print(f"Unknown1: {unknown1}")
            print(f"Unknown2 (entry count?): {unknown2}")
            print(f"Unknown3: {unknown3}")
            print(f"Unknown4: {unknown4}")
            print(f"Offset1 (data start?): {offset1}")
            print(f"Offset2: {offset2}")

        # Przejdź do danych (offset 28)
        f.seek(28)

        print("\n[PIERWSZE 500 BAJTÓW DANYCH]")

        data = f.read(500)

        # Szukaj pierwszego tekstu UTF-16
        print("\nSzukam pierwszego tekstu UTF-16...")

        for offset in range(0, 200, 2):
            try:
                # Próbuj odczytać jako UTF-16
                test_bytes = data[offset:offset+100]
                text = test_bytes.decode('utf-16-le', errors='strict')

                # Sprawdź czy to sensowny tekst
                if len(text) > 5 and all(32 <= ord(c) < 127 or ord(c) > 127 for c in text[:10] if c != '\x00'):
                    print(f"\nOffset {28 + offset}: Znaleziono tekst!")
                    print(f"  Pierwsze 80 znaków: {text[:80]}")

                    # Pokaż surowe bajty
                    print(f"  Hex: {data[offset:offset+40].hex()}")
                    break
            except:
                pass

        # Analiza statystyczna
        print("\n[STATYSTYKI]")

        f.seek(0, 2)  # Koniec pliku
        file_size = f.tell()
        print(f"Rozmiar pliku: {file_size / 1024 / 1024:.2f} MB")

        f.seek(0)
        all_data = f.read()

        # Policz null bytes
        null_count = all_data.count(b'\x00')
        print(f"Null bytes: {null_count} ({null_count/len(all_data)*100:.1f}%)")

        # Szukaj polskich znaków
        try:
            text_data = all_data.decode('utf-16-le', errors='ignore')
            has_polish = any(c in text_data for c in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
            print(f"Ma polskie znaki: {has_polish}")

            if has_polish:
                import re
                polish_words = re.findall(r'[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]{5,}', text_data)
                print(f"Przykłady polskich słów: {polish_words[:10]}")
        except:
            print("Nie można zdekodować jako UTF-16")


def compare_hex(file1, file2, offset, length=100):
    """Porównuje hex dump dwóch plików od danego offsetu"""

    print("\n" + "="*60)
    print(f"PORÓWNANIE HEX (offset {offset}, {length} bajtów)")
    print("="*60)

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        f1.seek(offset)
        f2.seek(offset)

        data1 = f1.read(length)
        data2 = f2.read(length)

        print(f"\n{os.path.basename(file1)}:")
        print(data1.hex())
        print(f"\nTekst: {data1.decode('utf-16-le', errors='ignore')[:50]}")

        print(f"\n{os.path.basename(file2)}:")
        print(data2.hex())
        print(f"\nTekst: {data2.decode('utf-16-le', errors='ignore')[:50]}")

        if data1 == data2:
            print("\n✓ IDENTYCZNE")
        else:
            print("\n✗ RÓŻNE")
            # Znajdź pierwszy różny bajt
            for i in range(min(len(data1), len(data2))):
                if data1[i] != data2[i]:
                    print(f"  Pierwszy różny bajt na pozycji {i}: {data1[i]:02x} vs {data2[i]:02x}")
                    break


def main():
    """Główna funkcja"""

    original = "English/text.bbb"
    our_file = "polish_text_exact.bbb"

    if not os.path.exists(original):
        print(f"BŁĄD: Nie znaleziono {original}")
        print("Skopiuj oryginalny text.bbb z gry do katalogu English/")
        return

    if not os.path.exists(our_file):
        print(f"BŁĄD: Nie znaleziono {our_file}")
        return

    # Analizuj oba pliki
    analyze_bbb_structure(original, "ORYGINALNY (English)")
    print("\n\n")
    analyze_bbb_structure(our_file, "NASZ (polish_text_exact)")

    # Porównaj pierwsze bajty danych
    compare_hex(original, our_file, offset=28, length=200)

    # Porównaj środek pliku
    compare_hex(original, our_file, offset=1000000, length=200)


if __name__ == '__main__':
    main()
