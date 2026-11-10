# Strumenti del Trono de e Nocchie

Script che il compito automatico delle 21 usa ogni sera. Tutto quello che serve è in questa cartella (font compresi).

- `classifica.py` — immagine della classifica dei comuni (1080×1080…1350).
- `sera.py classifica.json out.jpg` — immagine + didascalia del post della sera, dal JSON di `tg_classifica_sera()`.
- `nocchia-giorno.py YYYY-MM-DD out.jpg` — card con l'indizio della nocchia d'oro di quel giorno + didascalia.
  Stessa regola del gioco (`engine/tg-nocchia-giorno.js`): luogo = `luoghi.json[(giorni dal 1970-01-01) * 11 % 35]`.
- `derby.py classifica.json DATA out.jpg` — il derby di DATA: un solo comune (giorni dispari chi insegue, giorni pari chi dorme), i suoi numeri veri, una stoccata; stampa la didascalia (utm `derby`).
- `luoghi.json` — i 35 luoghi del mondo (id, cat, name, short), nello stesso ordine di `TG.debug.places` senza `lago`.
- `font/` — Poppins Bold/Medium, Lora Italic.

## Procedura della sera (eseguita dal compito pianificato)
1. `SELECT public.tg_classifica_sera();` sul progetto Supabase `wahrowxonkfqsktjmbdg` → salvare il JSON in `classifica.json`.
2. `python3 sera.py classifica.json trono-nocchie/classifica/YYYY-MM-DD.jpg` → didascalia a schermo.
3. `python3 nocchia-giorno.py <domani> trono-nocchie/nocchia/<domani>.jpg` → didascalia a schermo.
4. `git add` + commit + push su `main` (le immagini diventano `https://raw.githubusercontent.com/pedicar/fabricacivica/main/trono-nocchie/...`).
5. Metricool, brand TRONO DI NOCCHIE (blogId 7919446, Facebook, fuso Europe/Paris):
   - post della classifica subito (ora + 3 minuti), con l'immagine e la didascalia;
   - post della nocchia alle 8:03 di domani, con l'immagine e la didascalia;
   - post del derby alle 12:37 di domani, con l'immagine e la didascalia.
Regole fisse: sempre call to action a giocare, il motivo e il link con utm; dialetto con o/a/e/i; niente «Rapida».
