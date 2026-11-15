# A GUERRA DE I TERRENI — la mappa dei terreni co' e nocchie colorata per paese (seconda immagine del post della sera e della domenica).
# Uso: python3 terre.py terre.json out.jpg   → stampa la riga per la didascalia
# terre.json = risultato di `select public.tg_terre();` (oggetto {"t:<terreno>": [{paese,nome,punti,giocatori}...top3]}, settimana corrente).
# terreni.json (qui accanto) = posizioni dei terreni, strade e lago, esportati dal gioco.
import sys, json, os
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__))
F = lambda n, s: ImageFont.truetype(os.path.join(QUI, 'font', n), s)
G = json.load(open(os.path.join(QUI, 'terreni.json')))
BOUNDS = (-1500, 6200, -3700, 2300)   # x min/max, z min/max (dove stanno i terreni)
COLORI = {'caprarola': '#d8432a', 'fabrica': '#2f7fd1', 'carbognano': '#2e9e5b', 'ronciglione': '#e0a21b', 'canepina': '#8e44ad', 'vallerano': '#16a085', 'soriano': '#c0392b', 'civita-castellana': '#7f8c8d', 'viterbo': '#f39c12', 'nepi': '#1abc9c', 'vignanello': '#9b59b6', 'corchiano': '#e67e22', 'sutri': '#3498db', 'vetralla': '#27ae60', 'bassano-romano': '#d35400', 'gallese': '#2c3e50', 'fuori': '#95a5a6'}
def colore(p):
    if not p: return (70, 74, 70)
    if p in COLORI: h = COLORI[p].lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    import colorsys; hh = 0
    for c in p: hh = (hh * 31 + ord(c)) % 360
    r, g, b = colorsys.hls_to_rgb(hh / 360, .5, .55); return (int(r * 255), int(g * 255), int(b * 255))
def breve(n):
    for a in ('Il ', 'I ', 'La ', 'Le ', 'Lo '):
        if n.startswith(a): return n[len(a):]
    return n
SOGLIA = 10   # come o gioco (engine/tg-terre.js): pe' tenè un terreno bisogna stà davanti de almeno 10, sennò è conteso
def padrone(l):
    if not l or l[0].get('punti', 0) <= 0: return None
    return l[0] if len(l) < 2 or l[0]['punti'] - l[1].get('punti', 0) >= SOGLIA else None
def disegna(Z, out):
    W = 1080; minX, maxX, minZ, maxZ = BOUNDS
    MH = int(W * (maxZ - minZ) / (maxX - minX)); TOP = 150; H = TOP + MH + 190
    sx = lambda v: (v - minX) / (maxX - minX) * W; sz = lambda v: TOP + (v - minZ) / (maxZ - minZ) * MH
    k = W / (maxX - minX)
    im = Image.new('RGB', (W, H), (24, 33, 28)); d = ImageDraw.Draw(im, 'RGBA')
    for x, z in G.get('acqua', []): d.rectangle([sx(x - 40), sz(z - 40), sx(x + 40), sz(z + 40)], fill=(52, 104, 140))
    for s in G['strade']:
        pts = [(sx(a), sz(b)) for a, b in s['p']]
        if len(pts) > 1: d.line(pts, fill=(205, 190, 160, 150), width=4 if s.get('k') == 'asfalto' else 2)
    d.rectangle([0, 0, W, TOP - 10], fill=(120, 78, 40))
    d.text((60, 36), 'A GUERRA DE I TERRENI', font=F('Poppins-Bold.ttf', 44), fill=(247, 240, 224))
    d.text((60, 96), "Ogni terreno è de o paese che l'ha comprato co' e nocchie questa settimana", font=F('Poppins-Medium.ttf', 23), fill=(230, 215, 190))
    tot, nomi = {}, {}
    for l in Z.values():
        for r in l: nomi[r['paese']] = r['nome']
    for t in G['terre']:
        p = padrone(Z.get(t['id']) or []); pad = p['paese'] if p else None
        r = max(9, t['r'] * k * .55); cx, cy = sx(t['x']), sz(t['z'])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colore(pad) + (235 if pad else 70,), outline=(255, 255, 255, 220 if pad else 90), width=3 if pad else 1)
        if pad: tot[pad] = tot.get(pad, 0) + 1
    for nome, (x, z) in G['paesi'].items():
        if not (minX < x < maxX and minZ < z < maxZ): continue
        f = F('Poppins-Bold.ttf', 24); w = d.textlength(nome, font=f); cx, cy = sx(x), sz(z) - 34
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)): d.text((cx - w / 2 + dx, cy + dy), nome, font=f, fill=(0, 0, 0))
        d.text((cx - w / 2, cy), nome, font=f, fill=(255, 255, 255))
    y = TOP + MH + 22; x0 = 60; f = F('Poppins-Bold.ttf', 28)
    liberi = len(G['terre']) - sum(tot.values())
    for p, n in sorted(tot.items(), key=lambda q: -q[1]):
        t = f"{nomi.get(p, p)} {n}"; w = d.textlength(t, font=f) + 40
        if x0 + w > W - 60: x0 = 60; y += 44
        d.ellipse([x0, y + 7, x0 + 22, y + 29], fill=colore(p)); d.text((x0 + 30, y), t, font=f, fill=(247, 240, 224)); x0 += w + 12
    if tot: y += 48
    d.text((60, y), f"Liberi: {liberi} terreni su {len(G['terre'])}: a chi ce va prima.", font=F('Poppins-Medium.ttf', 24), fill=(200, 205, 195))
    d.text((60, H - 46), 'grandtuscia.netlify.app', font=F('Poppins-Medium.ttf', 22), fill=(150, 160, 150))
    im.save(out, quality=90, optimize=True)
    return tot, nomi, liberi
