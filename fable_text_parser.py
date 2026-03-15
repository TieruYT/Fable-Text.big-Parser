# -*- coding: utf-8 -*-
"""
Parser pliku text.big z gry Fable: The Lost Chapters
"""

import struct
import os
from concurrent.futures import ThreadPoolExecutor
import multiprocessing


class FableTextEntry:
    """Reprezentuje pojedynczy wpis tekstowy"""
    def __init__(self, name, text_id, offset, size, type_id=0):
        self.name = name
        self.text_id = text_id
        self.offset = offset
        self.size = size
        self.type_id = type_id
        self.sub_entries = []  # Lista sub-wpisów


class FableTextSubEntry:
    """Reprezentuje sub-wpis wewnątrz głównego wpisu"""
    def __init__(self, name, content):
        self.name = name
        self.content = content


class FableTextBigParser:
    """Parser pliku text.big"""

    def __init__(self, filename):
        self.filename = filename
        self.entries = []
        self.file_size = os.path.getsize(filename)

    def parse(self):
        """Parsuje plik text.big i zwraca listę wpisów"""
        with open(self.filename, 'rb') as f:
            # Czytanie nagłówka
            magic = f.read(4)

            # Sprawdź format: BIGB (The Lost Chapters) lub BBBB (Anniversary)
            if magic == b'BIGB':
                print("Wykryto format: Fable - The Lost Chapters (BIGB)")
                version = struct.unpack('<I', f.read(4))[0]
                index_offset = struct.unpack('<I', f.read(4))[0]
                entry_count = struct.unpack('<I', f.read(4))[0]

                print(f"Wersja: {version}")
                print(f"Liczba wpisów: {entry_count}")
                print(f"Offset tablicy indeksów: {index_offset}")

            elif magic == b'BBBB':
                print("Wykryto format: Fable Anniversary (BBBB)")
                # BBBB ma inną strukturę - dane są od razu po nagłówku
                # Pomijamy resztę nagłówka (24 bajty)
                f.read(24)

                print("Format BBBB: Parsowanie bezpośrednie (bez index table)")
                print("UWAGA: Format BBBB jest prostszy - dane zaczynają się od razu po nagłówku")

                # Dla BBBB nie ma index table, parsujemy dane bezpośrednio
                # Stwórzmy jeden główny wpis zawierający wszystkie dane
                entry = FableTextEntry("BBBB_DATA", 0, 28, self.file_size - 28, 0)
                self._parse_entry_data(f, entry)
                self.entries = [entry]

                return self.entries

            else:
                raise ValueError(f"Nieprawidłowy format pliku - nieznana sygnatura: {magic}")

            # Czytanie tablicy indeksów (tylko dla BIGB)
            f.seek(index_offset)
            self.entries = self._parse_index_table(f, entry_count)

            # Czytanie danych tekstowych dla każdego wpisu
            for entry in self.entries:
                self._parse_entry_data(f, entry)

        return self.entries

    def _parse_index_table(self, f, count):
        """Parsuje tablicę indeksów"""
        entries = []

        for i in range(count):
            try:
                # Type ID
                type_id_bytes = f.read(4)
                if len(type_id_bytes) < 4:
                    break
                type_id = struct.unpack('<I', type_id_bytes)[0]

                # Nazwa (null-terminated)
                name = self._read_null_terminated_string(f)

                # Metadane
                text_id_bytes = f.read(4)
                if len(text_id_bytes) < 4:
                    break
                text_id = struct.unpack('<I', text_id_bytes)[0]

                offset_bytes = f.read(4)
                if len(offset_bytes) < 4:
                    break
                offset = struct.unpack('<I', offset_bytes)[0]

                size_bytes = f.read(4)
                if len(size_bytes) < 4:
                    break
                size = struct.unpack('<I', size_bytes)[0]

                unknown_bytes = f.read(4)
                if len(unknown_bytes) < 4:
                    break
                unknown = struct.unpack('<I', unknown_bytes)[0]

                entry = FableTextEntry(name, text_id, offset, size, type_id)
                entries.append(entry)

            except Exception as e:
                # Koniec tablicy indeksów
                break

        return entries

    def _read_null_terminated_string(self, f):
        """Czyta string zakończony nullem"""
        chars = []
        while True:
            byte = f.read(1)
            if not byte or byte == b'\x00':
                break
            chars.append(byte)
        return b''.join(chars).decode('ascii', errors='replace')

    def _parse_entry_data(self, f, entry):
        """Parsuje dane tekstowe dla danego wpisu"""
        if entry.offset >= self.file_size or entry.size == 0:
            return

        try:
            f.seek(entry.offset)
            data = f.read(entry.size)

            # Parsowanie sub-wpisów
            entry.sub_entries = self._parse_sub_entries(data)

        except Exception as e:
            print(f"Błąd podczas parsowania danych wpisu {entry.name}: {e}")

    def _parse_sub_entries(self, data):
        """Parsuje sub-wpisy wewnątrz sekcji danych"""
        sub_entries = []
        pos = 0

        # Pomiń separator na samym początku (2 bajty 0x0000)
        if pos + 2 <= len(data) and data[pos:pos+2] == b'\x00\x00':
            pos += 2

        while pos < len(data) - 10:
            try:
                # === 1. CZYTAJ TEKST UTF-16 LE ===
                content = self._read_utf16_string(data, pos)
                if not content:  # Jeśli nie ma treści, pomiń bajty zerowe
                    while pos < len(data) and data[pos] == 0:
                        pos += 1
                    # Jeśli nadal nie ma tekstu, sprawdź czy to długość nazwy
                    if pos + 4 <= len(data):
                        possible_name_len = struct.unpack('<I', data[pos:pos+4])[0]
                        if 0 < possible_name_len < 1000 and pos + 4 + possible_name_len <= len(data):
                            # To wygląda na długość nazwy - pomiń ten wpis
                            pos += 4 + possible_name_len
                    continue

                pos += len(content.encode('utf-16-le')) + 2  # +2 dla null terminator

                # === 2. POMIŃ PADDING ===
                while pos < len(data) and data[pos] == 0:
                    pos += 1

                # === 3. CZYTAJ DŁUGOŚĆ NAZWY ===
                if pos + 4 > len(data):
                    break

                name_length = struct.unpack('<I', data[pos:pos+4])[0]

                # Walidacja
                if name_length == 0 or name_length > 1000:
                    continue

                pos += 4

                # === 4. CZYTAJ NAZWĘ ===
                if pos + name_length > len(data):
                    break

                name_bytes = data[pos:pos+name_length]
                name = name_bytes.decode('ascii', errors='replace').rstrip('\x00')
                pos += name_length

                # === 5. DODAJ SUB-WPIS ===
                if name and content:
                    sub_entry = FableTextSubEntry(name, content)
                    sub_entries.append(sub_entry)

                # === 6. POMIŃ PADDING PO NAZWIE (przed następnym tekstem) ===
                while pos < len(data) and data[pos] == 0:
                    pos += 1

            except Exception as e:
                # Jeśli błąd, spróbuj znaleźć następny wpis
                pos += 1

        return sub_entries

    def _read_utf16_string(self, data, offset):
        """Czyta string w formacie UTF-16 LE do napotkania null terminator"""
        chars = []
        pos = offset

        while pos + 1 < len(data):
            # Czytaj 2 bajty (UTF-16 LE)
            char_bytes = data[pos:pos+2]

            # Sprawdź czy to null terminator
            if char_bytes == b'\x00\x00':
                break

            # Dekoduj znak
            try:
                char = char_bytes.decode('utf-16-le')
                chars.append(char)
            except:
                break

            pos += 2

        return ''.join(chars)


