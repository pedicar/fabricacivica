# A SERA: dal JSON di tg_classifica_sera() all'immagine e alla didascalia del post delle 21.
# Uso: python3 sera.py classifica.json out.jpg  → stampa la didascalia
import sys, json, datetime as dt
from classifica import disegna, MESI
d = json.load(open(sys.argv[1])); out = sys.argv[2]
if isinstance(d, list): d = d[0].get('tg_classifica_sera', d[0])
disegna(d, out)
g = dt.date.fromisoformat(d['giorno']); righe = d.get('righe', [])
primo = righe[0] if righe else None
if not primo:
    testo = f"🏆 A CLASSIFICA DE STASERA, {g.day} {MESI[g.month-1]}.\nOggi gnente. Nessuno ha raccolto 'na nocchia. Domani ve aspettamo."
elif len(righe) == 1:
    testo = (f"🏆 A CLASSIFICA DE STASERA, {g.day} {MESI[g.month-1]}.\n{primo['nome']} è primo co' {primo['punti']} nocchie. E è pure l'unico.\n"
             f"Tutti l'altri paesi: zero. Zero. Ve sete addormentati o state a fa' finta?")
else:
    sec = righe[1]; dist = primo['punti'] - sec['punti']
    testo = (f"🏆 A CLASSIFICA DE STASERA, {g.day} {MESI[g.month-1]}.\n1º {primo['nome']} ({primo['punti']}), 2º {sec['nome']} ({sec['punti']})"
             + (f", 3º {righe[2]['nome']} ({righe[2]['punti']})" if len(righe) > 2 else '') + '.\n'
             + (f"{sec['nome']} sta a {dist} nocchie da o primo posto: se famo 'na dormita, domani se vede." if dist > 0 else "Pari. Domani se decide."))
    piu = max(righe, key=lambda r: r.get('oggi', 0))
    if piu.get('oggi'): testo += f"\nO paese che ha corso de più oggi: {piu['nome']}, +{piu['oggi']}."
if d.get('nocchia'): testo += f"\n🌰 A nocchia d'oro de oggi l'ha trovata {d['nocchia']}."
testo += ("\n\n👉 Ogni nocchia che raccoi ne o gioco va a o comune tuo. Scegli o paese, gioca 5 minuti, e domani sera a classifica cambia: "
          "https://grandtuscia.netlify.app/?utm_source=facebook&utm_campaign=classifica\n#TronoDeENocchie #SfidaDeiComuni #Tuscia #TusciaGames")
print(testo)
