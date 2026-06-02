# 📎 Clipper

Clipper es una pequeña aplicación en Python para organizar archivos de la carpeta Downloads usando reglas por extensión.

## Cómo funciona

El flujo actual está dividido en tres módulos:

- [main.py](main.py): punto de entrada. Llama al organizador y muestra qué archivos se movieron.
- [organizer.py](organizer.py): contiene la lógica principal para recorrer Downloads, decidir el destino y mover cada archivo.
- [rules.py](rules.py): define el diccionario de extensiones y carpetas destino.

## Reglas actuales

| Extensión | Carpeta |
| --- | --- |
| `.pdf` | `Documentos` |
| `.png` | `Imagenes` |
| `.jpg` | `Imagenes` |
| `.mp4` | `Videos` |

Los archivos que no coinciden con ninguna regla se mueven a `Otros`.

## Estructura del proyecto

- `main.py`: ejecuta la app.
- `organizer.py`: contiene `organize_downloads()`.
- `rules.py`: almacena `rules`.

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
python main.py
```

## Qué hace el programa

1. Busca la carpeta `Downloads` del usuario actual.
2. Recorre sus archivos.
3. Detecta la extensión de cada archivo.
4. Crea la carpeta destino si no existe.
5. Mueve el archivo a la carpeta correspondiente.
6. Imprime en consola el nombre del archivo y la carpeta destino.

## Estado actual

### V0.1
- Lectura de archivos en Descargas
- Detección de extensiones
- Creación automática de carpetas
- Organización básica por tipo de archivo

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
