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
def padrone(l): return l[0] if l and l[0].get('punti', 0) > 0 else None
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
    d.text((60, 96), "Ogni terreno è de o paese che c'ha raccolto più nocchie questa settimana", font=F('Poppins-Medium.ttf', 23), fill=(230, 215, 190))
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
if __name__ == '__main__':
    Z = json.load(open(sys.argv[1])); tot, nomi, liberi = disegna(Z, sys.argv[2]); print(riga(Z, tot, nomi, liberi))
