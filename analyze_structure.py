# -*- coding: utf-8 -*-
"""
Analiza struktury wpisów w text.bbb
"""

import struct


def analyze_entry_at_offset(filename, offset, count=10):
    """Analizuje strukturę wpisu na danym offsetie"""
    with open(filename, 'rb') as f:
        # Offset + nagłówek BBBB (28 bajtów)
        actual_offset = offset + 28
        f.seek(actual_offset)

        print(f"\n=== Analiza offsetu {offset} (plik: {actual_offset}) ===\n")

        # Czytaj pierwsze 200 bajtów i pokaż strukturę
        data = f.read(400)

        # Pokaż hex dump
        print("HEX dump pierwszych 200 bajtów:")
        for i in range(0, min(200, len(data)), 16):
            hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"{i:04x}:  {hex_part:<48}  {ascii_part}")

        print("\n" + "="*80)

        # Spróbuj zinterpretować pierwsze bajty jako różne struktury
        if len(data) >= 32:
            print("\nInterpretacja jako uint32 (little-endian):")
            for i in range(0, 32, 4):
                val = struct.unpack('<I', data[i:i+4])[0]
                print(f"  Offset +{i:2d}: {val:10d} (0x{val:08X})")

            # Spróbuj znaleźć tekst UTF-16 LE
            print("\nSzukanie tekstu UTF-16 LE:")
            for start_offset in range(0, 100, 4):
                try:
                    # Spróbuj czytać od tego offsetu
                    text_chars = []
                    pos = start_offset

                    while pos < len(data) - 1:
                        char_bytes = data[pos:pos+2]
                        if char_bytes == b'\x00\x00':
                            break

                        char = char_bytes.decode('utf-16-le', errors='ignore')
                        if char and 32 <= ord(char) < 127:  # ASCII drukowalny
                            text_chars.append(char)
                        else:
                            break

                        pos += 2

                        if len(text_chars) > 100:
                            break

                    if len(text_chars) > 20:
                        text = ''.join(text_chars)
                        print(f"\n  Offset +{start_offset}: Znaleziono tekst ({len(text_chars)} znaków)")
                        print(f"    Preview: {text[:80]}...")
                        break

                except:
                    continue


def test_multiple_offsets():
    """Testuje kilka różnych offsetów"""
    import sys

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = r'English\text.bbb'

    # Testuj kilka znanych offsetów z indeksu
    test_offsets = [
        203520,  # 0xB1A40900 - znany dobry offset
        0,       # Pierwszy wpis
        1000,    # Losowy offset
    ]

    for offset in test_offsets:
        try:
            analyze_entry_at_offset(filename, offset)
            input("\nNaciśnij Enter aby kontynuować do następnego offsetu...")
        except Exception as e:
            print(f"Błąd: {e}")


if __name__ == '__main__':
    test_multiple_offsets()
