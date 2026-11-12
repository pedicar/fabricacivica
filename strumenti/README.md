# Strumenti del Trono de e Nocchie

Script che il compito automatico delle 21 usa ogni sera. Tutto quello che serve è in questa cartella (font compresi).

- `classifica.py` — immagine della classifica dei comuni (1080×1080…1350).
- `sera.py classifica.json out.jpg` — immagine + didascalia del post della sera, dal JSON di `tg_classifica_sera()`.
- `nocchia-giorno.py YYYY-MM-DD out.jpg` — card con l'indizio della nocchia d'oro di quel giorno + didascalia.
  Stessa regola del gioco (`engine/tg-nocchia-giorno.js`): luogo = `luoghi.json[(giorni dal 1970-01-01) * 11 % 35]`.
- `derby.py classifica.json DATA out.jpg` — il derby di DATA: un solo comune (giorni dispari chi insegue, giorni pari chi dorme), i suoi numeri veri, una stoccata; stampa la didascalia (utm `derby`).
- `settimana.py settimana.json out.jpg` — post della domenica: raccolto di ogni paese in settimana, giocatori, «o mejo de o paese» (nomi da `tg_fantasmi`).
- `zone.py zone.json out.jpg` — mappa de «A guerra de e nocchie» (le zone colorate per comune, ultimi 7 giorni) + la riga per la didascalia. `zone.json` = risultato di `select public.tg_zone();`.
- `luoghi.json` — i 35 luoghi del mondo (id, cat, name, short), nello stesso ordine di `TG.debug.places` senza `lago`.
- `font/` — Poppins Bold/Medium, Lora Italic.

## Procedura della sera (eseguita dal compito pianificato)
1. `SELECT public.tg_classifica_sera();` sul progetto Supabase `wahrowxonkfqsktjmbdg` → salvare il JSON in `classifica.json`.
2. `python3 sera.py classifica.json trono-nocchie/classifica/YYYY-MM-DD.jpg` → didascalia a schermo.
2b. `select public.tg_zone();` → `zone.json`; `python3 zone.py zone.json trono-nocchie/zone/YYYY-MM-DD.jpg` → stampa la riga «⚔ A guerra de e nocchie: …» da inserire nella didascalia della classifica, prima del «👉». L'immagine delle zone è la SECONDA immagine del post della classifica.
3. `python3 nocchia-giorno.py <domani> trono-nocchie/nocchia/<domani>.jpg` → didascalia a schermo.
4. `git add` + commit + push su `main` (le immagini diventano `https://raw.githubusercontent.com/pedicar/fabricacivica/main/trono-nocchie/...`).
5. Metricool, brand TRONO DI NOCCHIE (blogId 7919446, Facebook, fuso Europe/Paris):
   - post della classifica subito (ora + 3 minuti), con l'immagine e la didascalia;
   - post della nocchia alle 8:03 di domani, con l'immagine e la didascalia;
   - post del derby alle 12:37 di domani, con l'immagine e la didascalia.
Regole fisse: sempre call to action a giocare, il motivo e il link con utm; dialetto con o/a/e/i; niente «Rapida».

## Domenica (in più, dopo la procedura della sera)
1. Eseguire questa query e salvare il JSON in `settimana.json`:
```sql
select json_build_object(
 'fine', (select max(giorno) from tg_trono_snap),
 'inizio', (select min(giorno) from tg_trono_snap where giorno >= (select max(giorno) from tg_trono_snap) - 6),
 'paesi', (select json_agg(row_to_json(q) order by q.punti desc) from (
    select s.paese, c.nome, s.punti,
      s.punti - coalesce((select p0.punti from tg_trono_snap p0 where p0.paese = s.paese and p0.giorno = (select min(giorno) from tg_trono_snap where giorno >= s.giorno - 6)), 0) as settimana,
      (select count(distinct dev) from tg_punti_dev d where d.paese = s.paese and d.giorno > s.giorno - 7) as giocatori
    from tg_trono_snap s join tg_comuni c on c.id = s.paese
    where s.giorno = (select max(giorno) from tg_trono_snap)) q),
 'mejo', (select json_agg(row_to_json(m)) from (
    select distinct on (f.gioco, f.paese) f.gioco, f.paese, c.nome as paese_nome, f.nome, f.tempo
    from tg_fantasmi f join tg_comuni c on c.id = f.paese
    where f.nome <> '' and f.creato > now() - interval '7 days'
    order by f.gioco, f.paese, f.tempo) m)
) as settimana;
```
2. `python3 settimana.py settimana.json trono-nocchie/settimana/YYYY-MM-DD.jpg` → didascalia a schermo.
3. Commit + push; su Metricool post Facebook alle 20:40 della domenica (dopo la classifica delle 19:2x), con immagine e didascalia.
