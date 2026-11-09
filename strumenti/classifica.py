# CLASSIFICA DE A SERA — immagine 1080x1350 con la classifica dei comuni del Trono de e Nocchie.
# Uso: python3 classifica.py dati.json out.jpg
# dati.json: {"giorno":"2026-11-10","righe":[{"nome":"Fabrica di Roma","punti":480,"oggi":35,"giocatori":4}], "silenti":["Caprarola","Ronciglione"], "nocchia":"Monte Venere" (opzionale, chi ha trovato la nocchia del giorno: paese o null)}
import sys, json, os, datetime as dt
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(QUI, 'font', n)
W, H = 1080, 1350
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
def font(n, s):
    return ImageFont.truetype(F(n), s)
def disegna(d, out):
    righe = d.get('righe', [])[:8]
    if not d.get('precedente'):
        for r in righe: r.pop('oggi', None)   # prima fotografia: il «+oggi» non ha senso
    g = dt.date.fromisoformat(d['giorno'])
    im = Image.new('RGB', (W, H), (24, 38, 32)); dr = ImageDraw.Draw(im)
    # fascia alta verde scuro con titolo
    dr.rectangle([0, 0, W, 250], fill=(18, 30, 25))
    dr.text((60, 58), 'O TRONO DE E NOCCHIE', font=font('Poppins-Bold.ttf', 30), fill=(232, 190, 90))
    dr.text((60, 100), 'A classifica de stasera', font=font('Poppins-Bold.ttf', 62), fill=(250, 246, 235))
    t = f'{g.day} {MESI[g.month-1]} · aggiornata a e 21'
    dr.text((60, 180), t, font=font('Poppins-Medium.ttf', 28), fill=(170, 180, 165))
    y = 290
    if not righe:
        dr.text((60, y), 'Oggi gnente. Nessuno ha giocato?', font=font('Poppins-Bold.ttf', 40), fill=(250, 246, 235)); y += 70
    pm = max([r['punti'] for r in righe] + [1])
    for i, r in enumerate(righe):
        pos = i + 1
        h = 108 if pos <= 3 else 94
        col = [(232, 190, 90), (205, 205, 205), (196, 132, 80)][pos-1] if pos <= 3 else (60, 78, 68)
        dr.rounded_rectangle([60, y, W-60, y+h-10], radius=18, fill=(34, 52, 44))
        # barra proporzionale
        bw = int((W-120-40) * r['punti'] / pm)
        dr.rounded_rectangle([80, y+h-24, 80+max(bw, 12), y+h-18], radius=3, fill=col if pos <= 3 else (90, 120, 100))
        dr.ellipse([80, y+14, 80+56, y+14+56], fill=col)
        dr.text((80+28, y+14+28), str(pos), font=font('Poppins-Bold.ttf', 30), fill=(24, 38, 32), anchor='mm')
        fs = 40 if pos <= 3 else 32
        dr.text((160, y+14), r['nome'], font=font('Poppins-Bold.ttf', fs), fill=(250, 246, 235))
        p = f"{r['punti']} nocchie"
        fp = font('Poppins-Bold.ttf', 34 if pos <= 3 else 28)
        dr.text((W-80-dr.textlength(p, font=fp), y+16), p, font=fp, fill=col if pos <= 3 else (220, 215, 200))
        sotto = []
        if r.get('oggi'): sotto.append(f"+{r['oggi']} oggi")
        if r.get('giocatori'): sotto.append(f"{r['giocatori']} giocator{'e' if r['giocatori']==1 else 'i'}")
        if sotto:
            fs2 = font('Poppins-Medium.ttf', 24); s = ' · '.join(sotto)
            dr.text((W-80-dr.textlength(s, font=fs2), y+(56 if pos <= 3 else 48)), s, font=fs2, fill=(170, 180, 165))
        y += h
    # chi dorme
    y = y + 40
    sil = d.get('silenti') or []
    if not sil:   # nessun dato sui paesi scelti: pungolo i rivali storici che non hanno punti
        gia = {r['nome'] for r in righe}
        sil = [n for n in ['Caprarola', 'Carbognano', 'Ronciglione', 'Soriano nel Cimino', 'Civita Castellana', 'Viterbo'] if n not in gia][:4]
    if sil:
        dr.text((60, y), 'Zero nocchie oggi:', font=font('Poppins-Bold.ttf', 30), fill=(232, 120, 90))
        fb = font('Poppins-Bold.ttf', 36); yy = y + 44; riga = ''
        for nome in sil[:5]:
            t2 = (riga + ', ' if riga else '') + nome
            if dr.textlength(t2 + ',', font=fb) > W - 120 and riga: dr.text((60, yy), riga + ',', font=fb, fill=(250, 246, 235)); yy += 46; riga = nome
            else: riga = t2
        dr.text((60, yy), riga + '.', font=fb, fill=(250, 246, 235)); yy += 56
        dr.text((60, yy), "Ve sete addormentati o state a fa' finta?", font=font('Lora-Italic-Variable.ttf', 32), fill=(200, 205, 190))
        y = yy + 64
    if d.get('nocchia'):
        dr.text((60, y), f"A nocchia d'oro de oggi l'ha trovata {d['nocchia']}.", font=font('Poppins-Medium.ttf', 28), fill=(232, 190, 90)); y += 50
    # piede: l'immagine è alta quanto serve (minimo quadrata), niente vuoto sotto
    fine = min(H, max(1080, y + 60)); im = im.crop((0, 0, W, fine)); dr = ImageDraw.Draw(im)
    dr.rectangle([0, fine-120, W, fine], fill=(18, 30, 25))
    t = 'Gioca pe\' o paese tuo, gratis dal telefono  ·  grandtuscia.netlify.app'
    f = font('Poppins-Bold.ttf', 26); dr.text(((W-dr.textlength(t, font=f))/2, fine-78), t, font=f, fill=(232, 190, 90))
    im.save(out, quality=90, optimize=True)
if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); disegna(d, sys.argv[2]); print('ok', sys.argv[2])
