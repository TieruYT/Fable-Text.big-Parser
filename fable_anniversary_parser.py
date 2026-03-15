# -*- coding: utf-8 -*-
"""
Zoptymalizowany parser dla Fable Anniversary używający plików indeksowych
"""

import struct
import os
from fable_text_parser import FableTextEntry, FableTextSubEntry


class FableAnniversaryParser:
    """Parser dla Fable Anniversary używający .ipbe/.iple index files"""

    def __init__(self, bbb_file, index_file=None):
        self.bbb_file = bbb_file

        # Automatycznie znajdź plik indeksowy jeśli nie podano
        if index_file is None:
            base = bbb_file.rsplit('.', 1)[0]
            # Sprawdź .ipbe
            if os.path.exists(base + '.ipbe'):
                index_file = base + '.ipbe'
            elif os.path.exists(base + '.iple'):
                index_file = base + '.iple'
            else:
                raise FileNotFoundError("Nie znaleziono pliku indeksowego (.ipbe lub .iple)")

        self.index_file = index_file
        self.index_map = {}
        print(f"Używam pliku indeksowego: {self.index_file}")

    def parse_index(self):
        """Parsuje plik indeksowy"""
        print("Parsowanie pliku indeksowego...")

        with open(self.index_file, 'rb') as f:
            # Pomiń nagłówek (16 bajtów)
            f.seek(16)

            file_size = os.path.getsize(self.index_file)
            entry_count = 0

            while f.tell() < file_size - 8:
                try:
                    hash_id = struct.unpack('<I', f.read(4))[0]
                    offset = struct.unpack('<I', f.read(4))[0]

                    # Walidacja offsetu
                    if offset < 10000000:  # max 10MB
                        self.index_map[hash_id] = offset
                        entry_count += 1
                except:
                    break

            print(f"Załadowano {entry_count} wpisów z indeksu")
            return self.index_map

    def find_utf16_text_start(self, data, max_search=100):
        """Znajduje początek tekstu UTF-16 LE w danych"""
        # Szukaj DŁUGIEGO ciągu drukowalnych znaków UTF-16 LE
        best_offset = None
        best_score = 0

        # Sprawdź PARZYSTE offsety (UTF-16 jest wyrównany do 2 bajtów)
        for offset in range(0, min(max_search, len(data) - 40), 2):
            valid_chars = 0
            consecutive_printable = 0
            pos = offset

            # Liczy CIĄGŁE drukowalne znaki (bez przerw)
            while pos < len(data) - 1:
                char_bytes = data[pos:pos+2]

                if char_bytes == b'\x00\x00':
                    break

                try:
                    char = char_bytes.decode('utf-16-le', errors='strict')

                    # Sprawdź czy to drukowalny znak ASCII (litera/cyfra/znak interpunkcyjny)
                    if 32 <= ord(char) < 127:
                        consecutive_printable += 1
                        valid_chars += 1
                    elif ord(char) > 127 and ord(char) < 0x0400:  # Unicode w rozsądnym zakresie
                        consecutive_printable += 1
                        valid_chars += 0.5
                    else:
                        # Przerwanie ciągu - jeśli był krótki, to nie jest tekst
                        if consecutive_printable < 8:
                            valid_chars = 0
                        break
                except:
                    if consecutive_printable < 8:
                        valid_chars = 0
                    break

                pos += 2

                if valid_chars > 30:  # Już wystarczająco dużo
                    break

            # Zapisz najlepszy wynik (wymaga minimum 8 kolejnych drukowalnych znaków)
            if valid_chars >= 8 and consecutive_printable >= 8:
                if valid_chars > best_score:
                    best_score = valid_chars
                    best_offset = offset

        return best_offset

    def read_text_at_offset(self, f, offset):
        """Czyta tekst UTF-16 LE z danego offsetu"""
        try:
            # Offsety w .ipbe są prawdopodobnie względne względem danych (po nagłówku BBBB)
            # Nagłówek BBBB ma 28 bajtów
            actual_offset = offset + 28

            f.seek(actual_offset)

            # Czytaj pierwsze 200 bajtów aby znaleźć początek tekstu
            header_data = f.read(200)

            # Znajdź gdzie zaczyna się tekst UTF-16
            text_start = self.find_utf16_text_start(header_data)

            if text_start is None:
                return "[No text found]"

            # Wróć do właściwego miejsca
            f.seek(actual_offset + text_start)

            # Czytaj tekst UTF-16 LE do napotkania null terminatora
            chars = []

            for _ in range(10000):  # max 10000 znaków
                char_bytes = f.read(2)

                if len(char_bytes) < 2 or char_bytes == b'\x00\x00':
                    break

                try:
                    char = char_bytes.decode('utf-16-le', errors='ignore')
                    # Sprawdź czy to drukowalny znak
                    if char and ord(char) >= 32 and ord(char) != 0xFFFD:
                        chars.append(char)
                    elif ord(char) == 10 or ord(char) == 13:  # newline/carriage return
                        chars.append(char)
                    else:
                        # Jeśli nie jest drukowalny, sprawdź czy to koniec tekstu
                        if len(chars) > 3:  # Mamy już jakiś tekst
                            break
                except:
                    break

            text = ''.join(chars).strip()

            # Filtruj teksty GUI i inne śmieci
            if len(text) < 2:
                return "[Empty]"

            # Pomiń jeśli to TYLKO nazwa kategorii (bez innych znaków)
            if (text.startswith("TEXT_GUI_") or text.startswith("TEXT_TLC_")) and len(text) < 50:
                # Sprawdź czy to TYLKO ID bez treści
                if ' ' not in text and '.' not in text:
                    return None  # Zwróć None aby pominąć ten wpis

            return text

        except Exception as e:
            return f"[Error: {e}]"

    def parse_all_texts(self, limit=None):
        """Parsuje wszystkie teksty używając indeksu"""
        if not self.index_map:
            self.parse_index()

        print(f"Parsowanie tekstów z {self.bbb_file}...")

        texts = []
        with open(self.bbb_file, 'rb') as f:
            # Sortuj offsety aby czytać sekwencyjnie
            sorted_items = sorted(self.index_map.items(), key=lambda x: x[1])

            # Ogranicz liczbę wpisów do parsowania (dla szybkiego testu)
            if limit:
                sorted_items = sorted_items[:limit]

            for hash_id, offset in sorted_items:
                text = self.read_text_at_offset(f, offset)

                # Pomiń None, puste, błędy i systemowe teksty
                if text and text not in ["[Empty]", "[No text found]", None]:
                    if not text.startswith("[Error:") and not text.startswith("[GUI"):
                        # Stwórz sub-entry z hash jako nazwa
                        sub_entry = FableTextSubEntry(f"0x{hash_id:08X}", text)
                        texts.append(sub_entry)

        print(f"Znaleziono {len(texts)} tekstów")
        return texts

    def export_to_txt(self, output_file, limit=None):
        """Eksportuje teksty do pliku TXT"""
        texts = self.parse_all_texts(limit=limit)

        with open(output_file, 'w', encoding='utf-8') as f:
            for sub in texts:
                f.write(f"[{sub.name}]\n")
                f.write(f"{sub.content}\n\n")

        print(f"Wyeksportowano {len(texts)} tekstów do {output_file}")


def test_anniversary_parser():
    """Test parsera Anniversary"""
    import sys

    if len(sys.argv) > 1:
        bbb_file = sys.argv[1]
    else:
        bbb_file = r'C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English\text.bbb'

    print(f"Parsowanie: {bbb_file}\n")

    parser = FableAnniversaryParser(bbb_file)

    # Parsuj tylko pierwsze 100 wpisów dla szybkiego testu
    texts = parser.parse_all_texts(limit=100)

    print(f"\n=== PRZYKŁADOWE TEKSTY (pierwsze 10) ===\n")
    for i, sub in enumerate(texts[:10]):
        print(f"[{i+1}] {sub.name}")
        preview = sub.content[:80] + "..." if len(sub.content) > 80 else sub.content
        print(f"    {preview}\n")


if __name__ == '__main__':
    test_anniversary_parser()
