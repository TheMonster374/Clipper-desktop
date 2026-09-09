import json
from pathlib import Path

from paths import RULES_PATH


def cargar_reglas(path: Path = RULES_PATH) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


rules = cargar_reglas()