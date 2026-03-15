# -*- coding: utf-8 -*-
"""
GUI Viewer dla plików BBB
Pozwala przeglądać i wyszukiwać teksty
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from fable_text_parser import FableTextBigParser
import re


class TextViewerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fable Text Viewer - BBB Parser")
        self.root.geometry("1200x800")

        self.current_file = None
        self.all_entries = []
        self.filtered_entries = []

        self.setup_ui()

    def setup_ui(self):
        """Tworzy interfejs"""

        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Otwórz BBB...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)

        # Górny panel - info o pliku
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        self.file_label = ttk.Label(top_frame, text="Nie załadowano pliku", font=("Arial", 10, "bold"))
        self.file_label.pack(side=tk.LEFT)

        self.stats_label = ttk.Label(top_frame, text="", font=("Arial", 9))
        self.stats_label.pack(side=tk.RIGHT)

        # Panel wyszukiwania
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Szukaj:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_entries())

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(search_frame, text="Wyczyść", command=self.clear_search).pack(side=tk.LEFT)

        self.polish_only_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="Tylko polskie", variable=self.polish_only_var,
                       command=self.filter_entries).pack(side=tk.LEFT, padx=(20, 0))

        # Panel główny z podziałem
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lista tekstów (lewa strona)
        list_frame = ttk.Frame(main_paned)
        main_paned.add(list_frame, weight=1)

        ttk.Label(list_frame, text="Lista tekstów:", font=("Arial", 9, "bold")).pack(anchor=tk.W)

        # Scrollbar + Listbox
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, font=("Consolas", 9))
        self.text_listbox.pack(fill=tk.BOTH, expand=True)
        self.text_listbox.bind('<<ListboxSelect>>', self.on_select)

        list_scroll.config(command=self.text_listbox.yview)

        # Panel szczegółów (prawa strona)
        detail_frame = ttk.Frame(main_paned)
        main_paned.add(detail_frame, weight=2)

        ttk.Label(detail_frame, text="Szczegóły:", font=("Arial", 9, "bold")).pack(anchor=tk.W)

        # Info o wybranym tekście
        self.detail_info = ttk.Label(detail_frame, text="", font=("Arial", 9))
        self.detail_info.pack(anchor=tk.W, pady=(5, 10))

        # Treść tekstu
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD,
                                                      font=("Arial", 11), height=20)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Gotowy", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file(self):
        """Otwiera plik BBB"""
        filename = filedialog.askopenfilename(
            title="Wybierz plik BBB",
            filetypes=[("BBB files", "*.bbb"), ("All files", "*.*")]
        )

        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Ładuje i parsuje plik"""
        try:
            self.status_bar.config(text=f"Ładowanie {filename}...")
            self.root.update()

            # Parsuj
            parser = FableTextBigParser(filename)
            entries = parser.parse()

            # Zbierz wszystkie sub-entries
            self.all_entries = []
            polish_count = 0

            for entry in entries:
                for sub in entry.sub_entries:
                    has_polish = any(c in sub.content for c in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')

                    self.all_entries.append({
                        'name': sub.name,
                        'content': sub.content,
                        'entry_name': entry.name,
                        'has_polish': has_polish
                    })

                    if has_polish:
                        polish_count += 1

            self.current_file = filename
            self.file_label.config(text=f"Plik: {os.path.basename(filename)}")

            total = len(self.all_entries)
            english_count = total - polish_count

            self.stats_label.config(
                text=f"Tekstów: {total} | Polskie: {polish_count} ({polish_count/total*100:.1f}%) | Angielskie: {english_count}"
            )

            self.filter_entries()
            self.status_bar.config(text=f"Załadowano: {filename}")

            messagebox.showinfo("Sukces", f"Załadowano {total} tekstów\n{polish_count} po polsku")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować pliku:\n{e}")
            self.status_bar.config(text="Błąd ładowania")

    def filter_entries(self):
        """Filtruje listę według wyszukiwania"""
        search_text = self.search_var.get().lower()
        polish_only = self.polish_only_var.get()

        self.filtered_entries = []

        for entry in self.all_entries:
            # Filtr polski
            if polish_only and not entry['has_polish']:
                continue

            # Filtr wyszukiwania
            if search_text:
                if (search_text not in entry['name'].lower() and
                    search_text not in entry['content'].lower()):
                    continue

            self.filtered_entries.append(entry)

        # Aktualizuj listbox
        self.text_listbox.delete(0, tk.END)

        for entry in self.filtered_entries:
            # Format: nazwa | pierwsze 60 znaków treści
            display = f"{entry['name'][:30]:30} | {entry['content'][:60]}"
            self.text_listbox.insert(tk.END, display)

        self.status_bar.config(text=f"Znaleziono: {len(self.filtered_entries)} tekstów")

    def on_select(self, event):
        """Obsługa wyboru z listy"""
        selection = self.text_listbox.curselection()

        if not selection:
            return

        idx = selection[0]
        entry = self.filtered_entries[idx]

        # Pokaż info
        info_text = (
            f"Nazwa: {entry['name']}\n"
            f"Entry: {entry['entry_name']}\n"
            f"Język: {'Polski 🇵🇱' if entry['has_polish'] else 'Angielski'}\n"
            f"Długość: {len(entry['content'])} znaków"
        )
        self.detail_info.config(text=info_text)

        # Pokaż treść
        self.detail_text.delete('1.0', tk.END)
        self.detail_text.insert('1.0', entry['content'])

        # Highlight polskich znaków
        if entry['has_polish']:
            content = entry['content']
            for i, char in enumerate(content):
                if char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ':
                    self.detail_text.tag_add('polish', f'1.{i}', f'1.{i+1}')

            self.detail_text.tag_config('polish', foreground='red', font=("Arial", 11, "bold"))

    def clear_search(self):
        """Czyści wyszukiwanie"""
        self.search_var.set("")
        self.polish_only_var.set(False)


def main():
    """Uruchamia GUI"""
    root = tk.Tk()
    app = TextViewerGUI(root)

    # Sprawdź czy są argumenty (ścieżka do pliku)
    import sys
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        app.load_file(sys.argv[1])

    root.mainloop()


if __name__ == '__main__':
    main()
