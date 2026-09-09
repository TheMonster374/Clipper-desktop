# 📎 Clipper

Clipper es una aplicación de escritorio en Python para organizar archivos de la carpeta Descargas usando reglas por extensión. Los sistemas objetivo de esta versión son Linux Mint y Windows.

## Cómo funciona

El flujo actual está dividido en varios módulos:

- [src/clipper/main.py](src/clipper/main.py): interfaz gráfica y modo de terminal.
- [src/clipper/organizer.py](src/clipper/organizer.py): vista previa y lógica para decidir destinos y mover archivos.
- [src/clipper/config.py](src/clipper/config.py): carga, guarda y define las reglas predeterminadas.
- [resources/rules.json](resources/rules.json): reglas configurables por extensión.
- [src/clipper/database.py](src/clipper/database.py): historial de movimientos y registro de errores en SQLite.
- [src/clipper/paths.py](src/clipper/paths.py): rutas multiplataforma para Descargas, datos y logs.
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

- `src/clipper/`: paquete de la aplicación.
- `resources/`: reglas y otros recursos externos.
- `packaging/`: configuración de PyInstaller.
- `scripts/`: scripts de construcción para Linux Mint y Windows.
- `tests/`: contiene las pruebas automatizadas.

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
PYTHONPATH=src python3 -m clipper
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
PYTHONPATH=src python3 -m clipper --cli
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
- Separar las extensiones con comas; `.pdf .docx` no es válido.
- Añadir o quitar reglas y restaurar las reglas predeterminadas.
- Revisar los movimientos en una vista previa antes de confirmarlos.
- Ejecutar la organización sin sobrescribir archivos existentes.
- Consultar el historial de movimientos y los errores registrados.
- Buscar en el historial y filtrar los errores por tipo.
- Mostrar mensajes de error en español para los problemas comunes del sistema.
- Mostrar una advertencia para cerrar archivos abiertos antes de organizar.

## Estado actual

### V1.0

- Organización por extensión con carpeta `Otros` para archivos sin regla.
- Detección multiplataforma de la carpeta Descargas.
- Interfaz gráfica y modo de terminal.
- Reglas editables, agrupación de extensiones y restauración de valores predeterminados.
- Vista previa y confirmación antes de mover archivos.
- Historial y errores persistentes en SQLite.
- Búsqueda en historial y filtros de errores.
- Mensajes de error comunes traducidos al español.
- Advertencia antes de organizar para cerrar archivos abiertos.
- Detección preventiva de archivos abiertos en Linux como protección adicional.
- Pruebas automatizadas para la lógica principal.

Los errores guardados antes de esta versión pueden conservar el mensaje original del sistema. Los errores nuevos se registran con mensajes descriptivos en español.

## Compatibilidad

Los sistemas objetivo de esta versión son Linux Mint y Windows. macOS y otras distribuciones de Linux no forman parte de las pruebas oficiales actuales.

Para ejecutar desde el código fuente en Windows:

```bash
py -m pip install -r requirements.txt
py -m clipper
```

En Linux Mint:

```bash
sudo apt install python3-tk python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src .venv/bin/python -m clipper
```

También puedes usar el Python del sistema si tu distribución permite instalar paquetes con `pip`:

```bash
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m clipper
```

El comportamiento de archivos abiertos depende del sistema operativo. Windows suele impedir mover archivos que otra aplicación está utilizando. Linux puede permitirlo, por lo que Clipper muestra una advertencia y realiza una detección preventiva adicional.

## Crear ejecutables

Los ejecutables deben generarse en el mismo sistema operativo donde se van a utilizar. PyInstaller no crea un ejecutable de Windows desde Linux. Los scripts de construcción crean automáticamente un entorno virtual `.venv-build` y allí instalan PyInstaller y las dependencias.

En Linux Mint:

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

Ejecuta esos comandos desde la carpeta `scripts/` o usa `./scripts/build_linux.sh` desde la raíz. El resultado se copiará fuera del repositorio, en `~/Aplicaciones/Clipper/Linux/Clipper/Clipper`.

Para Windows 10 u 11, abre PowerShell en el proyecto y ejecuta:

```powershell
.\scripts\build_windows.ps1
```

El resultado se copiará fuera del repositorio, en `%USERPROFILE%\Aplicaciones\Clipper\Windows\Clipper\Clipper.exe`. La carpeta `Clipper` completa debe distribuirse, porque contiene el ejecutable y los archivos internos, incluido `rules.json`.

Quien recibe la carpeta generada no necesita instalar Python, Tkinter ni las dependencias: PyInstaller las incluye en el paquete. `rules.json` queda dentro del paquete para que las reglas puedan seguir editándose.

Windows 10 y Windows 11 son objetivos separados de validación. La aplicación no usa APIs específicas de una de esas versiones, pero hay que probar el ejecutable en ambas.

## Instalar desde GitHub

La forma recomendada para usuarios finales es descargar una release, no clonar el repositorio ni instalar Python.

1. En GitHub, entra en **Releases**.
2. Descarga `Clipper-Linux-x86_64.zip` para Linux Mint o `Clipper-Windows-x86_64.zip` para Windows.
3. Descomprime el archivo.
4. Abre el ejecutable dentro de la carpeta `Clipper`.

En Linux Mint, si el explorador no permite abrirlo, activa **Permitir ejecutar el archivo como programa** en sus propiedades. En Windows puede aparecer una advertencia de SmartScreen porque el ejecutable todavía no tiene firma digital.

Las releases se generan automáticamente al crear un tag con formato `vX.Y.Z`, por ejemplo `v1.0.0`. El workflow de GitHub Actions construye un paquete distinto para cada sistema operativo.

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
- Permitir exportar el historial.
- Añadir configuración de ejecución automática o programación.
- Crear una interfaz de instalación con accesos directos.

## Autor

Proyecto personal desarrollado como práctica de programación y automatización.
