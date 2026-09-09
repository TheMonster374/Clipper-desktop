from pathlib import Path
import shutil
import logging
import os
import sys
from typing import Tuple, List

from . import config
from .database import DEFAULT_DB_PATH, add_error, add_history
from .paths import downloads_dir, log_path

# Logger para registrar errores persistentes
logger = logging.getLogger("clipper.organizer")
if not logger.handlers:
    log_file = log_path()
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def friendly_error(error: Exception, action: str) -> str:
    """Convierte errores comunes del sistema en mensajes comprensibles."""
    if isinstance(error, PermissionError):
        return f"{action}: no hay permisos suficientes o el archivo está en uso."
    if isinstance(error, FileNotFoundError):
        return f"{action}: no se encontró el archivo o la carpeta."
    if isinstance(error, IsADirectoryError):
        return f"{action}: la ruta apunta a una carpeta y no a un archivo."
    if isinstance(error, OSError):
        return f"{action}: el sistema no pudo completar la operación."
    return f"{action}: ocurrió un error inesperado."


def is_lock_file(file: Path) -> bool:
    """Identifica archivos temporales de bloqueo creados por editores."""
    return file.name.startswith(".~lock.") and file.name.endswith("#")


def open_files(proc_root: Path = Path("/proc")) -> set[Path]:
    """Devuelve los archivos abiertos detectables por Linux."""
    opened: set[Path] = set()
    if sys.platform != "linux":
        return opened

    try:
        for process_dir in proc_root.iterdir():
            if not process_dir.name.isdigit():
                continue
            descriptors = process_dir / "fd"
            try:
                for descriptor in descriptors.iterdir():
                    try:
                        opened.add(Path(os.readlink(descriptor)).resolve())
                    except (FileNotFoundError, PermissionError, OSError):
                        continue
            except (FileNotFoundError, PermissionError, OSError):
                continue
    except (FileNotFoundError, PermissionError, OSError):
        return opened
    return opened


def is_open_file(file: Path, proc_root: Path = Path("/proc")) -> bool:
    """Comprueba en Linux si algún proceso mantiene abierto el archivo."""
    return file.resolve() in open_files(proc_root)


def preview_downloads(
    downloads: Path,
    db_path: str = DEFAULT_DB_PATH,
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, str, str]]]:
    """Calcula movimientos posibles sin modificar archivos ni la base de datos."""
    planned: list[tuple[Path, Path]] = []
    errors: list[tuple[Path, str, str]] = []
    try:
        entries = list(downloads.iterdir())
    except OSError as error:
        return [], [(downloads, type(error).__name__, friendly_error(error, "No se pudo leer la carpeta"))]

    opened_files = open_files()
    for file in entries:
        if not file.is_file() or is_lock_file(file) or file.resolve() == Path(db_path).resolve():
            continue
        extension = file.suffix.lower()
        folder = downloads / config.rules.get(extension, "Otros")
        destination = folder / file.name
        if file.resolve() in opened_files:
            errors.append((file, "FileInUse", "El archivo está abierto por otro programa."))
        elif destination.exists():
            errors.append((file, "DestinationExists", f"El destino ya existe: {destination}"))
        else:
            planned.append((file, destination))
    return planned, errors


def organize_downloads(
    downloads: Path | None = None,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[List[tuple[Path, Path]], List[tuple[Path, str, str]]]:
    """Organiza los archivos de la carpeta Descargas según las reglas definidas.

    Args:
        downloads: Carpeta a organizar. Si no se indica, usa la carpeta Descargas
            configurada por el sistema operativo.

    Returns:
        Tupla con 1) lista de tuplas (archivo original, nueva ubicación) y
        2) lista de errores como tuplas (archivo, tipo_error, mensaje).
    """
    downloads = downloads or downloads_dir()
    moved_files: List[tuple[Path, Path]] = []
    errors: List[tuple[Path, str, str]] = []

    try:
        entries = list(downloads.iterdir())
    except Exception as e:
        msg = friendly_error(e, f"No se puede listar la carpeta {downloads}")
        logger.error(msg)
        errors.append((downloads, type(e).__name__, msg))
        add_error(str(downloads), type(e).__name__, msg, db_path)
        return moved_files, errors

    opened_files = open_files()
    for file in entries:
        try:
            if not file.is_file() or is_lock_file(file):
                continue

            if file.resolve() == Path(db_path).resolve():
                continue

            if file.resolve() in opened_files:
                msg = "El archivo está abierto por otro programa."
                errors.append((file, "FileInUse", msg))
                add_error(str(file), "FileInUse", msg, db_path)
                continue

            ext = file.suffix.lower()

            if ext in config.rules:
                folder = downloads / config.rules[ext]
            else:
                folder = downloads / "Otros"

            # Aseguramos la carpeta destino justo antes del movimiento
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                msg = friendly_error(e, f"No se pudo crear la carpeta destino {folder}")
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, msg))
                add_error(str(file), type(e).__name__, msg, db_path)
                continue

            destination = folder / file.name

            # Si el destino ya existe: registrar y saltar (no sobrescribir)
            if destination.exists():
                msg = f"Destino ya existe: {destination}"
                logger.info("%s - %s", file, msg)
                errors.append((file, "DestinationExists", msg))
                add_error(str(file), "DestinationExists", msg, db_path)
                continue

            try:
                shutil.move(str(file), str(destination))
                moved_files.append((file, destination))
                add_history(str(file), str(file.parent), str(destination.parent), db_path)
            except PermissionError as e:
                msg = friendly_error(e, "No se pudo mover el archivo")
                logger.warning("%s - %s", file, msg)
                errors.append((file, "PermissionError", msg))
                add_error(str(file), "PermissionError", msg, db_path)
                continue
            except (OSError, shutil.Error) as e:
                msg = friendly_error(e, "No se pudo mover el archivo")
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, msg))
                add_error(str(file), type(e).__name__, msg, db_path)
                continue

        except Exception as e:
            # Capturamos errores inesperados por archivo y continuamos
            logger.exception("Error inesperado procesando %s: %s", file, e)
            msg = friendly_error(e, "No se pudo procesar el archivo")
            errors.append((file, type(e).__name__, msg))
            add_error(str(file), type(e).__name__, msg, db_path)

    return moved_files, errors


if __name__ == "__main__":
    organize_downloads()
