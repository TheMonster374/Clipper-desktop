import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from clipper import config
from clipper import organizer
from clipper.database import add_error, add_history, get_errors, get_history
from clipper.main import ClipperApp


class OrganizerTests(unittest.TestCase):
    def test_organizes_known_and_unknown_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloads = Path(temp_dir) / "Descargas"
            downloads.mkdir()
            database = Path(temp_dir) / "clipper.db"
            pdf = downloads / "manual.pdf"
            archive = downloads / "archivo.xyz"
            pdf.write_text("pdf", encoding="utf-8")
            archive.write_text("archivo", encoding="utf-8")

            moved, errors = organizer.organize_downloads(downloads, str(database))

            self.assertEqual(errors, [])
            self.assertEqual(len(moved), 2)
            self.assertTrue((downloads / "Documentos" / "manual.pdf").exists())
            self.assertTrue((downloads / "Otros" / "archivo.xyz").exists())

    def test_does_not_overwrite_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloads = Path(temp_dir) / "Descargas"
            documents = downloads / "Documentos"
            documents.mkdir(parents=True)
            database = Path(temp_dir) / "clipper.db"
            source = downloads / "manual.pdf"
            destination = documents / source.name
            source.write_text("nuevo", encoding="utf-8")
            destination.write_text("original", encoding="utf-8")

            moved, errors = organizer.organize_downloads(downloads, str(database))

            self.assertEqual(moved, [])
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0][1], "DestinationExists")
            self.assertEqual(destination.read_text(encoding="utf-8"), "original")

    def test_reads_history_and_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database = str(Path(temp_dir) / "clipper.db")
            add_history("a.pdf", "Descargas", "Documentos", database)
            add_error("b.zip", "DestinationExists", "El destino ya existe", database)

            self.assertEqual(get_history(database)[0][0], "a.pdf")
            self.assertEqual(get_errors(database)[0][1], "DestinationExists")

    def test_saves_rules_to_a_custom_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_path = Path(temp_dir) / "rules.json"
            new_rules = {".txt": "Texto"}

            config.guardar_reglas(new_rules, rules_path)

            self.assertEqual(config.cargar_reglas(rules_path), new_rules)

    def test_preview_ignores_database_inside_downloads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloads = Path(temp_dir) / "Descargas"
            downloads.mkdir()
            database = downloads / "clipper.db"
            database.write_text("database", encoding="utf-8")
            document = downloads / "manual.pdf"
            document.write_text("pdf", encoding="utf-8")

            planned, errors = organizer.preview_downloads(downloads, str(database))

            self.assertEqual([source for source, _ in planned], [document])
            self.assertEqual(errors, [])

    def test_filters_history_rows_case_insensitively(self) -> None:
        rows = [
            ("/tmp/Imagenes/foto.png", "/tmp/Descargas", "/tmp/Imagenes", "fecha"),
            ("/tmp/Documentos/manual.pdf", "/tmp/Descargas", "/tmp/Documentos", "fecha"),
        ]

        filtered = ClipperApp.filter_rows(rows, "FOTO")

        self.assertEqual(filtered, [rows[0]])

    def test_file_filter_does_not_search_paths(self) -> None:
        rows = [("/tmp/Imagenes/foto.png", "/tmp/Descargas", "/tmp/Imagenes", "fecha")]

        filtered = ClipperApp.filter_rows(rows, "imagenes")

        self.assertEqual(filtered, [])

    def test_formats_iso_date_for_the_interface(self) -> None:
        formatted = ClipperApp.format_date("2026-09-09T17:05:00+00:00")

        self.assertRegex(formatted, r"09/09/2026 \(\d{2}:05 (AM|PM)\)")

    def test_translates_permission_errors(self) -> None:
        message = organizer.friendly_error(
            PermissionError(13, "Permission denied"),
            "No se pudo mover el archivo",
        )

        self.assertIn("no hay permisos", message)
        self.assertNotIn("Permission denied", message)

    def test_preview_uses_spanish_destination_conflict_message(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloads = Path(temp_dir) / "Descargas"
            documents = downloads / "Documentos"
            documents.mkdir(parents=True)
            source = downloads / "manual.pdf"
            destination = documents / source.name
            source.write_text("nuevo", encoding="utf-8")
            destination.write_text("original", encoding="utf-8")

            _, errors = organizer.preview_downloads(downloads, str(Path(temp_dir) / "clipper.db"))

            self.assertEqual(errors[0][2], f"El destino ya existe: {destination}")

    def test_ignores_editor_lock_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            downloads = Path(temp_dir) / "Descargas"
            downloads.mkdir()
            lock_file = downloads / ".~lock.documento.pdf#"
            lock_file.write_text("lock", encoding="utf-8")

            planned, errors = organizer.preview_downloads(downloads, str(Path(temp_dir) / "clipper.db"))

            self.assertEqual(planned, [])
            self.assertEqual(errors, [])

    def test_detects_a_file_opened_by_this_process_on_linux(self) -> None:
        with tempfile.NamedTemporaryFile() as opened_file:
            if organizer.sys.platform == "linux":
                self.assertTrue(organizer.is_open_file(Path(opened_file.name)))


if __name__ == "__main__":
    unittest.main()