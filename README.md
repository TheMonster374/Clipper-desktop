# 📎 Clipper

Clipper es una pequeña aplicación en Python para organizar archivos de la carpeta Descargas usando reglas por extensión. Detecta la ubicación configurada en Windows, Linux y macOS.

## Cómo funciona

El flujo actual está dividido en tres módulos:

- [main.py](main.py): punto de entrada. Llama al organizador y muestra qué archivos se movieron.
- [organizer.py](organizer.py): contiene la lógica principal para recorrer Downloads, decidir el destino y mover cada archivo.
- [rules.json](rules.json): define las extensiones y carpetas destino.

## Reglas predeterminadas

| Extensión | Carpeta      |
| --------- | ------------ |
| `.pdf`    | `Documentos` |
| `.png`, `.jpg`,`.jpeg`    | `Imagenes`   |
| `.mp4`    | `Videos`     |

`NUEVO:` Ya es posible agregar/quitar reglas personalizadas
Los archivos que no coinciden con ninguna regla se mueven a `Otros`.

## Estructura del proyecto

- `main.py`: ejecuta la app.
- `organizer.py`: contiene `organize_downloads()`.
- `rules.json`: almacena las reglas de organización.

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
6. Imprime en consola el nombre del archivo y la carpeta destino.

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

### V0.1

- Lectura de archivos en Descargas
- Detección de extensiones
- Creación automática de carpetas
- Organización básica por tipo de archivo
- Detección de la carpeta Descargas en Windows, Linux y macOS
- Registro persistente en la carpeta de datos del usuario

## Tecnologías

- Python
- pathlib
- shutil

## Roadmap

### V1

- Organización por categorías

### V2

- Integración con carpetas del sistema

### V3

- Historial de movimientos

### V4

- Búsqueda rápida

### V5

- Clasificación inteligente mediante IA

### V6

- Asistente flotante estilo clip

## Autor

Proyecto personal desarrollado como práctica de programación y automatización.
