# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['frontend/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('setting/default.json', 'setting'), ('backend/tools/markdown_parser/style.css', 'setting')],
    hiddenimports=["pynput", "openai", "markdown", "pygments", "peewee", "pyside6-fluent-widget", "tiktoken", "tiktoken_ext", "tiktoken_ext.openai_public"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['frontend\\add_libs.py'],
    excludes=['pyinstaller'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ProPal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)


def clean_up_dist():
    """move files from dist/main to dist/main/libs to make the directory look cleaner"""
    from pathlib import Path
    Path('dist/main/libs').mkdir(parents=True, exist_ok=True)
    for file in Path('dist/main').iterdir():
        if file.is_dir():
            continue
        if file.name in ['ProPal.exe', 'base_library.zip', 'python3.dll', 'python310.dll']:
            continue
        file.rename(Path('dist/main/libs') / file.name)

clean_up_dist()