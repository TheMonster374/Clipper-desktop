import json
from pathlib import Path

from .paths import RULES_PATH


DEFAULT_RULES: dict[str, str] = {
    ".pdf": "Documentos",
    ".jpg": "Imagenes",
    ".jpeg": "Imagenes",
    ".png": "Imagenes",
    ".mp4": "Videos",
}


def cargar_reglas(path: Path = RULES_PATH) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_reglas(new_rules: dict[str, str], path: Path = RULES_PATH) -> None:
    path.write_text(
        json.dumps(new_rules, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )


rules = cargar_reglas()