# Funkcja testowa
def test_parser():
    import sys

    # Jeśli podano plik jako argument, użyj go
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Domyślna ścieżka do Fable Anniversary
        filename = r'C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb'
        print(f"Używam domyślnej ścieżki: {filename}")
        print("Możesz podać własną ścieżkę: python fable_text_parser.py <ścieżka>\n")

    parser = FableTextBigParser(filename)
    entries = parser.parse()

    print(f"\n=== ZNALEZIONO {len(entries)} GŁÓWNYCH WPISÓW ===\n")

    # Wyświetl pierwsze kilka wpisów
    for i, entry in enumerate(entries[:5]):
        print(f"\n--- Wpis {i+1}: {entry.name} ---")
        print(f"ID: {entry.text_id}")
        print(f"Offset: {entry.offset}")
        print(f"Rozmiar: {entry.size}")
        print(f"Liczba sub-wpisów: {len(entry.sub_entries)}")

        # Wyświetl pierwsze 3 sub-wpisy
        for j, sub in enumerate(entry.sub_entries[:3]):
            print(f"  [{j+1}] {sub.name}")
            content_preview = sub.content[:50] + "..." if len(sub.content) > 50 else sub.content
            print(f"      {content_preview}")


if __name__ == '__main__':
    test_parser()
