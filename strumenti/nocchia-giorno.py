# A NOCCHIA DE O GIORNO — card del mattino con l'indizio del posto dove sta la nocchia d'oro nel gioco.
# Stessa regola di engine/tg-nocchia-giorno.js: n = giorni dal 1970-01-01 (data locale), luogo = luoghi[(n*11) % len] (21 luoghi raggiungibili, le vette e Viterbo sono esclusi).
# Uso: python3 nocchia-giorno.py 2026-11-10 out.jpg   → stampa anche la didascalia
import sys, json, os, datetime as dt
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(QUI, 'font', n)
W, H = 1080, 1350
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
CAT = {'luoghi': 'un luogo', 'natura': 'un posto de natura', 'storia': 'un posto de storia', 'attivita': "un'attività", 'tradizioni': 'na tradizione'}
LUOGHI = json.load(open(os.path.join(QUI, 'luoghi.json')))
def scelta(g):
    n = g.toordinal() - dt.date(1970, 1, 1).toordinal()
    return LUOGHI[(n * 11) % len(LUOGHI)]
def avvolgi(d, s, f, max_w):
    righe, riga = [], ''
    for w in s.split(' '):
        t = (riga + ' ' + w).strip()
        if d.textlength(t, font=f) <= max_w: riga = t
        else: righe.append(riga); riga = w
    righe.append(riga); return righe
def disegna(g, out):
    L = scelta(g)
    im = Image.new('RGB', (W, H), (247, 240, 224)); d = ImageDraw.Draw(im)
    # nocchia d'oro stilizzata al centro alto
    foto = Image.open(os.path.join(QUI, 'nocchia-foto.jpg')).resize((960, 576), Image.LANCZOS)
    m = Image.new('L', foto.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, 959, 575], radius=28, fill=255)
    im.paste(foto, (60, 160), m)
    d.text((60, 60), 'A NOCCHIA DE O GIORNO', font=ImageFont.truetype(F('Poppins-Bold.ttf'), 30), fill=(120, 78, 40))
    t = f'{g.day} {MESI[g.month-1]}'; f = ImageFont.truetype(F('Poppins-Medium.ttf'), 26); d.text((W-60-d.textlength(t, font=f), 62), t, font=f, fill=(150, 130, 100))
    d.text((60, 104), 'Oggi sta nascosta in ' + CAT.get(L['cat'], 'un posto') + ' de a Tuscia.', font=ImageFont.truetype(F('Poppins-Medium.ttf'), 30), fill=(90, 70, 40))
    fi = ImageFont.truetype(F('Lora-Italic-Variable.ttf'), 42)
    righe = avvolgi(d, '«' + L['short'] + '»', fi, 900); y = 790
    for r in righe: d.text(((W-d.textlength(r, font=fi))/2, y), r, font=fi, fill=(40, 30, 20)); y += 56
    fb = ImageFont.truetype(F('Poppins-Bold.ttf'), 34)
    for r in ['Entra ne o mondo, cerca o fascio de luce,', 'prendila: +10 nocchie pe\' o paese tuo.']:
        y += 8; d.text(((W-d.textlength(r, font=fb))/2, y + 30), r, font=fb, fill=(120, 78, 40)); y += 44
    d.rectangle([0, H-120, W, H], fill=(120, 78, 40))
    t = 'Vale solo oggi  ·  grandtuscia.netlify.app'; f = ImageFont.truetype(F('Poppins-Bold.ttf'), 28)
    d.text(((W-d.textlength(t, font=f))/2, H-78), t, font=f, fill=(247, 240, 224))
    im.save(out, quality=90, optimize=True)
    return L
def didascalia(g, L):
    return (f"🌰 A NOCCHIA DE O GIORNO, {g.day} {MESI[g.month-1]}.\n"
            f"Oggi sta nascosta in {CAT.get(L['cat'], 'un posto')} de a Tuscia: «{L['short']}»\n"
            f"Chi la trova porta 10 nocchie a o paese suo. Vale solo oggi, poi cambia posto.\n\n"
            f"👉 Entra ne o mondo, cerca o fascio de luce d'oro e prendila prima de l'altri paesi: "
            f"https://grandtuscia.netlify.app/?utm_source=facebook&utm_campaign=nocchia\n"
            f"#NocchiaDeOGiorno #TronoDeENocchie #Tuscia #TusciaGames")
if __name__ == '__main__':
    g = dt.date.fromisoformat(sys.argv[1]); L = disegna(g, sys.argv[2]); print(didascalia(g, L))
