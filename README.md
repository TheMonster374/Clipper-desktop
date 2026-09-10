<h1 align="center"> 📎 Clipper </h1>

Clipper es una aplicación de escritorio en Python para organizar archivos de la carpeta Descargas usando reglas por extensión.

> **Estado del proyecto:** esta es una **versión beta inicial**. La aplicación ya es funcional, pero todavía puede contener errores, ajustes pendientes y cambios en el comportamiento.

<h2 align="center"> 👁️​ Vista previa </h2>

<p align="center">
<img src="https://www.image2url.com/r2/default/images/1789061775463-3ef6fb85-15c8-4537-8681-46d43bda6f5a.png" alt="Clipper_Vista_Previa" width="500"/>

<p align="center">
<img src="https://www.image2url.com/r2/default/images/1789061779843-4a281f1a-d2c0-4fff-9788-a0c97fdc3c71.png" alt="Clipper_Vista_Previa" width="500"/>

<h3 align="center"> 📃 Historial </h3>
<p align="center">
<img src="https://www.image2url.com/r2/default/images/1789061770660-f4b26c29-2bd3-4f87-908e-6ccf5623b661.png" alt="Clipper_Vista_Previa_Historial" width="500"/>

<h3 align="center"> ❌ Historial Errores </h3>
<p align="center">
<img src="https://www.image2url.com/r2/default/images/1789061779843-4a281f1a-d2c0-4fff-9788-a0c97fdc3c71.png" alt="Clipper_Vista_Previa_Errores" width="500"/>

## `❓Qué hace`

Clipper organiza automáticamente los archivos de la carpeta Descargas según su extensión y los mueve a carpetas como:

- `Documentos`
- `Imagenes`
- `Videos`
- `Otros` para archivos que no coinciden con ninguna regla

## `✨ Características principales`

- Interfaz gráfica y modo de terminal.
- Reglas editables por extensión.
- Agrupación de varias extensiones en una sola regla.
- Vista previa antes de confirmar movimientos.
- Historial de movimientos y registro de errores en SQLite.
- Búsqueda en el historial y filtros de errores.
- Detección de archivos abiertos como protección adicional.
- Mensajes de error traducidos al español.
- Pruebas automatizadas para la lógica principal.

## `⚙️ Instalación`

La forma recomendada de usar Clipper es descargar una release.

1. En GitHub, entra en **[Releases](https://github.com/TheMonster374/Clipper-desktop/releases/tag/v1.0.1)**.
2. Descarga el paquete correspondiente a tu sistema operativo.
3. Descomprime el archivo.
4. Abre el ejecutable dentro de la carpeta `Clipper`.

### `✅ Descargas disponibles`

- **Linux Mint:** `Clipper-Linux-x86_64.zip`
- **Windows:** `Clipper-Windows-x86_64.zip`

> Si tu sistema muestra advertencias al abrir el archivo, revisa los permisos del ejecutable o las opciones de seguridad del sistema operativo.

## `📕 Uso`

Clipper detecta la carpeta Descargas del sistema, revisa sus archivos, aplica las reglas configuradas y mueve cada archivo a su carpeta destino.

Desde la interfaz puedes:

- consultar o cambiar la carpeta a organizar,
- editar y guardar reglas por extensión,
- agregar, quitar o restaurar reglas,
- revisar una vista previa antes de confirmar,
- ver el historial de movimientos,
- consultar errores guardados.

## `🔗 Compatibilidad`

Los sistemas objetivo de esta versión son:

- **Linux Mint**
- **Windows 10 y 11**

macOS y otras distribuciones de Linux no forman parte de las pruebas oficiales actuales.

## `🖥️ Tecnologías`

- Python
- Tkinter
- pathlib
- shutil
- SQLite
- platformdirs

## `📑 Pruebas`

Si quieres ejecutar las pruebas desde el código fuente:

```bash
python3 -W error -m unittest discover -s tests -v
```
## `↗️ Próximos pasos`

- Mejorar el diseño visual de la interfaz.
- Permitir exportar el historial.
- Añadir configuración de ejecución automática o programación.
- Crear una interfaz de instalación con accesos directos.

`👤 Autor`
<a href="https://github.com/TheMonster374"><img src="https://github.com/TheMonster374.png" width="250" height="250" alt="Monster"/></a>

`Clipper-desktop by MONSTER`
