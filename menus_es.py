# -*- coding: utf-8 -*-
"""Menús de la colección en español.

Aplica los datos de menus_es.dat sobre los archivos del propio juego del usuario: imágenes con texto de los menús
(pausa, carrusel, reproductor de música, pantallas de carga), textos de los menús y las tildes y la ñ de las fuentes.
No lleva nada de Konami: todo lo que hay en menus_es.dat está dibujado o escrito desde cero.
"""
import base64
import json
import os
import shutil
import tempfile
import zlib

SEED = "25G/xpvTbsb+6"
KEYLEN = "64"


class MenusError(Exception):
    pass


def cargar(res_dir):
    ruta = os.path.join(res_dir, "menus_es.dat")
    return json.loads(zlib.decompress(open(ruta, "rb").read()).decode("utf-8"))


def _editar(tool, run_tool, entry, work, version, fn):
    """Abre un .psb.m del juego, deja que `fn(json, carpeta_de_streams)` lo modifique y lo vuelve a empaquetar."""
    d = tempfile.mkdtemp(dir=work)
    base = os.path.basename(entry)
    shutil.copy2(entry, d)
    run_tool(tool, "m", "unpack", d, "zlib", SEED, KEYLEN)
    psb = os.path.join(d, base[:-2])
    if not os.path.isfile(psb):
        raise MenusError("No pude abrir %s" % base)
    for f in os.listdir(d):
        if f.endswith(".m"):
            os.remove(os.path.join(d, f))
    run_tool(tool, "psb", "deserialize", psb)
    jp, sd = psb + ".json", psb + ".streams"
    j = json.load(open(jp, encoding="utf-8"))
    fn(j, sd)
    with open(jp, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    run_tool(tool, "psb", "serialize", "--version", str(version), jp)
    shutil.rmtree(sd, ignore_errors=True)
    os.remove(jp)
    run_tool(tool, "m", "pack", d, "zlib", SEED, KEYLEN)
    shutil.copy2(psb + ".m", entry)
    shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------ imágenes
def _poner(buf, ancho, x, y, w, h, datos):
    """Copia un bloque RGBA de w x h en (x, y) de la textura (ancho en píxeles)."""
    for r in range(h):
        o = ((y + r) * ancho + x) * 4
        buf[o:o + w * 4] = datos[r * w * 4:(r + 1) * w * 4]


def _borrar(buf, ancho, x, y, w, h):
    fila = bytes(w * 4)
    for r in range(h):
        o = ((y + r) * ancho + x) * 4
        buf[o:o + w * 4] = fila


def _sprites(item):
    def fn(j, sd):
        for t in item["texturas"]:
            fuente = j["source"][t["tex"]]
            tex = fuente["texture"]
            if int(tex["width"]) != t["ancho"] or int(tex["height"]) != t["alto"]:
                raise MenusError("La textura de %s no tiene el tamaño esperado." % item["ruta"])
            ruta = os.path.join(sd, "stream_%d" % t["stream"])
            buf = bytearray(open(ruta, "rb").read())
            if len(buf) < t["ancho"] * t["alto"] * 4:
                raise MenusError("La textura de %s está incompleta." % item["ruta"])
            for op in t["ops"]:
                if op[0] == "clear":
                    _borrar(buf, t["ancho"], *op[1:5])
                else:
                    _poner(buf, t["ancho"], op[1], op[2], op[3], op[4], zlib.decompress(base64.b64decode(op[5])))
            open(ruta, "wb").write(buf)
            for n, (l, tp, w, h, ox, oy) in t["iconos"].items():
                ic = fuente["icon"][n]
                ic["left"], ic["top"], ic["width"], ic["height"], ic["originX"], ic["originY"] = l, tp, w, h, ox, oy
            if "truncated_height" in tex:
                tex["truncated_height"] = max(int(tex["truncated_height"]), t["trunc_alto"])
    return fn


# ------------------------------------------------------------------ fuentes
UMBRAL = 40


def _filas(buf, ancho, x, y, w, h):
    return [bytearray(buf[(y + r) * ancho + x:(y + r) * ancho + x + w]) for r in range(h)]


def _sin_punto(filas, b):
    """Quita de una 'i' el punto (la primera banda con tinta) para dejar el trazo vertical."""
    i = 0
    while i < len(filas) and not any(filas[i]):
        i += 1
    while i < len(filas) and any(filas[i]):
        i += 1
    while i < len(filas) and not any(filas[i]):
        i += 1
    return filas[i:], b - i


def _quitar_vacias_arriba(filas, b):
    i = 0
    while i < len(filas) - 1 and not any(filas[i]):
        i += 1
    return filas[i:], b - i


def _con_acento(base, b, acento, hueco, sin_punto):
    filas = [bytearray(r) for r in base]
    if sin_punto:
        filas, b = _sin_punto(filas, b)
    else:
        filas, b = _quitar_vacias_arriba(filas, b)
    w = len(filas[0])
    tinta = [(min(c for c, v in enumerate(r) if v > UMBRAL), max(c for c, v in enumerate(r) if v > UMBRAL)) for r in filas if any(v > UMBRAL for v in r)]
    cx = (min(t[0] for t in tinta) + max(t[1] for t in tinta) + 1) / 2.0
    aw, ah, ab64 = acento
    ab = zlib.decompress(base64.b64decode(ab64))
    x0 = int(round(cx - aw / 2.0))
    x0 = max(0, min(w - aw, x0))
    nuevas = [bytearray(w) for _ in range(ah + hueco)]
    for r in range(ah):
        nuevas[r][x0:x0 + aw] = ab[r * aw:(r + 1) * aw]
    return nuevas + filas, b + ah + hueco


def _fuente(item):
    def fn(j, sd):
        code = j["code"]
        ruta = os.path.join(sd, "stream_%d" % item["stream"])
        buf = bytearray(open(ruta, "rb").read())
        ancho, alto = item["ancho"], item["alto"]
        if len(buf) < ancho * alto:
            raise MenusError("La fuente tiene un formato inesperado.")
        glifos = []
        for car, base, nombre, sp in item["glifos"]:
            g = code[base]
            if g["id"] != item["id"]:
                raise MenusError("La letra %s no está en la textura esperada." % base)
            x, y, w, h = int(g["x"]), int(g["y"]), int(g["w"]), int(g["h"])
            filas, b = _con_acento(_filas(buf, ancho, x, y, w, h), int(g["b"]), item["acentos"][nombre], item["hueco"], sp)
            glifos.append((car, filas, b, g))
        for car, orig, baja in item["rotados"]:
            g = code[orig]
            x, y, w, h = int(g["x"]), int(g["y"]), int(g["w"]), int(g["h"])
            filas = _filas(buf, ancho, x, y, w, h)[::-1]
            glifos.append((car, [bytearray(r[::-1]) for r in filas], len(filas) - 1 - baja, g))
        # colocación en la franja libre (con 2 px de margen entre celdas)
        cx, cy, fila_h = 1, item["y0"], 0
        for car, filas, b, g in glifos:
            w, h = len(filas[0]), len(filas)
            if cx + w + 2 > ancho:
                cx, cy, fila_h = 1, cy + fila_h + 2, 0
            if cy + h + 2 > alto:
                raise MenusError("No hay sitio para las tildes en la fuente.")
            for r in range(h):
                o = (cy + r) * ancho + cx
                if any(buf[o:o + w]) and buf[o:o + w] != filas[r]:      # (si ya se había aplicado, queda igual)
                    raise MenusError("La zona reservada de la fuente no está libre.")
                buf[o:o + w] = filas[r]
            e = code[car]
            e["id"] = item["id"]
            e["x"], e["y"] = float(cx), float(cy)
            e["w"], e["h"] = g["w"], h
            e["b"], e["a"], e["d"] = b, b - item["dy"], float(b + item["dd"])
            e["width"], e["height"] = g["width"], g["height"]
            cx += w + 2
            fila_h = max(fila_h, h)
        open(ruta, "wb").write(buf)
    return fn


# ------------------------------------------------------------------ textos
def _poner_texto(nodo, texto):
    """'spa' lo usa Steam en «español (España)»; cualquier otro idioma que el juego no tenga (como el español
    latinoamericano) cae en 'eng'. Se escribe el mismo texto en las dos ranuras."""
    for ranura in ("spa", "eng"):
        actual = nodo.get(ranura)
        nodo[ranura] = [texto] if isinstance(actual, list) or (actual is None and isinstance(nodo.get("eng"), list)) else texto


def _textos(item):
    def fn(j, sd):
        if item.get("copiar_spa_a_eng"):
            for nodo in j.values():
                if isinstance(nodo, dict) and "spa" in nodo and "eng" in nodo:
                    nodo["eng"] = nodo["spa"]
        for ruta, texto in item["ediciones"]:
            nodo = j
            for k in ruta:
                nodo = nodo.get(k) if isinstance(nodo, dict) else None
                if nodo is None:
                    break
            if isinstance(nodo, dict):
                if item.get("solo_eng"):
                    nodo["eng"] = [texto] if isinstance(nodo.get("eng"), list) else texto
                else:
                    _poner_texto(nodo, texto)
    return fn


def aplicar(tool, raw, work, run_tool, log, res_dir):
    datos = cargar(res_dir)

    def entrada(ruta):
        ent = os.path.join(raw, *ruta.split("/")) + ".m"
        if not os.path.isfile(ent):
            raise MenusError("No encuentro %s en el juego." % ruta)
        return ent

    for item in datos["archivos"]:
        log("  menús: %s" % os.path.basename(item["ruta"]))
        _editar(tool, run_tool, entrada(item["ruta"]), work, item.get("ver", 3), _sprites(item))
    for item in datos.get("fuentes", []):
        log("  tildes: %s" % os.path.basename(item["ruta"]))
        _editar(tool, run_tool, entrada(item["ruta"]), work, item.get("ver", 2), _fuente(item))
    for item in datos.get("textos", []):
        log("  textos: %s" % os.path.basename(item["ruta"]))
        _editar(tool, run_tool, entrada(item["ruta"]), work, item.get("ver", 2), _textos(item))
