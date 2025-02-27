# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('icons', 'icons')]
binaries = [('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_multiarray_umath.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_webp.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_struct_ufunc_tests.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imagingmath.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_multiarray_tests.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_simd.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imaging.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_common.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/linalg/_umath_linalg.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_mt19937.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imagingtk.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imagingft.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/fft/_pocketfft_umath.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_pcg64.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/linalg/lapack_lite.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imagingmorph.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/bit_generator.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_operand_flag_tests.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/PIL/_imagingcms.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_philox.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_generator.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/mtrand.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_sfc64.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_umath_tests.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/random/_bounded_integers.cpython-313-darwin.so', '.'), ('/opt/homebrew/lib/python3.13/site-packages/numpy/_core/_rational_tests.cpython-313-darwin.so', '.')]
hiddenimports = ['skimage.filters.edges', 'PIL._tkinter_finder', 'PIL._imagingtk', 'tkinter', 'tkinter.filedialog', 'tkinter.scrolledtext', 'tkinter.ttk', 'numpy.core._dtype_ctypes']
tmp_ret = collect_all('cv2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('skimage')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SlideExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/shen.li/clipimgfromvideo/icons/app_icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SlideExtractor',
)
app = BUNDLE(
    coll,
    name='SlideExtractor.app',
    icon='/Users/shen.li/clipimgfromvideo/icons/app_icon.icns',
    bundle_identifier='com.clipimgfromvideo.slideextractor',
)
