# Saunatonttu

Saunatonttu tarkistaa joka päivä n. klo 12 Suomen aikaan kuluvan päivän
pörssisähkön hinnan illan tunneille (oletuksena klo 18–21) ja lähettää
push-ilmoituksen puhelimeen, jos hinta on jonain tuntina alle 10 snt/kWh
— eli sauna kannattaa lämmittää.

Hintadata haetaan [Pörssisähkö.net-rajapinnasta](https://porssisahko.net/api),
joka on ilmainen eikä vaadi API-avainta.

## Käyttöönotto

### 1. Asenna ntfy-sovellus puhelimeen

Lataa [ntfy](https://ntfy.sh/) App Storesta / Play Storesta ja keksi itsellesi
salainen "topic"-nimi (esim. `saunatonttu-a8x92k`, mitä satunnaisempi sitä
parempi, koska topicit eivät ole salasanasuojattuja). Tilaa kyseinen topic
sovelluksessa (Subscribe to topic).

### 2. Lisää topic GitHubin Secrets-asetuksiin

Reposta: **Settings → Secrets and variables → Actions → New repository secret**

- Nimi: `NTFY_TOPIC`
- Arvo: valitsemasi topic-nimi (esim. `saunatonttu-a8x92k`)

### 3. Ajastus

Workflow (`.github/workflows/saunatonttu.yml`) on ajastettu ajamaan joka päivä
klo 12:00 Suomen aikaa (kaksi cron-riviä kattaa kesä- ja talviajan, skripti
tarkistaa itse että kellonaika on oikea, joten ylimääräinen ajo ei tee mitään).

Voit myös ajaa workflown käsin: **Actions → Saunatonttu → Run workflow**
(valitse `force_run: true` jos haluat ohittaa kellonaikatarkistuksen ja testata
heti).

## Asetusten muokkaaminen

Ympäristömuuttujat `saunatonttu.py`-skriptille (voi asettaa workflow-tiedostossa):

| Muuttuja | Oletus | Selitys |
|---|---|---|
| `PRICE_THRESHOLD_SNT` | `10.0` | Kynnysarvo snt/kWh, jonka alittuessa ilmoitetaan |
| `WINDOW_START_HOUR` | `18` | Tarkasteluikkunan alkutunti (Suomen aikaa) |
| `WINDOW_END_HOUR` | `21` | Tarkasteluikkunan lopputunti (poissulkeva) |
| `RUN_HOUR_HELSINKI` | `12` | Mihin tuntiin skripti olettaa ajettavan |
| `NTFY_TOPIC` | – | ntfy.sh-topic ilmoituksille (secret) |

## Paikallinen testaus

```bash
pip install -r requirements.txt
FORCE_RUN=1 NTFY_TOPIC=oma-testitopic python saunatonttu.py
```
