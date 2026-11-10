# O DERBY DE DOMANI — un solo paese nel titolo, i suoi numeri veri in classifica, una stoccata. (Formula del post su Ronciglione
# dell'8/11: 4.575 persone e 65 clic contro i 100–300 delle altre serie.)
# Uso: python3 derby.py classifica.json DATA out.jpg  → stampa la didascalia. DATA = giorno di pubblicazione (YYYY-MM-DD).
import sys, json, os, datetime as dt
from PIL import Image, ImageDraw, ImageFont
QUI = os.path.dirname(os.path.abspath(__file__)); F = lambda n: os.path.join(QUI, 'font', n)
W, H = 1080, 1350
GIALLO, VERDE, ROSSO, CARTA, SCURO = (242,199,78), (23,32,31), (216,67,42), (243,231,203), (17,24,22)
LINK = 'https://grandtuscia.netlify.app/?utm_source=facebook&utm_campaign=derby'
PUNTI_A_TESTA = 30   # il massimo che un giocatore porta al comune in un giorno

# Stoccate per comune: (gancio in dialetto, tono). Sempre affettuose, mai offensive, niente parolacce.
STOCCATE = {
 'caprarola': ["Caprarola c'ha Palazzo Farnese. Bello. Ma o palazzo nun raccoie nocchie.", "Caprolatti, dite «macchè» pe' dì sì. Allora: giocate pe' Caprarola? Macchè."],
 'carbognano': ["Carbognano c'ha o cammello Armando. E mo' c'ha pure a classifica.", "Carbugnanesi, edè: ve stanno a guardà tutti."],
 'ronciglione': ["Ronciglione c'ha o Carnevale più bello de a Tuscia. Pe' tre giorni l'anno. E l'altri 362?", "Ronciglionesi, i cavalli scossi correno da soli. Voi no."],
 'fabrica': ["Fabrica è prima. Ma i primi se guardano sempre e spalle.", "Fabrichesi, a discesa de i carrettini a sapete a memoria. A classifica pure?"],
 'canepina': ["Canepina: i maccaroni co' e noci e 'n paese che nun se arrende.", "Canepinesi, siete pochi ma ve contate tutti."],
 'civita-castellana': ["Civita Castellana fa e ceramiche de tutto o mondo. E in classifica sta sotto a 'n paese de tremila anime.", "Civitonici, 'na città intera e giocano in tre?"],
 'soriano': ["Soriano c'ha a faggeta più bella de o Lazio. E in classifica nun c'ha gnente.", "Sorianesi, a castagna de Vallerano a guardate male. A classifica manco a guardate."],
 'vallerano': ["Vallerano: e castagne più bone. In classifica: zero. Le castagne nun contano.", "Valleranesi, dieci de voi bastano pe' passà mezza Tuscia."],
 'viterbo': ["Viterbo porta a Macchina de Santa Rosa: cento facchini, cinque tonnellate. E in classifica sta dietro a i paesi.", "Viterbesi, «io so' de città». E a città 'ndo sta, in classifica?"],
 'nepi': ["Nepi c'ha l'acqua minerale. Frizzante. A classifica, piatta.", "Nepesini, ve state a fa' aspettà."],
 'sutri': ["Sutri c'ha l'anfiteatro de i romani. Pubblico: tanto. Giocatori: zero.", "Sutrini, l'anfiteatro è pieno e a classifica è vota."],
 'vignanello': ["Vignanello c'ha o vino. Se sa chi beve de più. In classifica nun se sa gnente.", "Vignanellesi, 'n bicchiere e 'na partita."],
 'corchiano': ["Corchiano c'ha e forre e 'n cuore grosso. Famme vedé quanto.", "Corchianesi, paese piccolo, classifica «a testa»: è fatta pe' voi."],
 'bassano-romano': ["Bassano Romano c'ha a villa e o bosco. E mo' pure 'n posto in classifica.", "Bassanesi, ve sete svejati. Nun ve riaddormentate."],
 'vetralla': ["Vetralla c'ha l'olio. A classifica, secca.", "Vetrallesi, 'na partita costa meno de 'n litro d'olio."],
 'vejano': ["Vejano c'ha o castello. E 'n giocatore solo. Che fa tutto da solo.", "Vejanesi, uno de voi sta a tenè su o paese. Dateje 'na mano."],
}
def stoccata(paese, n): L = STOCCATE.get(paese) or [f"{n} sta in classifica. Pe' mo'."]; return L[dt.date.today().toordinal() % len(L)]

