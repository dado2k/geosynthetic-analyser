# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
from kivy_deps import sdl2, glew, gstreamer


a = Analysis(['F:\\University\\4th Bachelor\\4E4 Research Project\\GeosyntheticsProgram\\GeosyntheticAnalyser.py'],
             pathex=['F:\\University\\4th Bachelor\\4E4 Research Project\\GeosyntheticsProgram\\GeosyntheticAnalyser'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn','win32timezone','six','packaging','packaging.version','webbrowser','kivy','enchant'],
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
          *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins +  gstreamer.dep_bins)],
          name='GeosyntheticAnalyser',
          debug=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          console=False, icon='F:\\University\\4th Bachelor\\4E4 Research Project\\GeosyntheticsProgram\\iconImage.ico' )