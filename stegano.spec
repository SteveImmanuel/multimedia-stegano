# -*- mode: python ; coding: utf-8 -*-
import os
import platform

BASE_PATH = os.path.abspath(os.curdir)
os_name = platform.system().lower()
exe_name = f'stegano_{os_name}'
block_cipher = None

a = Analysis(['main.py'],
             pathex=[BASE_PATH],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=exe_name,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )