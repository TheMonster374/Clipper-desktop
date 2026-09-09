from __future__ import annotations

import argparse
from pathlib import Path

try:
	import tkinter as tk
	from tkinter import filedialog, messagebox, ttk
except ModuleNotFoundError:
	tk = None
	filedialog = None
	messagebox = None
	ttk = None

import config
from database import DEFAULT_DB_PATH, create_tables, get_errors, get_history
from organizer import organize_downloads
from paths import downloads_dir


class ClipperApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Clipper - Organizador de archivos")
		self.root.minsize(760, 520)
		self.downloads = downloads_dir()
		self.rule_rows: list[tuple[tk.StringVar, tk.StringVar]] = []
		self._build_ui()

	def _build_ui(self) -> None:
		container = ttk.Frame(self.root, padding=16)
		container.pack(fill="both", expand=True)

		ttk.Label(container, text="Carpeta a organizar").pack(anchor="w")
		folder_row = ttk.Frame(container)
		folder_row.pack(fill="x", pady=(4, 12))
		self.folder_var = tk.StringVar(value=str(self.downloads))
		ttk.Entry(folder_row, textvariable=self.folder_var, state="readonly").pack(
			side="left", fill="x", expand=True
		)
		ttk.Button(folder_row, text="Cambiar...", command=self.choose_folder).pack(
			side="left", padx=(8, 0)
		)
		ttk.Button(folder_row, text="Organizar archivos", command=self.organize).pack(
			side="left", padx=(8, 0)
		)

		notebook = ttk.Notebook(container)
		notebook.pack(fill="both", expand=True)
		self.rules_frame = ttk.Frame(notebook, padding=8)
		self.history_frame = ttk.Frame(notebook, padding=8)
		self.errors_frame = ttk.Frame(notebook, padding=8)
		notebook.add(self.rules_frame, text="Reglas")
		notebook.add(self.history_frame, text="Historial")
		notebook.add(self.errors_frame, text="Errores")
		self._build_rules_tab()
		self._build_history_tab()
		self._build_errors_tab()

		self.status_var = tk.StringVar(value="Listo")
		ttk.Label(container, textvariable=self.status_var).pack(anchor="w", pady=(10, 0))

	def _build_rules_tab(self) -> None:
		ttk.Label(self.rules_frame, text="Extensión").grid(row=0, column=0, sticky="w")
		ttk.Label(self.rules_frame, text="Carpeta destino").grid(row=0, column=1, sticky="w")
		for row, (extension, folder) in enumerate(sorted(config.rules.items()), start=1):
			extension_var = tk.StringVar(value=extension)
			folder_var = tk.StringVar(value=folder)
			self.rule_rows.append((extension_var, folder_var))
			ttk.Entry(self.rules_frame, textvariable=extension_var, width=18).grid(
				row=row, column=0, padx=(0, 8), pady=3, sticky="ew"
			)
			ttk.Entry(self.rules_frame, textvariable=folder_var).grid(
				row=row, column=1, padx=(0, 8), pady=3, sticky="ew"
			)
		self.rules_frame.columnconfigure(1, weight=1)
		ttk.Button(self.rules_frame, text="Guardar reglas", command=self.save_rules).grid(
			row=len(self.rule_rows) + 1, column=1, sticky="e", pady=(12, 0)
		)

	def _build_history_tab(self) -> None:
		self.history_tree = self._build_tree(
			self.history_frame,
			("archivo", "origen", "destino", "fecha"),
		)
		ttk.Button(self.history_frame, text="Actualizar", command=self.refresh_views).pack(
			anchor="e", pady=(8, 0)
		)

	def _build_errors_tab(self) -> None:
		self.errors_tree = self._build_tree(
			self.errors_frame,
			("archivo", "tipo", "mensaje", "fecha"),
		)
		ttk.Button(self.errors_frame, text="Actualizar", command=self.refresh_views).pack(
			anchor="e", pady=(8, 0)
		)

	@staticmethod
	def _build_tree(parent: ttk.Frame, columns: tuple[str, ...]) -> ttk.Treeview:
		tree = ttk.Treeview(parent, columns=columns, show="headings")
		for column in columns:
			tree.heading(column, text=column.capitalize())
			tree.column(column, width=180, anchor="w")
		tree.pack(fill="both", expand=True)
		return tree

	def choose_folder(self) -> None:
		selected = filedialog.askdirectory(initialdir=self.folder_var.get())
		if selected:
			self.folder_var.set(selected)

	def save_rules(self) -> None:
		new_rules: dict[str, str] = {}
		for extension_var, folder_var in self.rule_rows:
			extension = extension_var.get().strip().lower()
			folder = folder_var.get().strip()
			if not extension.startswith(".") or not folder:
				messagebox.showerror("Regla inválida", "Cada extensión debe comenzar con punto y tener una carpeta.")
				return
			new_rules[extension] = folder
		config.guardar_reglas(new_rules)
		config.rules = new_rules
		self.status_var.set("Reglas guardadas")

	def organize(self) -> None:
		folder = Path(self.folder_var.get())
		if not folder.is_dir():
			messagebox.showerror("Carpeta inválida", "Selecciona una carpeta existente.")
			return
		moved, errors = organize_downloads(folder, DEFAULT_DB_PATH)
		self.status_var.set(f"Movidos: {len(moved)} | Errores: {len(errors)}")
		self.refresh_views()
		if errors:
			messagebox.showwarning("Organización completada", f"Se movieron {len(moved)} archivos y hubo {len(errors)} errores.")

	def refresh_views(self) -> None:
		self._fill_tree(self.history_tree, get_history())
		self._fill_tree(self.errors_tree, get_errors())

	@staticmethod
	def _fill_tree(tree: ttk.Treeview, rows: list[tuple]) -> None:
		tree.delete(*tree.get_children())
		for row in rows:
			tree.insert("", "end", values=row)


def run_cli() -> None:
	create_tables()
	moved_files, errors = organize_downloads()
	for source, destination in moved_files:
		print("Archivo movido:", source.name, "a", destination.parent.name)
	if errors:
		print("\nErrores registrados:")
		for origin, type_, msg in errors:
			print(f"{origin.name} : {type_} - {msg}")


def main() -> None:
	parser = argparse.ArgumentParser(description="Organiza archivos por extensión.")
	parser.add_argument("--cli", action="store_true", help="Usa la interfaz de terminal.")
	args = parser.parse_args()
	if args.cli:
		run_cli()
		return
	if tk is None:
		raise SystemExit(
			"La interfaz requiere tkinter. En Debian/Linux Mint instala el paquete python3-tk."
		)
	create_tables()
	root = tk.Tk()
	app = ClipperApp(root)
	app.refresh_views()
	root.mainloop()


if __name__ == "__main__":
	main()