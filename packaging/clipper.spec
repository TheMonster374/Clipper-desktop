from pathlib import Path


project_dir = Path(SPECPATH).parent
source_dir = project_dir / "src"


a = Analysis(
    [str(source_dir / "clipper_launcher.py")],
    pathex=[str(source_dir)],
    binaries=[],
    datas=[(str(project_dir / "resources" / "rules.json"), ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Clipper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    exclude_binaries=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="Clipper",
)