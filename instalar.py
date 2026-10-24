#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Castlevania Advance Collection - traducción al español (Circle of the Moon, Harmony of Dissonance, Aria of Sorrow).

Instalador con interfaz gráfica (tkinter). También funciona por línea de comandos:  python instalar.py --cli [--restaurar]

Qué hace: abre el archivo del juego con MArchiveBatchTool, aplica los parches IPS de los traductores a las ROMs de GBA que lleva la
colección (reubicando antes dos bloques de código de Konami que chocan con los parches de Harmony y Aria), traduce los menús de la
colección y vuelve a empaquetar. Guarda copia de los originales en la carpeta 'backup' junto al instalador.
No distribuye ROMs ni parches de terceros: los parches se reconocen por su hash.
"""
import os, sys, re, json, shutil, struct, hashlib, subprocess, tempfile, threading, zipfile, io, urllib.request, webbrowser

for _f in (sys.stdout, sys.stderr):           # sin consola (exe con ventana) no hay stdout; y la consola de Windows no admite todo
    try:
        _f.reconfigure(errors="replace")
    except Exception:  # noqa
        pass

FROZEN = getattr(sys, "frozen", False)
APP_DIR = os.path.dirname(os.path.abspath(sys.executable if FROZEN else __file__))
RES_DIR = getattr(sys, "_MEIPASS", APP_DIR)           # datos empaquetados dentro del .exe
for _d in (RES_DIR, APP_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)
BACKUP = os.path.join(APP_DIR, "backup")
TOOL_HOME = os.path.join(APP_DIR, "MArchiveBatchTool")
SEED = "25G/xpvTbsb+6"
KEYLEN = "64"
STEAM_SUB = os.path.join("steamapps", "common", "Castlevania Advance Collection")
DATA_DIR = "windata"
TOOL_URL_WIN = "https://github.com/farmerbb/RED-Project/releases/download/tools/MArchiveBatchTool-win-x64.zip"
TOOL_URL_LIN = "https://github.com/farmerbb/RED-Project/releases/download/tools/MArchiveBatchTool-linux-x64.zip"
TOOL_URL = TOOL_URL_WIN if os.name == "nt" else TOOL_URL_LIN
REPO_URL = "https://github.com/zeedif/castlevania-advance-collection-es"
NO_WINDOW = 0x08000000 if os.name == "nt" else 0       # los procesos auxiliares no abren consola

JUEGOS = {
    'circle': dict(entry='01_Circle_US.patch_210614m.bin', nombre='Castlevania: Circle of the Moon', version='americana',
                   autor='Wastor', web='https://wastor.romhackhispano.org/castlevania-circle-of-the-moon/', reubicar=None),
    'harmony': dict(entry='02_Byakuya_EU.patch_210520m.bin', nombre='Castlevania: Harmony of Dissonance', version='europea',
                    autor='Kishne, v2.0 (Update 3)',
                    web='https://www.mediafire.com/download/6cts4vbaath6sa7/Castlevania+-+Harmony+of+Dissonance+2.0+%28Update+3%29+~+By+Kishne.rar',
                    reubicar=dict(src=0x6a0000, n=44, dst=0x6d0000, punteros=[0x313b8])),
    'aria': dict(entry='03_Akatsuki_EU.patch_210623m.bin', nombre='Castlevania: Aria of Sorrow', version='europea',
                 autor='Wastor', web='https://wastor.romhackhispano.org/castlevania-aria-of-sorrow/',
                 reubicar=dict(src=0x660000, n=0x6610be - 0x660000, dst=0x668000, punteros=[0x1cc02c]),
                 tablas=[0x50790c, 0x50881c, 0x50972c]),
}


class InstallError(Exception):
    pass


_log = print


def log(m=""):
    _log(m)


def sha1(data):
    return hashlib.sha1(data).hexdigest()


# ------------------------------------------------------------------ IPS
def ips_records(d):
    if d[:5] != b'PATCH':
        raise InstallError("El archivo no es un parche IPS.")
    i = 5; recs = []
    while True:
        if d[i:i + 3] == b'EOF':
            break
        off = int.from_bytes(d[i:i + 3], 'big'); i += 3
        size = int.from_bytes(d[i:i + 2], 'big'); i += 2
        if size == 0:
            rle = int.from_bytes(d[i:i + 2], 'big'); i += 2
            val = d[i:i + 1]; i += 1
            recs.append((off, rle, val * rle))
        else:
            recs.append((off, size, d[i:i + size])); i += size
    return recs


def overlaps_runs(recs, runs):
    import bisect
    starts = [a for a, _ in runs]
    out = []
    for off, n, data in recs:
        i = max(bisect.bisect_right(starts, off) - 1, 0)
        while i < len(runs) and runs[i][0] < off + n:
            a, b = runs[i]
            lo, hi = max(a, off), min(b, off + n)
            if lo < hi:
                out.append((lo, hi, data[lo - off:hi - off]))
            i += 1
    return out


def aplicar_juego(rom, ips_bytes, clave, datos):
    """ROM de Konami + traducción. Devuelve la ROM resultante."""
    cfg = JUEGOS[clave]
    rom = bytearray(rom)
    recs = ips_records(ips_bytes)
    runs = datos['runs'][cfg['entry']]
    permitidos = []
    r = cfg['reubicar']
    if r:
        dst, n = r['dst'], r['n']
        if any(rom[dst:dst + n]) and any(x != 0xff for x in rom[dst:dst + n]):
            raise InstallError("El destino de la reubicación no está libre en la ROM de %s." % cfg['nombre'])
        for off, size, data in recs:
            if off < dst + n and off + size > dst:
                raise InstallError("El parche escribe donde hay que reubicar código de Konami (%s)." % cfg['nombre'])
        permitidos.append((r['src'], r['src'] + n))
        permitidos += [(p, p + 4) for p in r['punteros']]
    if cfg.get('tablas'):
        permitidos += [(t, t + 1) for t in cfg['tablas']]
    conflictos = []
    for lo, hi, nuevo in overlaps_runs(recs, runs):
        for k in range(lo, hi):
            if any(a <= k < b for a, b in permitidos):
                continue
            if rom[k] != nuevo[k - lo]:
                conflictos.append(k)
    if conflictos:
        raise InstallError("El parche pisa %d bytes que Konami modificó en %s: no encaja con la ROM de la colección."
                           % (len(conflictos), cfg['nombre']))
    if r:
        src, n, dst = r['src'], r['n'], r['dst']
        rom[dst:dst + n] = rom[src:src + n]
        fill = datos.get('relleno', {}).get(cfg['entry'], 0xff)
        for p in r['punteros']:
            old = struct.unpack_from('<I', rom, p)[0]
            if (old & ~1) - 0x08000000 != src:
                raise InstallError("La ROM de %s no es la de la versión 1.0.0 de la colección." % cfg['nombre'])
            struct.pack_into('<I', rom, p, old - src + dst)
        rom[src:src + n] = bytes([fill]) * n
    for off, n, data in recs:
        if off + n > len(rom):
            raise InstallError("El parche IPS agranda la ROM (no soportado).")
        rom[off:off + n] = data
    if cfg.get('tablas'):
        for t in cfg['tablas']:
            rom[t] = rom[t + 4]
    return bytes(rom)


# ------------------------------------------------------------------ juego / herramienta
def steam_libraries():
    roots = []
    home = os.path.expanduser("~")
    for s in (r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam", os.path.join(home, ".local", "share", "Steam"),
              os.path.join(home, ".steam", "steam")):
        if os.path.isdir(s):
            roots.append(s)
            vdf = os.path.join(s, "steamapps", "libraryfolders.vdf")
            try:
                for m in re.finditer(r'"path"\s*"([^"]+)"', open(vdf, encoding="utf-8", errors="ignore").read()):
                    roots.append(m.group(1).replace("\\\\", "\\"))
            except OSError:
                pass
    if os.name == "nt":
        try:
            import winreg
            for hive, key, val in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                                   (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath")):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        v = winreg.QueryValueEx(k, val)[0].replace("/", "\\")
                    roots.append(v)
                    vdf = os.path.join(v, "steamapps", "libraryfolders.vdf")
                    for m in re.finditer(r'"path"\s*"([^"]+)"', open(vdf, encoding="utf-8", errors="ignore").read()):
                        roots.append(m.group(1).replace("\\\\", "\\"))
                except OSError:
                    pass
        except ImportError:
            pass
    for base in ("/run/media", "/media"):
        try:
            for u in os.listdir(base):
                for d in os.listdir(os.path.join(base, u)):
                    roots.append(os.path.join(base, u, d))
        except OSError:
            pass
    seen = set()
    return [r for r in roots if not (r in seen or seen.add(r))]


def find_juego(path=None):
    """Carpeta del juego (la que contiene 'windata'). Acepta la carpeta del juego o la de datos."""
    cands = []
    if path:
        cands += [path, os.path.dirname(path.rstrip("\\/"))]
    else:
        cands += [os.path.join(r, STEAM_SUB) for r in steam_libraries()]
    for c in cands:
        d = os.path.join(c, DATA_DIR)
        if os.path.isfile(os.path.join(d, "alldata.psb.m")) and os.path.isfile(os.path.join(d, "alldata.bin")):
            return os.path.abspath(c)
    return None


def find_tool():
    names = ("MArchiveBatchTool.exe", "MArchiveBatchTool")
    cands = []
    for base in (APP_DIR, TOOL_HOME):
        for n in names:
            cands.append(os.path.join(base, n))
        try:
            for d in os.listdir(base):
                p = os.path.join(base, d)
                if os.path.isdir(p) and d.lower().startswith("marchivebatchtool"):
                    cands += [os.path.join(p, n) for n in names]
        except OSError:
            pass
    for c in cands:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def descargar_herramienta(progress=None):
    os.makedirs(TOOL_HOME, exist_ok=True)
    log("Descargando MArchiveBatchTool...")
    req = urllib.request.Request(TOOL_URL, headers={"User-Agent": "CastlevaniaAdvanceES"})
    with urllib.request.urlopen(req, timeout=60) as r:
        total = int(r.headers.get("Content-Length") or 0)
        buf = io.BytesIO(); got = 0
        for chunk in iter(lambda: r.read(1 << 16), b''):
            buf.write(chunk); got += len(chunk)
            if progress and total:
                progress(got / total)
    log("Descomprimiendo...")
    with zipfile.ZipFile(buf) as z:
        z.extractall(TOOL_HOME)
    t = find_tool()
    if not t:
        raise InstallError("La descarga no contiene MArchiveBatchTool.")
    if os.name != "nt":
        os.chmod(t, 0o755)
    log("MArchiveBatchTool descargada.")
    return t


def run_tool(tool, *args):
    r = subprocess.run([tool] + list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
                       creationflags=NO_WINDOW)
    if r.returncode != 0:
        raise InstallError("MArchiveBatchTool falló (%s):\n%s" % (" ".join(args[:2]), r.stdout[-1500:]))
    return r.stdout


# ------------------------------------------------------------------ parches
class Parche:
    def __init__(self, label, data):
        self.label, self.data = label, data
        self.sha1 = sha1(data)


def _tar_extract(path, dest):
    t = None
    if os.name == "nt":                                      # tar de Windows (bsdtar): lee .rar y .7z; el de Git Bash no
        t = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "tar.exe")
    if not t or not os.path.isfile(t):
        t = shutil.which("bsdtar") or shutil.which("tar")
    if not t:
        return False
    r = subprocess.run([t, "-xf", path, "-C", dest], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NO_WINDOW)
    return r.returncode == 0


def buscar_parches(datos):
    """Reconoce por su hash los .ips que hay en la carpeta del programa: sueltos o dentro de un .zip / .rar / .7z.
    No mira subcarpetas ni nombres. Devuelve ({clave: Parche}, [archivos .ips que no coinciden con ninguna versión conocida])."""
    cands, tmps = [], []
    try:
        entradas = sorted(os.listdir(APP_DIR))
    except OSError:
        entradas = []
    for f in entradas:
        p = os.path.join(APP_DIR, f)
        if not os.path.isfile(p):
            continue
        low = f.lower()
        try:
            if low.endswith(".ips"):
                cands.append(Parche(f, open(p, 'rb').read()))
            elif low.endswith(".zip"):
                with zipfile.ZipFile(p) as z:
                    for n in z.namelist():
                        if n.lower().endswith(".ips"):
                            cands.append(Parche("%s > %s" % (f, os.path.basename(n)), z.read(n)))
            elif low.endswith((".rar", ".7z")):
                tmp = tempfile.mkdtemp(prefix="cvips_"); tmps.append(tmp)
                if _tar_extract(p, tmp):
                    for root, _, files in os.walk(tmp):
                        for n in files:
                            if n.lower().endswith(".ips"):
                                cands.append(Parche("%s > %s" % (f, n), open(os.path.join(root, n), 'rb').read()))
        except (OSError, zipfile.BadZipFile):
            continue
    for t in tmps:
        shutil.rmtree(t, ignore_errors=True)
    found, unknown = {}, []
    for c in cands:
        clave = datos['parches_conocidos'].get(c.sha1)
        if clave:
            found.setdefault(clave, c)
        else:
            unknown.append(c.label)
    return found, unknown


def cargar_datos():
    return json.load(open(os.path.join(RES_DIR, "datos.json"), encoding="utf-8"))


# ------------------------------------------------------------------ proceso
def instalar(juego, tool, parches, datos, menus=True):
    windata = os.path.join(juego, DATA_DIR)
    bin_p, idx_p = os.path.join(windata, "alldata.bin"), os.path.join(windata, "alldata.psb.m")
    os.makedirs(BACKUP, exist_ok=True)
    nueva_copia = False
    for p in (bin_p, idx_p):
        dst = os.path.join(BACKUP, os.path.basename(p))
        if not os.path.exists(dst):
            shutil.copy2(p, dst)
            nueva_copia = True
    if nueva_copia:
        log("Copia de seguridad guardada en la carpeta 'backup'.")
    work = tempfile.mkdtemp(prefix="cvadv_")
    suelto = os.path.join(windata, "alldata.psb")           # la herramienta lo deja junto al índice al abrirlo
    habia_suelto = os.path.exists(suelto)
    try:
        raw = os.path.join(work, "raw")
        log("Abriendo el archivo del juego...")
        run_tool(tool, "archive", "extract", "--codec", "zlib", "--seed", SEED, "--keyLength", KEYLEN, idx_p, raw)
        for clave, parche in parches.items():
            cfg = JUEGOS[clave]
            log("\n%s" % cfg['nombre'])
            ent = os.path.join(raw, "system", "roms", cfg['entry'] + ".m")
            if not os.path.isfile(ent):
                raise InstallError("No encuentro %s en el juego (¿versión distinta?)." % cfg['nombre'])
            tmpd = os.path.join(work, "m_" + clave); os.makedirs(tmpd)
            shutil.copy2(ent, tmpd)
            run_tool(tool, "m", "unpack", tmpd, "zlib", SEED, KEYLEN)
            romp = os.path.join(tmpd, cfg['entry'])
            rom = open(romp, 'rb').read()
            if sha1(rom) != datos['roms'][cfg['entry']]:
                raise InstallError("La ROM de %s no es la original de Konami (¿ya hay otra traducción instalada?).\n"
                                   "Pulsa «Restaurar originales» o usa «Verificar integridad» en Steam." % cfg['nombre'])
            log("  parche: %s" % parche.label)
            open(romp, 'wb').write(aplicar_juego(rom, parche.data, clave, datos))
            run_tool(tool, "m", "pack", tmpd, "zlib", SEED, KEYLEN)
            shutil.copy2(romp + ".m", ent)
            log("  traducción aplicada")
        if menus:
            try:
                import menus_es
            except ImportError:
                raise InstallError("Faltan los datos de los menús (menus_es.py / menus_es.dat) junto al instalador.")
            log("\nMenús de la colección")
            try:
                menus_es.aplicar(tool, raw, work, run_tool, log, RES_DIR)
            except menus_es.MenusError as e:
                raise InstallError("No se pudieron traducir los menús: %s" % e)
        log("\nReconstruyendo el archivo del juego...")
        out = os.path.join(work, "out"); os.makedirs(out)
        run_tool(tool, "archive", "build", "--codec", "zlib", "--seed", SEED, "--keyLength", KEYLEN, raw, os.path.join(out, "alldata"))
        nb, ni = os.path.join(out, "alldata.bin"), os.path.join(out, "alldata.psb.m")
        if not (os.path.isfile(nb) and os.path.isfile(ni)) or os.path.getsize(nb) < 300 * 1024 * 1024:
            raise InstallError("La reconstrucción no generó los archivos esperados.")
        for src, dst in ((nb, bin_p), (ni, idx_p)):
            tmp = dst + ".tmp"
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
        log("Instalación terminada.")
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if not habia_suelto and os.path.exists(suelto):
            try:
                os.remove(suelto)
            except OSError:
                pass


def restaurar(juego):
    windata = os.path.join(juego, DATA_DIR)
    for n in ("alldata.bin", "alldata.psb.m"):
        if not os.path.isfile(os.path.join(BACKUP, n)):
            raise InstallError("No hay copia de seguridad en la carpeta 'backup'.")
    for n in ("alldata.bin", "alldata.psb.m"):
        dst = os.path.join(windata, n)
        shutil.copy2(os.path.join(BACKUP, n), dst + ".tmp")
        os.replace(dst + ".tmp", dst)
    log("Archivos originales restaurados.")


def resumen_final(claves):
    if not claves:
        return
    log("\nEn «Versión del juego» (el icono del globo, al final del carrusel) elige:")
    for k in claves:
        log("  • %s: versión %s" % (JUEGOS[k]['nombre'], JUEGOS[k]['version']))
    if 'aria' in claves:
        log("En Aria of Sorrow, elige «Español» en su pantalla de idioma.")


# ------------------------------------------------------------------ interfaz gráfica
def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import queue

    datos = cargar_datos()
    q = queue.Queue()
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)      # texto nítido en pantallas con escala
        except Exception:  # noqa
            pass
    root = tk.Tk()
    root.title("Castlevania Advance Collection: traducción al español")
    root.geometry("900x640")
    root.minsize(780, 520)
    st = {'juego': None, 'tool': None, 'parches': {}, 'unk': [], 'busy': False, 'manual': None, 'firma': None}
    pad = dict(padx=8, pady=4)
    style = ttk.Style()
    try:
        style.theme_use("vista" if os.name == "nt" else "clam")
    except tk.TclError:
        pass
    try:
        import menus_es  # noqa
        hay_menus = True
    except ImportError:
        hay_menus = False

    frm = ttk.Frame(root, padding=10); frm.pack(fill="both", expand=True)
    ttk.Label(frm, text="Castlevania Advance Collection en español", font=("Segoe UI", 15, "bold")).pack(anchor="w")
    ttk.Label(frm, text="Cierra el juego antes de instalar.").pack(anchor="w", pady=(0, 6))

    f1 = ttk.LabelFrame(frm, text="1. Carpeta del juego"); f1.pack(fill="x", **pad)
    v_game = tk.StringVar()
    ttk.Label(f1, textvariable=v_game, wraplength=680).pack(side="left", padx=8, pady=6, fill="x", expand=True)
    ttk.Button(f1, text="Examinar…", command=lambda: elegir_juego()).pack(side="right", padx=8)

    f2 = ttk.LabelFrame(frm, text="2. MArchiveBatchTool"); f2.pack(fill="x", **pad)
    v_tool = tk.StringVar()
    ttk.Label(f2, textvariable=v_tool, wraplength=680).pack(side="left", padx=8, pady=6, fill="x", expand=True)
    b_tool = ttk.Button(f2, text="Descargar", command=lambda: descargar()); b_tool.pack(side="right", padx=8)

    f3 = ttk.LabelFrame(frm, text="3. Parches junto al programa")
    f3.pack(fill="x", **pad)
    f3.columnconfigure(1, weight=1)
    rows, b_inst = {}, {}
    claves = (["menus"] if hay_menus else []) + list(JUEGOS)
    for i, k in enumerate(claves):
        if k == "menus":
            ttk.Label(f3, text="Menús de la colección", width=34).grid(row=i, column=0, sticky="w", padx=8, pady=5)
        else:
            cfg = JUEGOS[k]
            ttk.Label(f3, text="%s\n%s" % (cfg['nombre'], cfg['autor']), width=34).grid(row=i, column=0, sticky="w", padx=8, pady=3)
            v = tk.StringVar()
            ttk.Label(f3, textvariable=v, wraplength=330).grid(row=i, column=1, sticky="w", padx=4)
            ttk.Button(f3, text="Abrir página", command=lambda u=cfg['web']: webbrowser.open(u)).grid(row=i, column=2, padx=4)
            rows[k] = v
        b = ttk.Button(f3, text="Instalar", command=lambda k=k: instalar_click(k)); b.grid(row=i, column=3, padx=(4, 8))
        b_inst[k] = b
    v_unk = tk.StringVar()
    ttk.Label(f3, textvariable=v_unk, foreground="#a33", wraplength=640).grid(row=len(claves), column=0, columnspan=4, sticky="w", padx=8)

    prog = ttk.Progressbar(frm, mode="determinate", maximum=100); prog.pack(fill="x", padx=8, pady=(8, 2))
    txt = tk.Text(frm, height=10, wrap="word", state="disabled", font=("Consolas", 9)); txt.pack(fill="both", expand=True, **pad)
    f4 = ttk.Frame(frm); f4.pack(fill="x", padx=8)
    a = ttk.Label(f4, text=REPO_URL, foreground="#1a5fb4", cursor="hand2"); a.pack(side="left")
    a.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))
    b_rest = ttk.Button(f4, text="Restaurar originales", command=lambda: restaurar_click()); b_rest.pack(side="right")

    def put(msg):
        txt.configure(state="normal"); txt.insert("end", msg + "\n"); txt.see("end"); txt.configure(state="disabled")

    def sep():
        if txt.get("1.0", "end").strip():
            put("")

    def pump():
        try:
            while True:
                kind, val = q.get_nowait()
                if kind == "log": put(val)
                elif kind == "done": fin(val)
                elif kind == "prog": prog.stop(); prog.configure(mode="determinate", value=val * 100)
        except queue.Empty:
            pass
        root.after(100, pump)

    def firma():
        out = []
        try:
            for f in sorted(os.listdir(APP_DIR)):
                if f.lower().endswith((".ips", ".zip", ".rar", ".7z")):
                    s = os.stat(os.path.join(APP_DIR, f))
                    out.append((f, s.st_size, s.st_mtime_ns))
        except OSError:
            pass
        return tuple(out)

    def refrescar():
        st['juego'] = find_juego(st['manual'])
        v_game.set(st['juego'] or "Falta")
        st['tool'] = find_tool()
        v_tool.set(os.path.basename(st['tool']) if st['tool'] else "Falta")
        b_tool.configure(state="disabled" if st['tool'] else "normal")
        f = firma()
        if f != st['firma']:                                  # los archivos de la carpeta cambiaron (o es la primera vez)
            st['firma'] = f
            st['parches'], st['unk'] = buscar_parches(datos)
        for k, v in rows.items():
            p = st['parches'].get(k)
            v.set(p.label if p else "Falta")
        v_unk.set("Sin reconocer: " + ", ".join(st['unk']) if st['unk'] else "")
        base = bool(st['juego'] and st['tool'] and not st['busy'])
        for k, b in b_inst.items():
            b.configure(state="normal" if base and (k == "menus" or k in st['parches']) else "disabled")
        b_rest.configure(state="normal" if st['juego'] and not st['busy'] and os.path.isfile(os.path.join(BACKUP, "alldata.bin")) else "disabled")

    def set_busy(b):
        st['busy'] = b
        if b:
            for w in list(b_inst.values()) + [b_rest, b_tool]:
                w.configure(state="disabled")
            prog.configure(mode="indeterminate"); prog.start(12)
        else:
            prog.stop(); prog.configure(mode="determinate", value=0)

    def elegir_juego():
        d = filedialog.askdirectory(title="Carpeta de Castlevania Advance Collection")
        if d:
            st['manual'] = d; refrescar()

    def worker(fn):
        def run():
            global _log
            _log = lambda m: q.put(("log", m))
            try:
                fn(); q.put(("done", None))
            except InstallError as e:
                q.put(("done", str(e)))
            except Exception as e:  # noqa
                import traceback
                q.put(("done", "Error inesperado: %s\n%s" % (e, traceback.format_exc()[-800:])))
        set_busy(True)
        threading.Thread(target=run, daemon=True).start()

    def fin(err):
        set_busy(False)
        refrescar()
        if err:
            put("\n¡Error! " + err); messagebox.showerror("No se pudo completar", err[:600])

    def descargar():
        worker(lambda: descargar_herramienta(lambda f: q.put(("prog", f))))

    def instalar_click(k):
        def job():
            if k == "menus":
                instalar(st['juego'], st['tool'], {}, datos, menus=True)
            else:
                instalar(st['juego'], st['tool'], {k: st['parches'][k]}, datos, menus=False)
                resumen_final([k])
        sep()
        worker(job)

    def restaurar_click():
        if messagebox.askyesno("Restaurar", "Se pierden las traducciones instaladas. ¿Restaurar los archivos originales?"):
            sep()
            worker(lambda: restaurar(st['juego']))

    root.bind("<FocusIn>", lambda e: e.widget is root and not st['busy'] and refrescar())
    refrescar(); pump()
    root.mainloop()


# ------------------------------------------------------------------ línea de comandos
def run_cli(a):
    def opt(n):
        return a[a.index(n) + 1] if n in a and a.index(n) + 1 < len(a) else None
    datos = cargar_datos()
    juego = find_juego(opt("--game"))
    if not juego:
        raise InstallError("No encuentro el juego. Usa --game \"<carpeta del juego>\".")
    log("Carpeta del juego: %s" % juego)
    if "--restaurar" in a:
        restaurar(juego); return
    tool = find_tool()
    if not tool:
        raise InstallError("No encuentro MArchiveBatchTool: %s" % TOOL_URL)
    parches, unk = buscar_parches(datos)
    for u in unk:
        log("Se ignora %s (no coincide con ninguna versión conocida)" % u)
    if not parches:
        raise InstallError("No encuentro ningún parche .ips reconocido junto al instalador.")
    for k in JUEGOS:
        log(" %-8s %s" % (k, parches[k].label if k in parches else "(sin parche)"))
    instalar(juego, tool, parches, datos, menus="--sin-menus" not in a)
    resumen_final(list(parches))


def main():
    a = sys.argv[1:]
    try:
        if "--cli" in a or "--restaurar" in a or "--game" in a:
            run_cli(a)
        else:
            try:
                import tkinter  # noqa
            except ImportError:
                run_cli(a); return
            run_gui()
    except InstallError as e:
        log("\n¡Error! %s" % e)
        sys.exit(1)


if __name__ == "__main__":
    main()
