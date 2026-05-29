from pathlib import Path
import shutil

# Organizador de archivos en la carpeta de Descargas
downloads = Path.home() / "Downloads"

# Reglas de organización: extensión de archivo -> carpeta destino
rules = {
    ".pdf": "Documentos",
    ".png": "Imagenes",
    ".jpg": "Imagenes",
    ".mp4": "Videos"
}

# Crear carpetas según las reglas
for file in downloads.iterdir():

    # Verificar si es un archivo (no una carpeta)
    if file.is_file():
        ext = file.suffix.lower()

        # Determinar la carpeta destino según la extensión del archivo
        if ext in rules:
            folder = downloads / rules[ext]
        else:
            folder = downloads / "Otros"

        # Crear la carpeta si no existe y mover el archivo
        folder.mkdir(exist_ok=True)
        shutil.move(str(file), str(folder / file.name))
        
        # Imprimir el resultado de la organización
        print(file.name, "->", folder)