def scegli(d, giorno):
    """Alterna: giorni dispari → il comune che insegue (fa punti ma non è primo); giorni pari → un rivale che dorme."""
    righe = d.get('righe', []); sil = d.get('silenti', []) or []
    primo = righe[0] if righe else None
    insegue = [r for r in righe[1:]]
    insegue.sort(key=lambda r: -(r.get('oggi') or 0))
    k = giorno.toordinal()
    if k % 2 == 1 and insegue:
        r = insegue[(k // 2) % len(insegue)]
        sopra = next((x for x in righe if x.get('pos') == (r.get('pos') or 0) - 1), None) or primo   # il comune subito sopra: obiettivo raggiungibile
        return 'insegue', r, sopra
    # rivali che dormono: prima quelli con giocatori che hanno scelto il paese (silenti), poi la lista fissa
    fissi = ['Soriano nel Cimino', 'Vallerano', 'Viterbo', 'Nepi', 'Sutri', 'Vignanello', 'Corchiano', 'Vetralla', 'Civita Castellana']
    sil = [s for s in sil if not primo or s != primo['nome']]
    fissi = [f for f in fissi if f not in sil and (not primo or f != primo['nome'])]
    j = k // 2
    nome = sil[(j // 2) % len(sil)] if sil and j % 2 == 0 else fissi[(j // 2) % len(fissi)]   # un giorno chi ha scelto il paese e dorme, un giorno un rivale storico
    r = next((x for x in righe if x['nome'] == nome), None) or {'nome': nome, 'punti': 0, 'pos': None}
    return 'dorme', r, primo
ID = {'Fabrica di Roma': 'fabrica', 'Caprarola': 'caprarola', 'Carbognano': 'carbognano', 'Ronciglione': 'ronciglione', 'Canepina': 'canepina', 'Civita Castellana': 'civita-castellana', 'Soriano nel Cimino': 'soriano', 'Vallerano': 'vallerano', 'Viterbo': 'viterbo', 'Nepi': 'nepi', 'Sutri': 'sutri', 'Vignanello': 'vignanello', 'Corchiano': 'corchiano', 'Bassano Romano': 'bassano-romano', 'Vetralla': 'vetralla', 'Vejano': 'vejano'}
def gent(nome):
    return {'Fabrica di Roma': 'Fabrichesi', 'Caprarola': 'Caprolatti', 'Carbognano': 'Carbugnanesi', 'Ronciglione': 'Ronciglionesi', 'Canepina': 'Canepinesi', 'Civita Castellana': 'Civitonici', 'Soriano nel Cimino': 'Sorianesi', 'Vallerano': 'Valleranesi', 'Viterbo': 'Viterbesi', 'Nepi': 'Nepesini', 'Sutri': 'Sutrini', 'Vignanello': 'Vignanellesi', 'Corchiano': 'Corchianesi', 'Bassano Romano': 'Bassanesi', 'Vetralla': 'Vetrallesi', 'Vejano': 'Vejanesi'}.get(nome, 'Gente de ' + nome)

def testi(tipo, r, primo):
    nome = r['nome']; pid = r.get('paese') or ID.get(nome, '')
    g = stoccata(pid, nome)
    if tipo == 'insegue' and primo:
        diff = primo['punti'] - r['punti']; persone = max(1, -(-diff // PUNTI_A_TESTA))
        titolo = f"{nome.upper()} {r['punti']} · {primo['nome'].upper()} {primo['punti']}"
        risposta = f"Ve mancano {diff} nocchie: {persone} person{'a' if persone == 1 else 'e'} che giocano domani."
        cap = (f"{nome.upper()}, SIETE A {diff} NOCCHIE DA {primo['nome'].upper()}.\n{g}\n"
               f"Classifica de stasera: {primo['nome']} {primo['punti']} ({primo.get('pos') or '?'}º), {nome} {r['punti']} ({r.get('pos') or '?'}º" + (f", +{r['oggi']} oggi" if r.get('oggi') else '') + ").\n"
               f"{gent(nome)}, bastano {persone} de voi che giocano domani: ogni partita so' fino a 30 nocchie pe' o paese.")
    else:
        titolo = f"{nome.upper()}: {r['punti']} NOCCHIE" if r.get('punti') else f"{nome.upper()}: ZERO"
        if primo: risposta = f"{primo['nome']} ne c'ha {primo['punti']}. E voi state a dormì."
        else: risposta = "E a classifica è aperta."
        cap = (f"{nome.upper()}, {'ZERO' if not r.get('punti') else str(r['punti']) + ' NOCCHIE'}. {g}\n"
               + (f"Stasera in classifica: {primo['nome']} {primo['punti']}, {nome} {r.get('punti') or 0}.\n" if primo else '')
               + f"{gent(nome)}, dieci de voi bastano pe' entrà ne i primi tre: scegliete {nome} e giocate 5 minuti.")
    cap += f"\n\n👉 Gioca pe' {nome}, gratis dal telefono, senza scaricà gnente: {LINK}\n#SfidaDeiComuni #TronoDeENocchie #{nome.replace(' ', '')} #Tuscia #TusciaGames"
    return titolo, g, risposta, cap

def font(p, s): return ImageFont.truetype(F(p), s)
def avvolgi(d, s, f, max_w):
    righe = []
    for par in s.split('\n'):
        riga = ''
        for w in par.split(' '):
            t = (riga + ' ' + w).strip()
            if d.textlength(t, font=f) <= max_w: riga = t
            else: righe.append(riga); riga = w
        righe.append(riga)
    return righe
def blocco(d, s, p, size_max, max_w, max_h):
    for size in range(size_max, 36, -4):
        f = font(p, size); righe = avvolgi(d, s, f, max_w); h = len(righe) * size * 1.08
        if h <= max_h: return f, righe, h
    return f, righe, h
def disegna(titolo, gancio, risposta, out, stile):
    bg = {'giallo': GIALLO, 'verde': VERDE, 'rosso': ROSSO}[stile]; im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im); M = 72
    col1 = SCURO if stile == 'giallo' else CARTA; col2 = SCURO if stile == 'giallo' else (GIALLO if stile == 'verde' else CARTA); pied = (60, 50, 20) if stile == 'giallo' else (235, 225, 200)
    d.text((M, 70), 'SFIDA DE I COMUNI', font=font('Poppins-Bold.ttf', 30), fill=col2); d.text((M + 300, 70), ' · O TRONO DE E NOCCHIE', font=font('Poppins-Medium.ttf', 30), fill=pied)
    f0, r0, h0 = blocco(d, titolo, 'Poppins-Bold.ttf', 72, W - 2 * M, 200)
    f1, r1, h1 = blocco(d, gancio, 'Poppins-Bold.ttf', 96, W - 2 * M, 480)
    f2, r2, h2 = blocco(d, risposta, 'Poppins-Medium.ttf', 52, W - 2 * M, 260)
    y = 190
    for r in r0: d.text((M, y), r, font=f0, fill=col2); y += f0.size * 1.08
    y += 30
    for r in r1: d.text((M, y), r, font=f1, fill=col1); y += f1.size * 1.08
    y += f1.size * 0.22; d.rectangle([M, y, M + 140, y + 10], fill=col2); y += 44
    for r in r2: d.text((M, y), r, font=f2, fill=col2); y += f2.size * 1.12
    d.rectangle([M, H - 120, W - M, H - 118], fill=pied)
    d.text((M, H - 100), 'Gratis dal telefono, niente da installare', font=font('Poppins-Medium.ttf', 26), fill=pied)
    f = font('Poppins-Bold.ttf', 32); d.text((W - M - d.textlength('grandtuscia.netlify.app', font=f), H - 102), 'grandtuscia.netlify.app', font=f, fill=col2)
    im.save(out, quality=90, optimize=True)
if __name__ == '__main__':
    d = json.load(open(sys.argv[1]));
    if isinstance(d, list): d = d[0].get('tg_classifica_sera', d[0])
    giorno = dt.date.fromisoformat(sys.argv[2]); out = sys.argv[3]
    tipo, r, primo = scegli(d, giorno); titolo, g, risposta, cap = testi(tipo, r, primo)
    disegna(titolo, g, risposta, out, ['rosso', 'verde', 'giallo'][giorno.toordinal() % 3])
    print(cap)
