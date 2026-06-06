from pathlib import Path
import shutil
import logging
from typing import Tuple, List

from rules import rules

# Logger para registrar errores persistentes
logger = logging.getLogger("clipper.organizer")
if not logger.handlers:
    handler = logging.FileHandler("clipper_errors.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def organize_downloads(
    downloads: Path | None = None,
) -> Tuple[List[tuple[Path, Path]], List[tuple[Path, str, str]]]:
    """Organiza los archivos de la carpeta Descargas según las reglas definidas.

    Args:
        downloads: Carpeta a organizar. Si no se indica, usa la carpeta Downloads
            del usuario actual.

    Returns:
        Tupla con 1) lista de tuplas (archivo original, nueva ubicación) y
        2) lista de errores como tuplas (archivo, tipo_error, mensaje).
    """
    downloads = downloads or Path.home() / "Downloads"
    moved_files: List[tuple[Path, Path]] = []
    errors: List[tuple[Path, str, str]] = []

    try:
        entries = list(downloads.iterdir())
    except Exception as e:
        msg = f"No se puede listar la carpeta {downloads}: {e}"
        logger.error(msg)
        errors.append((downloads, type(e).__name__, str(e)))
        return moved_files, errors

    for file in entries:
        try:
            if not file.is_file():
                continue

            ext = file.suffix.lower()

            if ext in rules:
                folder = downloads / rules[ext]
            else:
                folder = downloads / "Otros"

            # Aseguramos la carpeta destino justo antes del movimiento
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                msg = f"No se pudo crear la carpeta destino {folder}: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, str(e)))
                continue

            destination = folder / file.name

            # Si el destino ya existe: registrar y saltar (no sobrescribir)
            if destination.exists():
                msg = f"Destino ya existe: {destination}"
                logger.info("%s - %s", file, msg)
                errors.append((file, "DestinationExists", msg))
                continue

            try:
                shutil.move(str(file), str(destination))
                moved_files.append((file, destination))
            except PermissionError as e:
                msg = f"Sin permisos o archivo en uso: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, "PermissionError", str(e)))
                continue
            except (OSError, shutil.Error) as e:
                msg = f"Error al mover: {e}"
                logger.warning("%s - %s", file, msg)
                errors.append((file, type(e).__name__, str(e)))
                continue

        except Exception as e:
            # Capturamos errores inesperados por archivo y continuamos
            logger.exception("Error inesperado procesando %s: %s", file, e)
            errors.append((file, type(e).__name__, str(e)))

    return moved_files, errors


if __name__ == "__main__":
    organize_downloads()
