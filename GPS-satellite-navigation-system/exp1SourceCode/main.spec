# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['E:\\Code\\2020-schoolworks\\GPS-satellite-navigation-system\\main.py'],
             pathex=['C:\\Users\\littlefish\\AppData\\Local\\Programs\\Python\\Python37\\libs', 'E:\\Code\\2020-schoolworks\\GPS-satellite-navigation-system'],
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
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='E:\\Code\\2020-schoolworks\\GPS-satellite-navigation-system\\main.ico')
