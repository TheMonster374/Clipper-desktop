from pathlib import Path
import shutil
import logging
from typing import Tuple, List

import config
from database import DEFAULT_DB_PATH, add_error, add_history
from paths import downloads_dir, log_path

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
        return [], [(downloads, type(error).__name__, str(error))]

    for file in entries:
        if not file.is_file() or file.resolve() == Path(db_path).resolve():
            continue
        extension = file.suffix.lower()
        folder = downloads / config.rules.get(extension, "Otros")
        destination = folder / file.name
        if destination.exists():
            errors.append((file, "DestinationExists", f"Destino ya existe: {destination}"))
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
        msg = f"No se puede listar la carpeta {downloads}: {e}"
        logger.error(msg)
        errors.append((downloads, type(e).__name__, str(e)))
        add_error(str(downloads), type(e).__name__, str(e), db_path)
        return moved_files, errors

    for file in entries:
        try:
            if not file.is_file():
                continue

            if file.resolve() == Path(db_path).resolve():
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
                msg = f"No se pudo crear la carpeta destino {folder}: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, str(e)))
                add_error(str(file), type(e).__name__, str(e), db_path)
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
                msg = f"Sin permisos o archivo en uso: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, "PermissionError", str(e)))
                add_error(str(file), "PermissionError", str(e), db_path)
                continue
            except (OSError, shutil.Error) as e:
                msg = f"Error al mover: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, str(e)))
                add_error(str(file), type(e).__name__, str(e), db_path)
                continue

        except Exception as e:
            # Capturamos errores inesperados por archivo y continuamos
            logger.exception("Error inesperado procesando %s: %s", file, e)
            errors.append((file, type(e).__name__, str(e)))
            add_error(str(file), type(e).__name__, str(e), db_path)

    return moved_files, errors


if __name__ == "__main__":
    organize_downloads()
