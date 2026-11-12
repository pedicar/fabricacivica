# A SETTIMANA DE O TRONO — post della domenica: quanto ha raccolto ogni paese in settimana, quanti giocatori, e «o mejo de o paese»
# (il miglior tempo con nome nei giochi a record: tg_fantasmi.nome, chiesto al primo record).
# Uso: python3 settimana.py settimana.json out.jpg   → stampa la didascalia
# settimana.json = risultato della query in README (sezione «Domenica»).
import sys, json, os, datetime as dt
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__))
F = lambda n, s: ImageFont.truetype(os.path.join(QUI, 'font', n), s)
W = 1080
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
GIOCHI = {'carrettini': 'a i carrettini de Fabrica', 'ciminodh': 'a a discesa de a faggeta', 'vicosail': 'a a regata de o lago', 'corseavuoto': 'a a corsa de i cavalli'}
def nome_gioco(g): return GIOCHI.get(g.split(':')[0], 'a ' + g)
def fmt(t):
    t = float(t); m = int(t // 60); s = t - m * 60
    return (f'{m}:{s:04.1f}' if m else f'{s:.1f}') + ' s' if not m else f'{m}:{s:04.1f}'
def disegna(d, out):
    paesi = sorted([p for p in d['paesi'] if p['settimana'] > 0], key=lambda p: -p['settimana'])[:6]
    mejo = (d.get('mejo') or [])[:4]
    H = 270 + 96 * len(paesi) + (110 + 70 * len(mejo) if mejo else 0) + 150
    im = Image.new('RGB', (W, H), (247, 240, 224)); g = ImageDraw.Draw(im)
    g.rectangle([0, 0, W, 150], fill=(120, 78, 40))
    g.text((60, 42), 'A SETTIMANA DE O TRONO', font=F('Poppins-Bold.ttf', 44), fill=(247, 240, 224))
    fine = dt.date.fromisoformat(d['fine']); ini = dt.date.fromisoformat(d['inizio'])
    g.text((60, 100), f'da o {ini.day} a o {fine.day} {MESI[fine.month-1]}', font=F('Poppins-Medium.ttf', 26), fill=(230, 215, 190))
    y = 190
    g.text((60, y), 'Chi ha raccolto de più in settimana', font=F('Poppins-Bold.ttf', 30), fill=(120, 78, 40)); y += 60
    fb, fm, fn = F('Poppins-Bold.ttf', 40), F('Poppins-Medium.ttf', 26), F('Poppins-Bold.ttf', 44)
    massimo = max(p['settimana'] for p in paesi) if paesi else 1
    for i, p in enumerate(paesi):
        col = (217, 119, 6) if i == 0 else (90, 70, 40)
        g.text((60, y), f'{i+1}º', font=fm, fill=(150, 130, 100))
        g.text((130, y - 6), p['nome'], font=fb, fill=col)
        g.text((130, y + 44), f"{p['giocatori']} giocator{'e' if p['giocatori'] == 1 else 'i'} · totale {p['punti']}", font=fm, fill=(150, 130, 100))
        t = f"+{p['settimana']}"; g.text((W - 60 - g.textlength(t, font=fn), y - 8), t, font=fn, fill=col)
        bw = int((W - 120) * p['settimana'] / massimo); g.rectangle([60, y + 82, 60 + bw, y + 88], fill=(242, 199, 78) if i == 0 else (220, 205, 175))
        y += 96
    if mejo:
        y += 30; g.text((60, y), 'O mejo de o paese', font=F('Poppins-Bold.ttf', 30), fill=(120, 78, 40)); y += 50
        fi = F('Lora-Italic-Variable.ttf', 30)
        for m in mejo:
            g.text((60, y), f"«{m['nome']}» de {m['paese_nome']}, {nome_gioco(m['gioco'])} in {fmt(m['tempo'])}", font=fi, fill=(40, 30, 20)); y += 70
    g.rectangle([0, H - 120, W, H], fill=(120, 78, 40))
    t = 'Lunedì se ricomincia  ·  grandtuscia.netlify.app'; f = F('Poppins-Bold.ttf', 28)
    g.text(((W - g.textlength(t, font=f)) / 2, H - 78), t, font=f, fill=(247, 240, 224))
    im.save(out, quality=90, optimize=True)
def didascalia(d):
    paesi = sorted([p for p in d['paesi'] if p['settimana'] > 0], key=lambda p: -p['settimana'])
    fine = dt.date.fromisoformat(d['fine'])
    r = [f"🏆 A SETTIMANA DE O TRONO, {fine.day} {MESI[fine.month-1]}."]
    if paesi:
        p = paesi[0]; r.append(f"Chi ha raccolto de più: {p['nome']}, +{p['settimana']} nocchie in sette giorni co' {p['giocatori']} giocator{'e' if p['giocatori']==1 else 'i'}.")
        if len(paesi) > 1: r.append('Doppo: ' + ', '.join(f"{q['nome']} +{q['settimana']}" for q in paesi[1:4]) + '.')
        dorme = [q for q in d['paesi'] if q['settimana'] <= 0]
        if dorme: r.append(f"Chi ha dormito tutta a settimana: {', '.join(q['nome'] for q in dorme[:3])}. Se sveja?")
    for m in (d.get('mejo') or [])[:4]:
        r.append(f"O mejo de {m['paese_nome']} {nome_gioco(m['gioco'])}: «{m['nome']}», {fmt(m['tempo'])}. Chi lo batte?")
    r.append('')
    r.append("👉 Lunedì se ricomincia da zero co' a settimana nova. Gioca pe' o paese tuo, gratis dal telefono: https://grandtuscia.netlify.app/?utm_source=facebook&utm_campaign=settimana")
    r.append('#TronoDeENocchie #SfidaDeiComuni #Tuscia #TusciaGames')
    return '\n'.join(r)
if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); disegna(d, sys.argv[2]); print(didascalia(d))
