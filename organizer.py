from pathlib import Path
import shutil

from rules import rules


def organize_downloads(downloads: Path | None = None) -> list[tuple[Path, Path]]:
    """Organiza los archivos de la carpeta Descargas según las reglas definidas.

    Args:
        downloads: Carpeta a organizar. Si no se indica, usa la carpeta Downloads
            del usuario actual.

    Returns:
        Lista de tuplas con el archivo original y su nueva ubicación.
    """
    downloads = downloads or Path.home() / "Downloads"
    moved_files: list[tuple[Path, Path]] = []

    for file in downloads.iterdir():
        if file.is_file():
            ext = file.suffix.lower()

            if ext in rules:
                folder = downloads / rules[ext]
            else:
                folder = downloads / "Otros"

            folder.mkdir(exist_ok=True)
            destination = folder / file.name
            shutil.move(str(file), str(destination))
            moved_files.append((file, destination))

    return moved_files


if __name__ == "__main__":
    organize_downloads()
