# A GUERRA DE E NOCCHIE — la mappa delle celle esagonali colorata per comune (seconda immagine del post della sera e della domenica).
# Uso: python3 zone.py zone.json out.jpg   → stampa la riga per la didascalia
# zone.json = risultato di `select public.tg_zone();` (oggetto {cella: [{paese,nome,punti,giocatori}...]}, cella = «h<q>_<r>»;
# le chiavi con i vecchi nomi a cerchi (noccioleti, lago…) vengono ignorate). Stessa matematica di engine/tg-zone.js.
import sys, json, os, math, re
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__))
F = lambda n, s: ImageFont.truetype(os.path.join(QUI, 'font', n), s)
R = 300; SQ3 = math.sqrt(3); BOUNDS = (-3300, 8000, -4700, 3200); ETTARI = round(2.598 * R * R / 10000)
# le contrade: nomi per le celle (stessa lista di engine/tg-zone.js)
CONTRADE = [
 ('noccioleti', 'I noccioleti', 2800, -250, 450), ('caprarola', 'Caprarola', 2330, -170, 330), ('carbognano', 'Carbognano', 3240, -520, 330),
 ('fabrica', 'Fabrica', 4000, -620, 450), ('forre', 'E forre', 4300, 330, 350), ('falerii', 'Falerii', 5250, 970, 420), ('soratte', 'O Soratte', 6300, 1450, 900),
 ('ronciglione', 'Ronciglione', 1480, 1580, 420), ('lago', 'O lago', 252, 800, 600), ('riva', 'A riva de Vico', -854, 250, 420), ('riserva', 'A Riserva', -480, -1000, 520),
 ('venere', 'Monte Venere', 250, -1300, 420), ('caldera', 'A caldera', -1030, -1750, 420), ('fogliano', 'Monte Fogliano', -1440, 555, 450), ('cimino', 'O Cimino', 1200, -2900, 560),
 ('viterbo', 'Viterbo', -750, -3300, 520), ('cinghiale', 'O bosco de o cinghiale', 1250, -1550, 420), ('airone', "I campi de l'airone", 900, 250, 360)]
COLORI = {'caprarola': '#d8432a', 'fabrica': '#2f7fd1', 'carbognano': '#2e9e5b', 'ronciglione': '#e0a21b', 'canepina': '#8e44ad', 'vallerano': '#16a085', 'soriano': '#c0392b', 'civita-castellana': '#7f8c8d', 'viterbo': '#f39c12', 'nepi': '#1abc9c', 'vignanello': '#9b59b6', 'corchiano': '#e67e22', 'sutri': '#3498db', 'vetralla': '#27ae60', 'bassano-romano': '#d35400', 'fuori': '#95a5a6'}
def colore(p):
    if not p: return (70, 74, 70)
    if p in COLORI: h = COLORI[p].lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    import colorsys; hh = 0
    for c in p: hh = (hh * 31 + ord(c)) % 360
    r, g, b = colorsys.hls_to_rgb(hh / 360, .5, .55); return (int(r * 255), int(g * 255), int(b * 255))
def cella_xy(q, r): return R * 1.5 * q, R * SQ3 * (r + q / 2)
def cella_da_id(k):
    m = re.match(r'^h(-?\d+)_(-?\d+)$', k or ''); return (int(m.group(1)), int(m.group(2))) if m else None
def angoli(x, z): return [(x + R * math.cos(math.pi / 3 * i), z + R * math.sin(math.pi / 3 * i)) for i in range(6)]
def tutte():
    out = []
    for q in range(-8, 20):
        for r in range(-19, 12):
            x, z = cella_xy(q, r)
            if BOUNDS[0] < x < BOUNDS[1] and BOUNDS[2] < z < BOUNDS[3]: out.append((f'h{q}_{r}', x, z))
    return out
def contrada(x, z):
    best, bd = None, 1e12
    for k in CONTRADE:
        d = (x - k[2]) ** 2 + (z - k[3]) ** 2
        if d < k[4] * k[4] * 2.2 and d < bd: bd, best = d, k
    return best
