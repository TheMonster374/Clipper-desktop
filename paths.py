import os
from pathlib import Path

try:
    from platformdirs import user_data_dir, user_downloads_dir
except ImportError:
    def user_downloads_dir() -> str:
        if os.name == "nt":
            return str(Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads")

        if sys_platform() == "linux":
            config_file = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "user-dirs.dirs"
            if config_file.is_file():
                for line in config_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith("XDG_DOWNLOAD_DIR="):
                        value = line.partition("=")[2].strip().strip('"')
                        return os.path.abspath(os.path.expandvars(value))

        return str(Path.home() / "Downloads")

    def user_data_dir(app_name: str) -> str:
        if os.name == "nt":
            base = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
        elif sys_platform() == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return str(Path(base) / app_name)

    def sys_platform() -> str:
        import sys

        return sys.platform


APP_NAME = "Clipper"
PROJECT_DIR = Path(__file__).resolve().parent
RULES_PATH = PROJECT_DIR / "rules.json"


def downloads_dir() -> Path:
    """Devuelve la carpeta Descargas configurada para el sistema actual."""
    return Path(user_downloads_dir())


def data_dir() -> Path:
    """Devuelve la carpeta de datos de usuario de Clipper."""
    return Path(user_data_dir(APP_NAME))


def database_path() -> Path:
    return data_dir() / "clipper.db"


def log_path() -> Path:
    return data_dir() / "clipper_errors.log"