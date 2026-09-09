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
from organizer import friendly_error, organize_downloads, preview_downloads
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
		grouped_rules: dict[str, list[str]] = {}
		for extension, folder in sorted(config.rules.items()):
			grouped_rules.setdefault(folder, []).append(extension)
		for extensions, folder in sorted(
			([extensions, folder] for folder, extensions in grouped_rules.items()),
			key=lambda item: item[1],
		):
			self._add_rule_row(", ".join(extensions), folder)
		self.rules_frame.columnconfigure(1, weight=1)
		self._refresh_rule_buttons()

	def _add_rule_row(self, extensions: str = "", folder: str = "") -> None:
		extension_var = tk.StringVar(value=extensions)
		folder_var = tk.StringVar(value=folder)
		self.rule_rows.append((extension_var, folder_var))
		self._refresh_rule_rows()

	def _refresh_rule_rows(self) -> None:
		for child in self.rules_frame.grid_slaves():
			if int(child.grid_info().get("row", 0)) > 0:
				child.destroy()
		for row, (extension_var, folder_var) in enumerate(self.rule_rows, start=1):
			ttk.Entry(self.rules_frame, textvariable=extension_var, width=28).grid(
				row=row, column=0, padx=(0, 8), pady=3, sticky="ew"
			)
			ttk.Entry(self.rules_frame, textvariable=folder_var).grid(
				row=row, column=1, padx=(0, 8), pady=3, sticky="ew"
			)
			ttk.Button(self.rules_frame, text="Quitar", command=lambda index=row - 1: self.remove_rule(index)).grid(
				row=row, column=2, pady=3
			)
		self._refresh_rule_buttons()

	def _refresh_rule_buttons(self) -> None:
		for child in self.rules_frame.grid_slaves():
			if int(child.grid_info().get("row", 0)) == len(self.rule_rows) + 1:
				child.destroy()
		button_row = len(self.rule_rows) + 1
		ttk.Button(self.rules_frame, text="Añadir regla", command=lambda: self._add_rule_row()).grid(
			row=button_row, column=0, sticky="w", pady=(12, 0)
		)
		ttk.Button(self.rules_frame, text="Restaurar predeterminadas", command=self.restore_default_rules).grid(
			row=button_row, column=1, sticky="e", pady=(12, 0)
		)
		ttk.Button(self.rules_frame, text="Guardar reglas", command=self.save_rules).grid(
			row=button_row, column=2, sticky="e", pady=(12, 0)
		)

	def remove_rule(self, index: int) -> None:
		if len(self.rule_rows) == 1:
			messagebox.showwarning("Reglas", "Debe quedar al menos una regla.")
			return
		self.rule_rows.pop(index)
		self._refresh_rule_rows()

	def restore_default_rules(self) -> None:
		if not messagebox.askyesno("Restaurar reglas", "¿Reemplazar las reglas actuales por las predeterminadas?"):
			return
		self.rule_rows.clear()
		grouped_rules: dict[str, list[str]] = {}
		for extension, folder in config.DEFAULT_RULES.items():
			grouped_rules.setdefault(folder, []).append(extension)
		for folder, extensions in grouped_rules.items():
			self.rule_rows.append((tk.StringVar(value=", ".join(extensions)), tk.StringVar(value=folder)))
		self._refresh_rule_rows()
		self.save_rules()

	def _build_history_tab(self) -> None:
		filter_bar = ttk.Frame(self.history_frame)
		filter_bar.pack(fill="x", pady=(0, 8))
		self.history_filter_var = tk.StringVar()
		ttk.Label(filter_bar, text="Nombre de archivo:").pack(side="left")
		ttk.Entry(filter_bar, textvariable=self.history_filter_var).pack(side="left", fill="x", expand=True, padx=8)
		ttk.Button(filter_bar, text="Filtrar", command=self.refresh_views).pack(side="left")
		ttk.Button(filter_bar, text="Limpiar", command=lambda: self.clear_filter(self.history_filter_var)).pack(side="left", padx=(6, 0))
		self.history_tree = self._build_tree(
			self.history_frame,
			("archivo", "origen", "destino", "fecha"),
		)
		ttk.Button(self.history_frame, text="Actualizar", command=self.refresh_views).pack(anchor="e", pady=(8, 0))

	def _build_errors_tab(self) -> None:
		filter_bar = ttk.Frame(self.errors_frame)
		filter_bar.pack(fill="x", pady=(0, 8))
		self.errors_filter_var = tk.StringVar()
		self.error_type_var = tk.StringVar(value="Todos")
		ttk.Label(filter_bar, text="Nombre de archivo:").pack(side="left")
		ttk.Entry(filter_bar, textvariable=self.errors_filter_var).pack(side="left", fill="x", expand=True, padx=8)
		ttk.Label(filter_bar, text="Tipo:").pack(side="left")
		self.error_type_combo = ttk.Combobox(
			filter_bar,
			textvariable=self.error_type_var,
			values=("Todos",),
			state="readonly",
			width=20,
		)
		self.error_type_combo.pack(side="left", padx=8)
		self.error_type_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_views())
		ttk.Button(filter_bar, text="Filtrar", command=self.refresh_views).pack(side="left")
		ttk.Button(filter_bar, text="Limpiar", command=self.clear_error_filters).pack(side="left", padx=(6, 0))
		self.errors_tree = self._build_tree(
			self.errors_frame,
			("archivo", "tipo", "mensaje", "fecha"),
		)
		ttk.Button(self.errors_frame, text="Actualizar", command=self.refresh_views).pack(anchor="e", pady=(8, 0))

	@staticmethod
	def _build_tree(parent: ttk.Frame, columns: tuple[str, ...]) -> ttk.Treeview:
		tree_frame = ttk.Frame(parent)
		tree_frame.pack(fill="both", expand=True)
		tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
		vertical_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
		horizontal_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
		tree.configure(yscrollcommand=vertical_scroll.set, xscrollcommand=horizontal_scroll.set)
		for column in columns:
			tree.heading(column, text=column.capitalize())
			width = {
				"archivo": 180,
				"origen": 280,
				"destino": 280,
				"tipo": 150,
				"mensaje": 360,
				"fecha": 165,
			}.get(column, 180)
			tree.column(column, width=width, minwidth=90, anchor="w", stretch=False)
		tree.grid(row=0, column=0, sticky="nsew")
		vertical_scroll.grid(row=0, column=1, sticky="ns")
		horizontal_scroll.grid(row=1, column=0, sticky="ew")
		tree_frame.rowconfigure(0, weight=1)
		tree_frame.columnconfigure(0, weight=1)
		return tree

	def choose_folder(self) -> None:
		selected = filedialog.askdirectory(initialdir=self.folder_var.get())
		if selected:
			self.folder_var.set(selected)

	def save_rules(self) -> None:
		new_rules: dict[str, str] = {}
		seen_extensions: set[str] = set()
		for extension_var, folder_var in self.rule_rows:
			folder = folder_var.get().strip()
			extensions = [item.strip().lower() for item in extension_var.get().split(",") if item.strip()]
			if (
				not extensions
				or any(not extension.startswith(".") or any(char.isspace() for char in extension) for extension in extensions)
				or not folder
			):
				messagebox.showerror("Regla inválida", "Separa las extensiones con comas: .pdf, .docx")
				return
			if len(extensions) != len(set(extensions)) or seen_extensions.intersection(extensions):
				messagebox.showerror("Regla duplicada", "Una extensión no puede aparecer en más de una regla.")
				return
			seen_extensions.update(extensions)
			for extension in extensions:
				new_rules[extension] = folder
		config.guardar_reglas(new_rules)
		config.rules = new_rules
		self.status_var.set("Reglas guardadas")

	def organize(self) -> None:
		folder = Path(self.folder_var.get())
		if not folder.is_dir():
			messagebox.showerror("Carpeta inválida", "Selecciona una carpeta existente.")
			return
		if not messagebox.askyesno(
			"Archivos abiertos",
			"Cierra todos los archivos abiertos dentro de la carpeta que vas a organizar.\n\n¿Quieres continuar?",
		):
			return
		planned, conflicts = preview_downloads(folder, DEFAULT_DB_PATH)
		if not planned and not conflicts:
			messagebox.showinfo("Organización", "No hay archivos para organizar.")
			return
		if not self.confirm_plan(planned, conflicts):
			return
		moved, errors = organize_downloads(folder, DEFAULT_DB_PATH)
		self.status_var.set(f"Movidos: {len(moved)} | Errores: {len(errors)}")
		self.refresh_views()
		if errors:
			messagebox.showwarning("Organización completada", f"Se movieron {len(moved)} archivos y hubo {len(errors)} errores.")

	def confirm_plan(self, planned: list[tuple[Path, Path]], conflicts: list[tuple[Path, str, str]]) -> bool:
		preview = tk.Toplevel(self.root)
		preview.title("Confirmar organización")
		preview.transient(self.root)
		preview.grab_set()
		result = tk.BooleanVar(value=False)
		ttk.Label(preview, text=f"Se moverán {len(planned)} archivos. Revisa el destino:").pack(anchor="w", padx=12, pady=12)
		text = tk.Text(preview, width=90, height=18, state="normal")
		text.pack(fill="both", expand=True, padx=12)
		for source, destination in planned:
			text.insert("end", f"{source.name}  ->  {destination.parent}\n")
		for source, _, message in conflicts:
			text.insert("end", f"{source.name}  ->  OMITIDO ({message})\n")
		text.configure(state="disabled")
		buttons = ttk.Frame(preview)
		buttons.pack(anchor="e", padx=12, pady=12)
		ttk.Button(buttons, text="Cancelar", command=preview.destroy).pack(side="right", padx=(8, 0))
		ttk.Button(buttons, text="Confirmar", command=lambda: (result.set(True), preview.destroy())).pack(side="right")
		self.root.wait_window(preview)
		return result.get()

	def refresh_views(self) -> None:
		history_rows = get_history()
		error_rows = get_errors()
		history_query = self.history_filter_var.get().strip().lower()
		error_query = self.errors_filter_var.get().strip().lower()
		error_type = self.error_type_var.get()
		self._fill_tree(self.history_tree, self.filter_rows(history_rows, history_query))
		filtered_errors = self.filter_rows(error_rows, error_query)
		if error_type != "Todos":
			filtered_errors = [row for row in filtered_errors if row[1] == error_type]
		self._fill_tree(self.errors_tree, filtered_errors)
		self.error_type_combo.configure(values=("Todos", *sorted({row[1] for row in error_rows})))

	def clear_filter(self, variable: tk.StringVar) -> None:
		variable.set("")
		self.refresh_views()

	def clear_error_filters(self) -> None:
		self.errors_filter_var.set("")
		self.error_type_var.set("Todos")
		self.refresh_views()

	@staticmethod
	def filter_rows(rows: list[tuple], query: str) -> list[tuple]:
		query = query.strip().lower()
		if not query:
			return rows
		return [row for row in rows if query in str(row[0]).lower()]

	@staticmethod
	def _fill_tree(tree: ttk.Treeview, rows: list[tuple]) -> None:
		tree.delete(*tree.get_children())
		for row in rows:
			values = list(row)
			values[0] = Path(values[0]).name if values[0] else ""
			if len(values) == 4 and values[1] in {"PermissionError", "FileNotFoundError", "IsADirectoryError", "OSError"}:
				values[2] = ClipperApp.localized_error(values[1], values[2])
			values[-1] = ClipperApp.format_date(values[-1])
			tree.insert("", "end", values=values)

	@staticmethod
	def localized_error(error_type: str, message: str) -> str:
		if error_type == "PermissionError":
			return friendly_error(PermissionError(), "No se pudo completar la operación")
		if error_type == "FileNotFoundError":
			return friendly_error(FileNotFoundError(), "No se pudo completar la operación")
		if error_type == "IsADirectoryError":
			return friendly_error(IsADirectoryError(), "No se pudo completar la operación")
		if error_type == "OSError" and "Permission denied" in message:
			return friendly_error(PermissionError(), "No se pudo completar la operación")
		return message

	@staticmethod
	def format_date(value: str) -> str:
		from datetime import datetime

		try:
			return datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y (%I:%M %p)")
		except ValueError:
			return value


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