def disegna(Z, out):
    W = 1080; minX, maxX, minZ, maxZ = BOUNDS
    MH = int(W * (maxZ - minZ) / (maxX - minX)); TOP = 150; H = TOP + MH + 170
    sx = lambda v: (v - minX) / (maxX - minX) * W; sz = lambda v: TOP + (v - minZ) / (maxZ - minZ) * MH
    im = Image.new('RGB', (W, H), (15, 21, 20)); d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, 0, W, TOP - 10], fill=(120, 78, 40))
    d.text((60, 40), 'A GUERRA DE E NOCCHIE', font=F('Poppins-Bold.ttf', 44), fill=(247, 240, 224))
    d.text((60, 98), f'Chi tiene cosa, negli ultimi 7 giorni · una cella so\' {ETTARI} ettari', font=F('Poppins-Medium.ttf', 24), fill=(230, 215, 190))
    tot = {}
    for cid, x, z in tutte():
        l = Z.get(cid) or []; pad = l[0]['paese'] if l else None
        col = colore(pad); pts = [(sx(a), sz(b)) for a, b in angoli(x, z)]
        d.polygon(pts, fill=col + (165 if pad else 18,), outline=(255, 255, 255, 60 if not pad else 140))
        if pad: tot[pad] = tot.get(pad, 0) + 1
    for zid, nome, x, z, r in CONTRADE:
        if zid in ('noccioleti', 'airone', 'cinghiale', 'riva'): continue  # troppo vicine alle altre: si leggono male
        cx, cy = sx(x), sz(z); f = F('Poppins-Bold.ttf', 20)
        t = nome[2:] if nome[:2] in ('O ', 'A ', 'E ', 'I ') else nome
        w = d.textlength(t, font=f)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((cx - w / 2 + dx, cy - f.size / 2 + dy), t, font=f, fill=(0, 0, 0))
        d.text((cx - w / 2, cy - f.size / 2), t, font=f, fill=(255, 255, 255))
    # legenda (ettari per comune)
    y = TOP + MH + 20; x0 = 60; f = F('Poppins-Bold.ttf', 26)
    nomi = {}
    for l in Z.values():
        for r in l: nomi[r['paese']] = r['nome']
    for p, n in sorted(tot.items(), key=lambda q: -q[1]):
        t = f"{nomi.get(p, p)} {n * ETTARI} ha"; w = d.textlength(t, font=f) + 40
        if x0 + w > W - 60: x0 = 60; y += 40
        d.ellipse([x0, y + 6, x0 + 20, y + 26], fill=colore(p)); d.text((x0 + 28, y), t, font=f, fill=(247, 240, 224)); x0 += w + 10
    if not tot: d.text((60, y), 'Nessuna cella ha ancora un padrone: a prima è de chi ce va.', font=f, fill=(247, 240, 224))
    d.text((60, H - 50), 'grandtuscia.netlify.app', font=F('Poppins-Medium.ttf', 22), fill=(150, 160, 150))
    im.save(out, quality=90, optimize=True)
    return tot, nomi
def riga(Z, tot, nomi):
    if not tot: return "⚔ A guerra de e nocchie è cominciata: a Tuscia è tutta terra de nessuno, a prima cella è de chi ce va."
    parti = [f"{nomi.get(p, p)} {n * ETTARI} ettari" for p, n in sorted(tot.items(), key=lambda q: -q[1])[:4]]
    contese = []
    for k, l in Z.items():
        qr = cella_da_id(k)
        if not qr or len(l) < 2: continue
        x, z = cella_xy(*qr); c = contrada(x, z)
        contese.append((c[1] if c else 'a campagna', l[0]['nome'], l[1]['nome'], l[0]['punti'] - l[1]['punti']))
    contese.sort(key=lambda q: q[3]); c = contese[0] if contese else None
    s = "⚔ A guerra de e nocchie: " + ', '.join(parti)
    if c: s += f". A cella più contesa sta a {c[0]}: {c[1]} tiene {c[2]} a {c[3]} punt{'o' if c[3] == 1 else 'i'}."
    return s
if __name__ == '__main__':
    Z = json.load(open(sys.argv[1])); tot, nomi = disegna(Z, sys.argv[2]); print(riga(Z, tot, nomi))
