# 📎 Clipper

Clipper es una aplicación de escritorio en Python para organizar archivos de la carpeta Descargas usando reglas por extensión. Detecta la ubicación configurada en Windows, Linux y macOS.

## Cómo funciona

El flujo actual está dividido en varios módulos:

- [main.py](main.py): interfaz gráfica y modo de terminal.
- [organizer.py](organizer.py): vista previa y lógica para decidir destinos y mover archivos.
- [config.py](config.py): carga, guarda y define las reglas predeterminadas.
- [rules.json](rules.json): reglas configurables por extensión.
- [database.py](database.py): historial de movimientos y registro de errores en SQLite.
- [paths.py](paths.py): rutas multiplataforma para Descargas, datos y logs.
- [tests/test_organizer.py](tests/test_organizer.py): pruebas automatizadas.

## Reglas predeterminadas

| Extensiones             | Carpeta      |
| ----------------------- | ------------ |
| `.pdf`                  | `Documentos` |
| `.jpg`, `.jpeg`, `.png` | `Imagenes`   |
| `.mp4`                  | `Videos`     |

También es posible agregar, quitar y editar reglas personalizadas desde la interfaz.
Los archivos que no coinciden con ninguna regla se mueven a `Otros`.

## Estructura del proyecto

- `main.py`: ejecuta la interfaz o el modo CLI.
- `organizer.py`: contiene `preview_downloads()` y `organize_downloads()`.
- `config.py` y `rules.json`: almacenan y gestionan las reglas.
- `database.py`: gestiona la base de datos SQLite.
- `paths.py`: resuelve las rutas según el sistema operativo.
- `tests/`: contiene las pruebas automatizadas.

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python3 main.py
```

Antes de ejecutar, instala la dependencia multiplataforma:

```bash
python3 -m pip install -r requirements.txt
```

En Linux Mint, instala también el soporte de interfaz gráfica si no está disponible:

```bash
sudo apt install python3-tk
```

La aplicación abre una interfaz de escritorio. Para usar la versión de terminal:

```bash
python3 main.py --cli
```

## Qué hace el programa

1. Busca la carpeta Descargas configurada por el sistema operativo.
2. Recorre sus archivos.
3. Detecta la extensión de cada archivo.
4. Crea la carpeta destino si no existe.
5. Mueve el archivo a la carpeta correspondiente.
6. Muestra una vista previa y pide confirmación antes de mover archivos desde la interfaz.
7. Registra los movimientos y errores en SQLite.

## Interfaz de escritorio

La interfaz permite:

- Consultar y cambiar la carpeta que se va a organizar.
- Editar y guardar las reglas por extensión.
- Agrupar varias extensiones en una regla, por ejemplo `.jpg, .jpeg, .png`.
- Añadir o quitar reglas y restaurar las reglas predeterminadas.
- Revisar los movimientos en una vista previa antes de confirmarlos.
- Ejecutar la organización sin sobrescribir archivos existentes.
- Consultar el historial de movimientos y los errores registrados.

## Estado actual

### V0.9

- Organización por extensión con carpeta `Otros` para archivos sin regla.
- Detección multiplataforma de la carpeta Descargas.
- Interfaz gráfica y modo de terminal.
- Reglas editables, agrupación de extensiones y restauración de valores predeterminados.
- Vista previa y confirmación antes de mover archivos.
- Historial y errores persistentes en SQLite.
- Pruebas automatizadas para la lógica principal.

## Tecnologías

- Python
- Tkinter
- pathlib
- shutil
- SQLite
- platformdirs

## Pruebas

Desde la carpeta del proyecto:

```bash
python3 -W error -m unittest discover -s tests -v
```

## Próximos pasos

- Mejorar el diseño visual de la interfaz.
- Añadir búsqueda y filtros al historial.
- Permitir exportar el historial.
- Añadir configuración de ejecución automática o programación.
- Preparar paquetes instalables para Windows, Linux y macOS.

## Autor

Proyecto personal desarrollado como práctica de programación y automatización.
