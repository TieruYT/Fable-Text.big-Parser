# -*- coding: utf-8 -*-
"""
Parser plików indeksowych .ipbe i .iple z Fable Anniversary
"""

import struct
import os


class FableIndexParser:
    """Parser dla plików .ipbe/.iple"""

    def __init__(self, filename):
        self.filename = filename
        self.file_size = os.path.getsize(filename)
        self.index_map = {}  # hash/id -> offset

    def parse(self):
        """Parsuje plik indeksowy i zwraca mapę hash->offset"""
        with open(self.filename, 'rb') as f:
            # Czytaj nagłówek (jeśli istnieje)
            header = struct.unpack('<I', f.read(4))[0]
            print(f"Header/Magic: 0x{header:08X} ({header})")

            # Następne wartości
            val1 = struct.unpack('<I', f.read(4))[0]
            val2 = struct.unpack('<I', f.read(4))[0]
            val3 = struct.unpack('<I', f.read(4))[0]

            print(f"Val1: {val1} (0x{val1:08X})")
            print(f"Val2: {val2} (0x{val2:08X})")
            print(f"Val3: {val3} (0x{val3:08X})")

            # Sprawdź czy val1 lub val2 to rozmiar pliku
            if val1 == self.file_size or val1 == self.file_size - 8:
                print(f"Val1 wygląda na rozmiar pliku!")
            if val2 == self.file_size or val2 == self.file_size - 8:
                print(f"Val2 wygląda na rozmiar pliku!")

            # Wróć do początku po nagłówku (np. 16 bajtów)
            f.seek(16)

            # Parsuj pary (hash, offset)
            entry_count = 0
            while f.tell() < self.file_size - 8:
                try:
                    hash_id = struct.unpack('<I', f.read(4))[0]
                    offset = struct.unpack('<I', f.read(4))[0]

                    # Walidacja - offset powinien być w rozsądnym zakresie
                    if offset < 10000000:  # max 10MB offset
                        self.index_map[hash_id] = offset
                        entry_count += 1

                        # Pokaż pierwsze 10 wpisów
                        if entry_count <= 10:
                            print(f"Entry {entry_count}: Hash=0x{hash_id:08X}, Offset={offset}")

                except:
                    break

            print(f"\nZnaleziono {entry_count} wpisów w indeksie")
            return self.index_map

    def get_offset_by_hash(self, hash_id):
        """Zwraca offset dla danego hash ID"""
        return self.index_map.get(hash_id)


def test_index_parser():
    """Testuje parser indeksów"""
    import sys

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print("Użycie: python fable_index_parser.py <plik.ipbe>")
        return

    parser = FableIndexParser(filename)
    index_map = parser.parse()

    print(f"\n=== STATYSTYKI ===")
    print(f"Liczba wpisów: {len(index_map)}")
    if index_map:
        print(f"Pierwszy hash: 0x{min(index_map.keys()):08X}")
        print(f"Ostatni hash: 0x{max(index_map.keys()):08X}")


if __name__ == '__main__':
    test_index_parser()
