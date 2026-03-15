# -*- coding: utf-8 -*-
"""
Writer dla formatu BBBB - tworzy polski text.bbb dla Fable Anniversary
"""

import struct
import os


class FableBBBWriter:
    """Writer dla pliku BBBB"""

    def __init__(self):
        self.entries = []

    def add_entry(self, name, content, hash_id=None):
        """Dodaje wpis tekstowy"""
        self.entries.append({
            'name': name,
            'content': content,
            'hash_id': hash_id
        })

    def write_utf16_string(self, text):
        """Konwertuje tekst do UTF-16 LE z null terminatorem"""
        return text.encode('utf-16-le') + b'\x00\x00'

    def write_sub_entry(self, name, content):
        """Zapisuje pojedynczy sub-entry"""
        data = bytearray()

        # 1. Treść w UTF-16 LE
        content_bytes = self.write_utf16_string(content)
        data.extend(content_bytes)

        # 2. Padding do wyrównania (optional - może nie być potrzebny)
        # Alignment do 4 bajtów
        while len(data) % 4 != 0:
            data.append(0)

        # 3. Długość nazwy
        name_bytes = name.encode('ascii') + b'\x00'
        name_length = len(name_bytes)
        data.extend(struct.pack('<I', name_length))

        # 4. Nazwa
        data.extend(name_bytes)

        # 5. Padding po nazwie
        while len(data) % 4 != 0:
            data.append(0)

        return bytes(data)

    def build_bbb(self, output_file):
        """Buduje kompletny plik BBB"""

        print(f"Budowanie pliku BBB: {output_file}")
        print(f"Liczba wpisów: {len(self.entries)}")

        # Nagłówek BBBB (28 bajtów)
        header = bytearray()
        header.extend(b'BBBB')  # Magic

        # Unknown values - skopiujemy z oryginalnego pliku
        # Na razie placeholder
        header.extend(struct.pack('<I', 0))  # Unknown1
        header.extend(struct.pack('<I', len(self.entries)))  # Unknown2 (prawdopodobnie entry count)
        header.extend(struct.pack('<I', 0))  # Unknown3
        header.extend(struct.pack('<I', 0))  # Unknown4
        header.extend(struct.pack('<I', 28))  # Offset1 (dane zaczynają się po nagłówku)
        header.extend(struct.pack('<I', 0))  # Offset2

        # Dane
        data_section = bytearray()

        # Separator na początku (2 bajty 0x0000)
        data_section.extend(b'\x00\x00')

        for entry in self.entries:
            sub_entry_data = self.write_sub_entry(entry['name'], entry['content'])
            data_section.extend(sub_entry_data)

        # Zapisz
        with open(output_file, 'wb') as f:
            f.write(header)
            f.write(data_section)

        print(f"Plik zapisany: {os.path.getsize(output_file)} bajtów")

    def build_index(self, output_file):
        """Buduje plik indeksowy (.ipbe)"""

        print(f"Budowanie pliku indeksowego: {output_file}")

        # Nagłówek (16 bajtów - placeholder)
        header = bytearray(16)

        # Index entries
        index_data = bytearray()

        current_offset = 0  # Offset względem początku danych (po nagłówku BBBB)

        for entry in self.entries:
            if entry['hash_id'] is None:
                continue

            # Hash ID
            index_data.extend(struct.pack('<I', entry['hash_id']))

            # Offset
            index_data.extend(struct.pack('<I', current_offset))

            # Oblicz rozmiar tego entry
            sub_entry_data = self.write_sub_entry(entry['name'], entry['content'])
            current_offset += len(sub_entry_data)

        # Zapisz
        with open(output_file, 'wb') as f:
            f.write(header)
            f.write(index_data)

        print(f"Plik indeksowy zapisany: {len(self.entries)} wpisów")


def test_writer():
    """Test writera"""

    print("="*60)
    print("TEST BBBB WRITER")
    print("="*60)

    writer = FableBBBWriter()

    # Dodaj przykładowe wpisy
    writer.add_entry("TEXT_TEST_1", "To jest testowy polski tekst!", hash_id=0x12345678)
    writer.add_entry("TEXT_TEST_2", "Gildia Bohaterów", hash_id=0x87654321)
    writer.add_entry("TEXT_TEST_3", "Dębowa Dolina - piękna wioska w Albion", hash_id=0xAABBCCDD)

    # Zapisz
    writer.build_bbb("test_output.bbb")
    writer.build_index("test_output.ipbe")

    print("\n" + "="*60)
    print("Test zakończony!")
    print("Sprawdź pliki: test_output.bbb, test_output.ipbe")
    print("="*60)


if __name__ == '__main__':
    test_writer()
