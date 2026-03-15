# -*- coding: utf-8 -*-
"""
GUI dla parsera plików text.big (TLC) i text.bbb (Anniversary)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import csv
from fable_text_parser import FableTextBigParser


class FableTextGUI:
    """Główne okno GUI dla parsera Fable"""

    def __init__(self, root):
        self.root = root
        self.root.title("Fable Text Parser (TLC & Anniversary)")
        self.root.geometry("1200x700")

        self.parser = None
        self.entries = []
        self.current_file = None
        self.entry_map = {}  # Mapowanie item_id -> entry object
        self.sub_entry_map = {}  # Mapowanie item_id -> sub_entry object

        self.setup_ui()

    def setup_ui(self):
        """Tworzy interfejs użytkownika"""

        # Menu górne
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Plik", menu=file_menu)
        file_menu.add_command(label="Otwórz plik tekstowy...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Eksportuj TYLKO DIALOGI do TXT...", command=self.export_dialogues_only)
        file_menu.add_separator()
        file_menu.add_command(label="Eksportuj wszystko do JSON...", command=lambda: self.export_all("json"))
        file_menu.add_command(label="Eksportuj wszystko do TXT...", command=lambda: self.export_all("txt"))
        file_menu.add_command(label="Eksportuj wszystko do CSV...", command=lambda: self.export_all("csv"))
        file_menu.add_separator()
        file_menu.add_command(label="Wyjście", command=self.root.quit)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Otwórz plik", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Odśwież", command=self.refresh).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Label(toolbar, text="Wyszukaj:").pack(side=tk.LEFT, padx=2)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(toolbar, text="Gotowy")
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Panel główny (PanedWindow)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lewa strona - lista wpisów
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Wpisy główne:").pack(anchor=tk.W, pady=2)

        # Treeview dla wpisów
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("id", "size"), show="tree headings")
        self.tree.heading("#0", text="Nazwa")
        self.tree.heading("id", text="ID")
        self.tree.heading("size", text="Sub-wpisy")
        self.tree.column("#0", width=250)
        self.tree.column("id", width=80)
        self.tree.column("size", width=80)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Prawa strona - zawartość
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Zawartość:").pack(anchor=tk.W, pady=2)

        # Notebook dla różnych widoków
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Lista sub-wpisów
        sub_frame = ttk.Frame(self.notebook)
        self.notebook.add(sub_frame, text="Sub-wpisy")

        sub_tree_frame = ttk.Frame(sub_frame)
        sub_tree_frame.pack(fill=tk.BOTH, expand=True)

        self.sub_tree = ttk.Treeview(sub_tree_frame, columns=("content",), show="tree headings")
        self.sub_tree.heading("#0", text="Nazwa")
        self.sub_tree.heading("content", text="Podgląd treści")
        self.sub_tree.column("#0", width=200)
        self.sub_tree.column("content", width=400)

        sub_scroll = ttk.Scrollbar(sub_tree_frame, orient=tk.VERTICAL, command=self.sub_tree.yview)
        self.sub_tree.configure(yscrollcommand=sub_scroll.set)

        self.sub_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sub_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.sub_tree.bind("<<TreeviewSelect>>", self.on_sub_tree_select)

        # Tab 2: Pełna treść
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Pełna treść")

        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=60, height=30)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Przyciski eksportu na dole
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(fill=tk.X, pady=5)

        ttk.Button(export_frame, text="Eksportuj wybrane do JSON",
                  command=lambda: self.export_selected("json")).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="Eksportuj wybrane do TXT",
                  command=lambda: self.export_selected("txt")).pack(side=tk.LEFT, padx=2)

    def open_file(self):
        """Otwiera plik text.big lub text.bbb"""
        filename = filedialog.askopenfilename(
            title="Wybierz plik tekstowy Fable",
            filetypes=[
                ("Fable text files", "*.big *.bbb"),
                ("TLC files", "*.big"),
                ("Anniversary files", "*.bbb"),
                ("All files", "*.*")
            ]
        )

        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Ładuje i parsuje plik"""
        try:
            self.status_label.config(text="Parsowanie...")
            self.root.update()

            self.parser = FableTextBigParser(filename)
            self.entries = self.parser.parse()
            self.current_file = filename

            self.populate_tree()

            self.status_label.config(text=f"Załadowano {len(self.entries)} wpisów z {filename}")
            messagebox.showinfo("Sukces", f"Pomyślnie załadowano {len(self.entries)} wpisów!")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować pliku:\n{str(e)}")
            self.status_label.config(text="Błąd")

    def populate_tree(self):
        """Wypełnia drzewo wpisami"""
        # Wyczyść drzewo i mapowanie
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.entry_map.clear()
        self.sub_entry_map.clear()

        # Dodaj sub-wpisy bezpośrednio do drzewa (nie główne wpisy)
        for entry in self.entries:
            for sub_entry in entry.sub_entries:
                # Podgląd treści
                preview = sub_entry.content[:50] + "..." if len(sub_entry.content) > 50 else sub_entry.content
                preview = preview.replace("\n", " ").replace("\r", " ")

                item_id = self.tree.insert("", tk.END, text=sub_entry.name,
                                         values=("", preview))
                self.sub_entry_map[item_id] = sub_entry

    def on_tree_select(self, event):
        """Obsługuje wybór wpisu w drzewie"""
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        sub_entry = self.sub_entry_map.get(item_id)

        if sub_entry:
            self.display_sub_entry(sub_entry)

    def display_entry(self, entry):
        """Wyświetla zawartość wybranego wpisu"""
        # Wyczyść sub-drzewo i mapowanie
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
        self.sub_entry_map.clear()

        # Dodaj sub-wpisy
        for sub_entry in entry.sub_entries:
            preview = sub_entry.content[:100] + "..." if len(sub_entry.content) > 100 else sub_entry.content
            preview = preview.replace("\n", " ").replace("\r", " ")

            item_id = self.sub_tree.insert("", tk.END, text=sub_entry.name,
                               values=(preview,))
            self.sub_entry_map[item_id] = sub_entry

        # Wyświetl wszystkie sub-wpisy w text area
        self.text_area.delete(1.0, tk.END)

        text_content = f"=== {entry.name} ===\n"
        text_content += f"ID: {entry.text_id}\n"
        text_content += f"Liczba sub-wpisów: {len(entry.sub_entries)}\n\n"

        for i, sub_entry in enumerate(entry.sub_entries, 1):
            text_content += f"--- [{i}] {sub_entry.name} ---\n"
            text_content += f"{sub_entry.content}\n\n"

        self.text_area.insert(1.0, text_content)

    def display_sub_entry(self, sub_entry):
        """Wyświetla pojedynczy sub-wpis"""
        # Wyczyść sub-drzewo (nie używamy go w tym widoku)
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)

        # Wyświetl sub-wpis w text area
        self.text_area.delete(1.0, tk.END)
        text_content = f"=== {sub_entry.name} ===\n\n"
        text_content += sub_entry.content
        self.text_area.insert(1.0, text_content)

    def on_sub_tree_select(self, event):
        """Obsługuje wybór sub-wpisu"""
        selection = self.sub_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        sub_entry = self.sub_entry_map.get(item_id)

        if not sub_entry:
            return

        # Wyświetl pełną treść sub-wpisu
        self.text_area.delete(1.0, tk.END)
        text_content = f"=== {sub_entry.name} ===\n\n"
        text_content += sub_entry.content
        self.text_area.insert(1.0, text_content)

        # Przełącz na tab z pełną treścią
        self.notebook.select(1)

    def on_search(self, *args):
        """Obsługuje wyszukiwanie"""
        search_text = self.search_var.get().lower()

        # Wyczyść drzewo i mapowanie
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.sub_entry_map.clear()

        # Filtruj i dodaj sub-wpisy
        for entry in self.entries:
            for sub_entry in entry.sub_entries:
                if (not search_text or
                    search_text in sub_entry.name.lower() or
                    search_text in sub_entry.content.lower()):

                    # Podgląd treści
                    preview = sub_entry.content[:50] + "..." if len(sub_entry.content) > 50 else sub_entry.content
                    preview = preview.replace("\n", " ").replace("\r", " ")

                    item_id = self.tree.insert("", tk.END, text=sub_entry.name,
                                             values=("", preview))
                    self.sub_entry_map[item_id] = sub_entry

    def refresh(self):
        """Odświeża widok"""
        if self.current_file:
            self.load_file(self.current_file)

    def export_selected(self, format_type):
        """Eksportuje wybrany wpis"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Brak wyboru", "Proszę wybrać wpis do eksportu")
            return

        item_id = selection[0]
        entry = self.entry_map.get(item_id)

        if not entry:
            messagebox.showerror("Błąd", "Nie można znaleźć wybranego wpisu")
            return

        if format_type == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"{entry.name}.json"
            )
            if filename:
                self.export_entry_to_json([entry], filename)

        elif format_type == "txt":
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"{entry.name}.txt"
            )
            if filename:
                self.export_entry_to_txt([entry], filename)

    def export_dialogues_only(self):
        """Eksportuje tylko dialogi (ScriptDialogue.lug) do TXT"""
        if not self.entries:
            messagebox.showwarning("Brak danych", "Proszę najpierw załadować plik text.big")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="fable_dialogues_only.txt"
        )

        if not filename:
            return

        try:
            import re
            dialogue_count = 0
            cleaned_count = 0

            with open(filename, 'w', encoding='utf-8') as f:
                for entry in self.entries:
                    for sub_entry in entry.sub_entries:
                        # Filtruj tylko dialogi (zawierają "Dialogue" w nazwie)
                        if 'Dialogue' in sub_entry.name:
                            content = sub_entry.content

                            # Usuń chińskie znaki i nietypowe znaki Unicode (metadane/błędy parsowania)
                            original_len = len(content)

                            # Krok 1: Usuń CJK (chiński/japoński/koreański), nietypowe znaki Unicode
                            content = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf\uf000-\uffff\u2000-\u206f]', '', content)

                            # Krok 2: Usuń wielkie litery metadanych na początku
                            # - Usuń sekwencje 2+ wielkich liter ze spacją (np. "ABC test" → "test")
                            content = re.sub(r'^[A-Z]{2,}\s+', '', content)
                            # - Usuń pojedynczą wielką literę TYLKO jeśli poprzedza kolejną wielką (np. "RPowodzenia" → "Powodzenia")
                            content = re.sub(r'^[A-Z](?=[A-Z])', '', content)

                            # Krok 3: Usuń nadmiarowe spacje i znaki białe
                            content = ' '.join(content.split())

                            if len(content) < original_len:
                                cleaned_count += 1

                            # Zapisz tylko jeśli po czyszczeniu coś zostało
                            if content.strip():
                                f.write(f"{content}\n")
                                dialogue_count += 1

            msg = f"Wyeksportowano {dialogue_count} dialogów do {filename}"
            if cleaned_count > 0:
                msg += f"\n\nWyczyszczono {cleaned_count} dialogów z niepoprawnych znaków."
            messagebox.showinfo("Sukces", msg)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyeksportować:\n{str(e)}")

    def export_all(self, format_type):
        """Eksportuje wszystkie wpisy"""
        if not self.entries:
            messagebox.showwarning("Brak danych", "Proszę najpierw załadować plik text.big")
            return

        if format_type == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="fable_dialogs.json"
            )
            if filename:
                self.export_entry_to_json(self.entries, filename)

        elif format_type == "txt":
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="fable_dialogs.txt"
            )
            if filename:
                self.export_entry_to_txt(self.entries, filename)

        elif format_type == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="fable_dialogs.csv"
            )
            if filename:
                self.export_entry_to_csv(self.entries, filename)

    def export_entry_to_json(self, entries, filename):
        """Eksportuje wpisy do JSON"""
        try:
            data = []
            for entry in entries:
                entry_data = {
                    "name": entry.name,
                    "text_id": entry.text_id,
                    "type_id": entry.type_id,
                    "sub_entries": []
                }

                for sub_entry in entry.sub_entries:
                    entry_data["sub_entries"].append({
                        "name": sub_entry.name,
                        "content": sub_entry.content
                    })

                data.append(entry_data)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Sukces", f"Wyeksportowano {len(entries)} wpisów do {filename}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyeksportować:\n{str(e)}")

    def export_entry_to_txt(self, entries, filename):
        """Eksportuje wpisy do TXT - tylko same teksty, linia po linii"""
        try:
            total_texts = 0
            with open(filename, 'w', encoding='utf-8') as f:
                for entry in entries:
                    for sub_entry in entry.sub_entries:
                        # Zapisz tylko sam tekst, każdy w osobnej linii
                        f.write(f"{sub_entry.content}\n")
                        total_texts += 1

            messagebox.showinfo("Sukces", f"Wyeksportowano {total_texts} tekstów do {filename}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyeksportować:\n{str(e)}")

    def export_entry_to_csv(self, entries, filename):
        """Eksportuje wpisy do CSV"""
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Entry Name", "Entry ID", "Type ID", "Sub-Entry Name", "Content"])

                for entry in entries:
                    if entry.sub_entries:
                        for sub_entry in entry.sub_entries:
                            writer.writerow([
                                entry.name,
                                entry.text_id,
                                entry.type_id,
                                sub_entry.name,
                                sub_entry.content
                            ])
                    else:
                        writer.writerow([entry.name, entry.text_id, entry.type_id, "", ""])

            messagebox.showinfo("Sukces", f"Wyeksportowano {len(entries)} wpisów do {filename}")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyeksportować:\n{str(e)}")


def main():
    root = tk.Tk()
    app = FableTextGUI(root)

    # Jeśli plik text.big istnieje w tym samym katalogu, załaduj go automatycznie
    import os
    if os.path.exists("text.big"):
        root.after(100, lambda: app.load_file("text.big"))

    root.mainloop()


if __name__ == '__main__':
    main()
