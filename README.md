# Profit District Bot

Bot de Telegram pentru Profit District: onboarding (mentorat, Telegram, Discord, Challenge, Competiții), gamification (XP, niveluri, achievement-uri, streak, leaderboard), Daily Check-In/Check-Out, feedback zilnic, acceptare automată în grup.

## Structură

- `bot.py` — pornește botul, înregistrează toate comenzile/butoanele și job-urile programate (remindere zilnice).
- `config.py` — citește token-ul și link-urile din variabile de mediu.
- `texts.py` — tot textul afișat de bot (aici se editează conținutul, fără cod).
- `keyboards.py` — butoanele (meniurile) afișate sub mesaje.
- `db.py` — baza de date locală (SQLite, fișierul `data.db`) cu datele utilizatorilor.
- `levels.py` / `achievements.py` — pragurile de nivel, beneficiile și achievement-urile.
- `handlers/` — logica fiecărei secțiuni (meniu, mentorat, broker, challenge, competiție, profil, nivel, leaderboard, check-in/check-out, feedback zilnic, aprobări admin, intrare în grup).

## Rulare locală

```
pip install -r requirements.txt
```

Creează un fișier `.env` (vezi `.env.example`) cu:

```
BOT_TOKEN=token-ul de la @BotFather
ADMIN_CHAT_ID=id-ul de chat Telegram al adminului (vezi mai jos cum îl afli)
WEBSITE_URL=...
TELEGRAM_GROUP_LINK=...
DISCORD_INVITE_LINK=...
FP_MARKETS_LINK=...
PU_PRIME_LINK=...
CONTACT_USERNAME=hanetrades
```

Apoi:

```
python bot.py
```

⚠️ **Nu porni botul local dacă rulează deja pe Railway** — două instanțe cu același token intră în conflict (eroare `Conflict: terminated by other getUpdates request`) și utilizatorii pot pierde mesaje/click-uri. Oprește-l pe Railway sau nu rula local în paralel.

### Cum afli ADMIN_CHAT_ID

Scrie-i botului @userinfobot pe Telegram — îți răspunde cu ID-ul tău numeric. Acela e `ADMIN_CHAT_ID`. Când e completat, botul îți trimite automat o notificare de fiecare dată când cineva trimite date de înscriere sau cere aprobare (mentorat finalizat, Challenge, Eveniment, Competiție, Primul Trade). Poți cere oricând o evidență completă a membrilor scriind `/raport` botului, în chatul tău privat cu el.

## Deploy pe Railway

1. Railway e deja conectat la acest repo GitHub.
2. În Railway, deschide proiectul → tab **Variables** → adaugă aceleași variabile ca în `.env`. Nu pune niciodată token-ul în cod sau în GitHub — doar în Variables.
3. Railway va folosi `Procfile`-ul din repo (`worker: python bot.py`) ca să pornească botul.
4. La fiecare `git push`, Railway redeploy-ează automat botul.

⚠️ **Foarte important — baza de date `data.db`**: sistemul de fișiere de pe Railway e efemer — la fiecare redeploy, `data.db` (cu toți membrii, XP-ul, istoricul check-in/check-out) se poate **pierde definitiv** dacă nu ai atașat un **Railway Volume** montat peste folderul proiectului. Înainte de a considera botul „live" cu utilizatori reali, atașează un Volume în Railway (Settings → Volumes) montat la calea proiectului, altfel orice redeploy viitor șterge toate datele acumulate.

## Editare conținut

Tot textul afișat de bot e în `texts.py`, în română, ușor de editat fără cunoștințe de programare — cauți mesajul după nume și modifici textul dintre ghilimele. Pragurile de nivel și beneficiile sunt în `levels.py`.

## Funcționalități acoperite

- **Onboarding**: Meniu principal, Începe de aici, Mentorat, Telegram/Discord/Telegram+Discord (selector broker + onboarding + trimitere date), Challenge 500 → 5.000, Competiții (înscriere + link Myfxbook), FAQ, Contact, Evenimente, Resurse gratuite.
- **Gamification**: XP pentru fiecare acțiune, niveluri (Rookie → Elite) cu beneficii, achievement-uri, daily streak, leaderboard live.
- **Aprobare admin**: mentorat finalizat, Challenge, Eveniment, Competiție și Primul Trade necesită aprobarea @hanetrades (buton „Aprobă" trimis automat).
- **Daily Check-In / Check-Out**: chestionare zilnice trimise automat dimineața (08:00) și seara (19:00, ora României), plus feedback zilnic (poză win/loss) cu reminder la 20:00.
- **Grup Telegram**: acceptă automat cererile de intrare și trimite un mesaj de bun venit în privat.
- **`/raport`**: comandă doar pentru admin, trimite evidența XP a tuturor membrilor.

## Neincluse încă (posibile extinderi viitoare)

CRM/Admin Panel vizual, Broadcast din panou, Statistici agregate, Referral System, istoric/jurnal vizibil pentru Check-In/Check-Out.
