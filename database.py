import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = str(BASE_DIR / 'clipper.db')

def create_tables(db_path: str = DEFAULT_DB_PATH) -> None:
    """Crea las tablas 'history' y 'errors' si no existen."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archivo TEXT NOT NULL,
        carpeta_origen TEXT,
        carpeta_destino TEXT,
        fecha TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        archivo TEXT,
        tipo_error TEXT,
        mensaje TEXT,
        fecha TEXT NOT NULL
    )
    ''')

    c.execute("PRAGMA table_info(history)")
    columns = {row[1] for row in c.fetchall()}
    if "carpeta_destino" not in columns:
        c.execute("ALTER TABLE history ADD COLUMN carpeta_destino TEXT")

    conn.commit()
    conn.close()

def now_iso() -> str:
    """Fecha y hora en formato ISO (UTC)."""
    return datetime.utcnow().isoformat()

def add_history(archivo: str, carpeta_origen: str, carpeta_destino: str, db_path: str = DEFAULT_DB_PATH, fecha: str | None = None) -> None:
    fecha = fecha or now_iso()
    create_tables(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO history (archivo, carpeta_origen, carpeta_destino, fecha) VALUES (?, ?, ?, ?)',
              (archivo, carpeta_origen, carpeta_destino, fecha))
    conn.commit()
    conn.close()

def add_error(archivo: str | None, tipo_error: str, mensaje: str, db_path: str = DEFAULT_DB_PATH, fecha: str | None = None) -> None:
    fecha = fecha or now_iso()
    create_tables(db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO errors (archivo, tipo_error, mensaje, fecha) VALUES (?, ?, ?, ?)',
              (archivo, tipo_error, mensaje, fecha))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
    print("Tablas 'history' y 'errors' creadas en clipper.db")