def riga(Z, tot, nomi, liberi):
    if not tot: return f"⚔ A guerra de i terreni: tutti i {len(G['terre'])} terreni so' ancora liberi. O primo che ce raccoje se li pija pe' o paese suo."
    parti = [f"{nomi.get(p, p)} {n} terren{'o' if n == 1 else 'i'}" for p, n in sorted(tot.items(), key=lambda q: -q[1])[:4]]
    T = {t['id']: t for t in G['terre']}; contese = []
    for k, l in Z.items():
        if len(l) >= 2 and l[0]['punti'] > 0 and k in T: contese.append((breve(T[k]['nome']), l[0]['nome'], l[1]['nome'], l[0]['punti'] - l[1]['punti']))
    contese.sort(key=lambda q: q[3]); c = contese[0] if contese else None
    s = "⚔ A guerra de i terreni: " + ', '.join(parti) + f". Liberi: {liberi}"
    if c: s += f". O più conteso è o {c[0]}: {c[1]} sta davanti a {c[2]} de {c[3]} nocchi{'a' if c[3] == 1 else 'e'}"
    return s + '.'

# ---- i terreni accesi e a battaglia de un giorno: stessa scelta de o gioco (engine/tg-terre.js calcolaAccesi) ----
CENTRI = {'fabrica': (4080, -640), 'carbognano': (3230, -470), 'caprarola': (2280, -170), 'falerii': (5330, 960), 'ronciglione': (1560, 1620), 'viterbo': (-750, -3350), 'pantanacce': (-900, -900)}
NOMI_ZONA = {'fabrica': 'Fabrica', 'carbognano': 'Carbognano', 'caprarola': 'Caprarola', 'falerii': 'Falerii', 'ronciglione': 'Ronciglione', 'viterbo': 'Viterbo', 'pantanacce': 'e Pantanacce'}
def fnv(s):
    h = 2166136261
    for ch in s:
        h ^= ord(ch); h = (h * 16777619) & 0xffffffff
    return h
def zona(t):
    return min(CENTRI, key=lambda k: (t['x'] - CENTRI[k][0]) ** 2 + (t['z'] - CENTRI[k][1]) ** 2)
def accesi(giorno):
    gr = {}
    for t in G['terre']:
        if t['id'] == 't:podere': continue
        gr.setdefault(zona(t), []).append(t)
    s = {'t:podere'}
    for k, l in gr.items():
        for t in sorted(l, key=lambda t: fnv(giorno + t['id']))[:3]: s.add(t['id'])
    return s
def battaglia(giorno):
    a = [i for i in accesi(giorno) if i != 't:podere']
    i = min(a, key=lambda i: fnv('battaglia' + giorno + i))
    t = next(t for t in G['terre'] if t['id'] == i)
    return t, NOMI_ZONA[zona(t)]
