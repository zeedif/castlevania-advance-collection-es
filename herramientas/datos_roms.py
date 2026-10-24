# -*- coding: utf-8 -*-
"""Regenera datos.json, que usa el instalador para reconocer las ROMs de la colección y los parches.

Uso:
    python datos_roms.py <carpeta system/roms del juego (ya abierta)> <Circle.gba> <Harmony.gba> <Aria.gba> <salida datos.json>

Las ROMs originales de GBA (las de la versión «limpia» de cada juego) solo se usan para localizar qué bytes cambió Konami
en las ROMs de la colección. En datos.json solo quedan las huellas SHA-1 y los rangos de posiciones (sin bytes de las ROMs).
"""
import hashlib
import json
import os
import sys

ENTRADAS = ['01_Circle_US.patch_210614m.bin', '02_Byakuya_EU.patch_210520m.bin', '03_Akatsuki_EU.patch_210623m.bin']
RELLENO = {'02_Byakuya_EU.patch_210520m.bin': 255, '03_Akatsuki_EU.patch_210623m.bin': 0}
# huellas SHA-1 de los parches .ips que reconoce el instalador
PARCHES = {
    '325bc62f3106692d48183d4ecf06e36f0995d986': 'circle',    # Wastor v1.0 (Circle of the Moon, USA)
    '572ade56eef83a72b833d63ffb5476f3b750610d': 'harmony',   # Kishne v2.0 Update 3 (Harmony of Dissonance, Europa)
    '0d0d6fd430d407b5de1ea7baa2f6cbfe808bb66f': 'aria',      # Wastor v1.0 (Aria of Sorrow, Europa)
}


def main():
    roms_dir, c, h, a, salida = sys.argv[1:6]
    datos = {'roms': {}, 'runs': {}, 'relleno': RELLENO, 'parches_conocidos': PARCHES}
    for nombre, orig in zip(ENTRADAS, (c, h, a)):
        k = open(os.path.join(roms_dir, nombre), 'rb').read()
        o = open(orig, 'rb').read()
        if len(k) != len(o):
            raise SystemExit('%s: el tamaño no coincide con la ROM original' % nombre)
        runs, i = [], 0
        while i < len(k):
            if k[i] != o[i]:
                j = i
                while j < len(k) and k[j] != o[j]:
                    j += 1
                runs.append([i, j])
                i = j
            else:
                i += 1
        datos['roms'][nombre] = hashlib.sha1(k).hexdigest()
        datos['runs'][nombre] = runs
        print(nombre, datos['roms'][nombre], len(runs), 'rangos')
    json.dump(datos, open(salida, 'w'), separators=(',', ':'))


if __name__ == '__main__':
    main()