def trono(Z, out):
    """Card de a domenica: o paese che tiene più terreni se prende o Trono."""
    tot, nomi = {}, {}
    for l in Z.values():
        for r in l: nomi[r['paese']] = r['nome']
    for t in G['terre']:
        p = padrone(Z.get(t['id']) or [])
        if p: tot[p['paese']] = tot.get(p['paese'], 0) + 1
    cl = sorted(tot.items(), key=lambda q: -q[1])
    W, H = 1080, 1350; im = Image.new('RGB', (W, H), (20, 26, 23)); d = ImageDraw.Draw(im)
    if not cl:
        return None
    vin, n = cl[0]; col = colore(vin)
    for y in range(H):
        f = max(0, 1 - y / 900); d.line([(0, y), (W, y)], fill=tuple(int(c * f + (20, 26, 23)[i] * (1 - f)) for i, c in enumerate(col)))
    def cen(t, y, f, fill):
        w = d.textlength(t, font=f); d.text(((W - w) / 2 + 3, y + 4), t, font=f, fill=(0, 0, 0)); d.text(((W - w) / 2, y), t, font=f, fill=fill)
    cen('👑' if False else 'O TRONO DE E NOCCHIE', 150, F('Poppins-Bold.ttf', 58), (247, 240, 224))
    cen('VA A', 300, F('Poppins-Bold.ttf', 60), (247, 240, 224))
    nome = nomi.get(vin, vin).upper(); fs = 130
    while d.textlength(nome, font=F('Poppins-Bold.ttf', fs)) > W - 120 and fs > 60: fs -= 6
    cen(nome, 400, F('Poppins-Bold.ttf', fs), (255, 255, 255))
    cen(f"{n} terren{'o' if n == 1 else 'i'} tenuti a a fine de a settimana", 600, F('Poppins-Medium.ttf', 40), (247, 240, 224))
    y = 760
    for i, (p, k) in enumerate(cl[1:6], 2):
        t = f"{i}. {nomi.get(p, p)} · {k}"; d.ellipse([300, y + 12, 330, y + 42], fill=colore(p)); d.text((350, y), t, font=F('Poppins-Bold.ttf', 40), fill=(230, 222, 205)); y += 66
    cen('Lunedì se riparte da zero: grandtuscia.netlify.app', H - 110, F('Poppins-Medium.ttf', 32), (200, 205, 195))
    im.save(out, quality=90, optimize=True)
    return vin, nomi.get(vin, vin), n

# ---- a sfida de a settimana: due paesi, 12 campi de confine (stessa scelta de engine/tg-sfida.js + tg-terre.js calcolaAccesi) ----
import datetime
PROGRAMMA = {'2026-11-09': ('fabrica', 'carbognano'), '2026-11-16': ('fabrica', 'carbognano')}
ROTA = [('fabrica', 'carbognano'), ('caprarola', 'ronciglione')]
NOMI_SF = {'fabrica': 'Fabrica', 'carbognano': 'Carbognano', 'caprarola': 'Caprarola', 'ronciglione': 'Ronciglione', 'viterbo': 'Viterbo'}
def sfida(giorno):
    d = datetime.date.fromisoformat(giorno); lun = d - datetime.timedelta(days=d.weekday())
    if lun.isoformat() in PROGRAMMA: return PROGRAMMA[lun.isoformat()], lun
    n = round((lun - datetime.date(2026, 11, 16)).days / 7); return ROTA[n % len(ROTA)], lun
def campi_sfida(P):
    a, b = CENTRI[P[0]], CENTRI[P[1]]; mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; out = []
    for q in P:
        l = [t for t in G['terre'] if t['id'] != 't:podere' and zona(t) == q]
        l.sort(key=lambda t: ((t['x'] - mx) ** 2 + (t['z'] - mz) ** 2) ** .5); out += l[:6]
    return out
def punteggio_sfida(Z, giorno):
    P, lun = sfida(giorno); tot = {P[0]: 0, P[1]: 0}; campi = campi_sfida(P)
    for t in campi:
        l = [r for r in (Z.get(t['id']) or []) if r['paese'] in P and r.get('punti', 0) > 0]
        if l: tot[max(l, key=lambda r: r['punti'])['paese']] += 1
    return P, tot, len(campi) - sum(tot.values()), lun
def card_sfida(Z, giorno, out, finale=False):
    P, tot, liberi, lun = punteggio_sfida(Z, giorno); a, b = P; na, nb = tot[a], tot[b]
    W, H = 1080, 1350; im = Image.new('RGB', (W, H), (20, 26, 23)); d = ImageDraw.Draw(im)
    ca, cb = colore(a), colore(b)
    for y in range(H):
        f = max(0, 1 - y / 1000)
        d.line([(0, y), (W // 2, y)], fill=tuple(int(c * f + (20, 26, 23)[i] * (1 - f)) for i, c in enumerate(ca)))
        d.line([(W // 2, y), (W, y)], fill=tuple(int(c * f + (20, 26, 23)[i] * (1 - f)) for i, c in enumerate(cb)))
    def cen(t, y, f, fill, x=W / 2):
        w = d.textlength(t, font=f); d.text((x - w / 2 + 3, y + 4), t, font=f, fill=(0, 0, 0)); d.text((x - w / 2, y), t, font=f, fill=fill)
    if finale and na != nb:
        v, p = (a, b) if na > nb else (b, a)
        cen('O DERBY DE A SETTIMANA', 120, F('Poppins-Bold.ttf', 46), (247, 240, 224))
        fs = 140
        while d.textlength(NOMI_SF[v].upper(), font=F('Poppins-Bold.ttf', fs)) > W - 100: fs -= 8
        cen(NOMI_SF[v].upper(), 300, F('Poppins-Bold.ttf', fs), (255, 255, 255))
        cen('HA BATTUTO', 480, F('Poppins-Bold.ttf', 64), (247, 240, 224))
        cen(NOMI_SF[p].upper(), 580, F('Poppins-Bold.ttf', 90), (230, 222, 205))
    else:
        cen('O DERBY DE A SETTIMANA', 120, F('Poppins-Bold.ttf', 46), (247, 240, 224))
        cen(NOMI_SF[a].upper(), 290, F('Poppins-Bold.ttf', 100), (255, 255, 255))
        cen('contro', 440, F('Poppins-Medium.ttf', 44), (230, 222, 205))
        cen(NOMI_SF[b].upper(), 520, F('Poppins-Bold.ttf', 100), (255, 255, 255))
    cen(f"{na}   –   {nb}", 760, F('Poppins-Bold.ttf', 190), (255, 255, 255))
    cen('campi presi', 990, F('Poppins-Medium.ttf', 38), (230, 222, 205))
    if liberi and not finale: cen(f"{liberi} campi ancora liberi", 1050, F('Poppins-Medium.ttf', 34), (200, 205, 195))
    cen('Lunedì se riparte: grandtuscia.netlify.app' if finale else 'Gioca pe\' o paese tuo: grandtuscia.netlify.app', H - 110, F('Poppins-Medium.ttf', 32), (220, 225, 215))
    im.save(out, quality=90, optimize=True)
    return P, tot, liberi
def riga_sfida(P, tot, liberi, giorno, finale=False):
    a, b = P; na, nb = tot[a], tot[b]; A, B = NOMI_SF[a], NOMI_SF[b]
    dom = datetime.date.fromisoformat(giorno).weekday() == 6
    if finale:
        if na == nb: return f"⚔ O derby finisce pari: {A} {na} – {B} {nb}. Lunedì se riparte."
        v, p = (A, B) if na > nb else (B, A)
        return f"🏆 {v} ha battuto {p}: {max(na, nb)} campi a {min(na, nb)}. Lunedì a rivincita."
    s = f"⚔ O DERBY: {A} {na} – {B} {nb}"
    if liberi: s += f" · {liberi} campi ancora liberi"
    s += '. ' + ("Stanotte a mezzanotte se chiude: chi se pija l'ultimi campi?" if dom else "Domenica sera vince chi tiene più campi.")
    if na == nb: s += ' Tutto aperto.'
    else: s += f" {A if na < nb else B} deve rimonta'."
    return s

# ---- a rivalità de a sera: i due paesi più vicini in classifica de i terreni (o derby vive solo ne i post) ----
def rivali(Z):
    tot, nomi = {}, {}
    for l in Z.values():
        for r in l: nomi[r['paese']] = r['nome']
    for t in G['terre']:
        p = padrone(Z.get(t['id']) or [])
        if p: tot[p['paese']] = tot.get(p['paese'], 0) + 1
    cl = sorted((q for q in tot.items() if q[0] != 'fuori'), key=lambda q: -q[1])
    if len(cl) < 2: return None
    ok = [i for i in range(len(cl) - 1) if cl[i + 1][1] >= 2] or [0]   # niente rivalità tra paesi co' un terreno solo, se se pò
    i = min(ok, key=lambda i: ((cl[i][1] - cl[i + 1][1]) / (cl[i][1] + cl[i + 1][1]), i))
    return cl[i], cl[i + 1], i + 1, nomi
def corto(n): return n.split(' (')[0].replace(' di Roma', '').replace(' Castellana', ' C.')
def card_rivali(Z, out):
    r = rivali(Z)
    if not r: return None
    (a, na), (b, nb), pos, nomi = r; A, B = corto(nomi.get(a, a)), corto(nomi.get(b, b))
    W, H = 1080, 1350; im = Image.new('RGB', (W, H), (20, 26, 23)); d = ImageDraw.Draw(im)
    ca, cb = colore(a), colore(b)
    for y in range(H):
        f = max(0, 1 - y / 1000)
        d.line([(0, y), (W // 2, y)], fill=tuple(int(c * f + (20, 26, 23)[i] * (1 - f)) for i, c in enumerate(ca)))
        d.line([(W // 2, y), (W, y)], fill=tuple(int(c * f + (20, 26, 23)[i] * (1 - f)) for i, c in enumerate(cb)))
    def cen(t, y, fs, fill, bold=True):
        f = F('Poppins-Bold.ttf' if bold else 'Poppins-Medium.ttf', fs)
        while d.textlength(t, font=f) > W - 100 and fs > 40: fs -= 6; f = F('Poppins-Bold.ttf' if bold else 'Poppins-Medium.ttf', fs)
        w = d.textlength(t, font=f); d.text(((W - w) / 2 + 3, y + 4), t, font=f, fill=(0, 0, 0)); d.text(((W - w) / 2, y), t, font=f, fill=fill)
    cen('A RIVALITÀ DE STASERA', 120, 46, (247, 240, 224))
    cen(A.upper(), 290, 100, (255, 255, 255)); cen('contro', 440, 44, (230, 222, 205), False); cen(B.upper(), 520, 100, (255, 255, 255))
    cen(f"{na}   –   {nb}", 760, 190, (255, 255, 255))
    cen('terreni tenuti', 990, 38, (230, 222, 205), False)
    g = na - nb
    cen(('Pari: chi passa davanti?' if g == 0 else f"{g} terren{'o' if g == 1 else 'i'} de differenza") + (f" · {pos}° e {pos + 1}° posto"), 1050, 34, (200, 205, 195), False)
    cen('Gioca pe\' o paese tuo: grandtuscia.netlify.app', H - 110, 32, (220, 225, 215), False)
    im.save(out, quality=90, optimize=True)
    return A, B, na, nb, pos
def riga_rivali(r):
    if not r: return ''
    A, B, na, nb, pos = r; g = na - nb
    if g == 0: return f"⚔ A RIVALITÀ DE STASERA: {A} e {B} so' pari, {na} terreni a testa. Domani chi passa davanti?"
    return f"⚔ A RIVALITÀ DE STASERA: {A} {na} – {B} {nb}. {'Un terreno' if g == 1 else str(g) + ' terreni'} de differenza: {B}, domani o sorpasso?"

if __name__ == '__main__':
    # python3 terre.py terre.json out.jpg            → riga de a guerra pe' a classifica
    # python3 terre.py --battaglia AAAA-MM-GG         → riga de a battaglia de quel giorno (pe' o post de a sera, co' a data de domani)
    # python3 terre.py --trono terre.json out.jpg     → card de a domenica (o Trono) + riga
    # python3 terre.py --sfida terre.json out.jpg [AAAA-MM-GG] [--finale] → card + riga de a sfida de a settimana
    # python3 terre.py --rivali terre.json out.jpg → card + riga de a rivalità de a sera (i due paesi più vicini in classifica)
    if sys.argv[1] == '--rivali':
        Z = json.load(open(sys.argv[2])); print(riga_rivali(card_rivali(Z, sys.argv[3])) or 'Nessuna rivalità: meno de due paesi co\' terreni.')
    elif sys.argv[1] == '--sfida':
        g = next((x for x in sys.argv[4:] if x[:2] == '20'), datetime.date.today().isoformat()); fin = '--finale' in sys.argv
        Z = json.load(open(sys.argv[2])); P, tot, lib = card_sfida(Z, g, sys.argv[3], fin); print(riga_sfida(P, tot, lib, g, fin))
    elif sys.argv[1] == '--battaglia':
        t, z = battaglia(sys.argv[2]); print(f"⚔ Domani se combatte pe' o {breve(t['nome'])} (vicino a {z}): ogni nocchia raccolta lì vale doppio. Chi se o pija domani sera?")
    elif sys.argv[1] == '--trono':
        Z = json.load(open(sys.argv[2])); r = trono(Z, sys.argv[3])
        print(f"👑 O TRONO DE E NOCCHIE va a {r[1]}: {r[2]} terren{'o' if r[2] == 1 else 'i'} tenuti a a fine de a settimana. Lunedì se riparte da zero." if r else 'Nessun terreno tenuto questa settimana.')
    else:
        Z = json.load(open(sys.argv[1])); tot, nomi, liberi = disegna(Z, sys.argv[2]); print(riga(Z, tot, nomi, liberi))
