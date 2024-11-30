<div align="center">

# Bakaláříček

![GitHub License](https://img.shields.io/github/license/MortikCZ/Bakalaricek)
![GitHub repo size](https://img.shields.io/github/repo-size/MortikCZ/Bakalaricek)
![GitHub last commit](https://img.shields.io/github/last-commit/MortikCZ/Bakalaricek)

Discord bot pro zásílání zpráv o změnách v rozvrhu ze systému [Bakaláři](https://bakalari.cz/).

</div>

## Základní informace 

- Bot je napsán v jazyce Python s využitím knihovny [discord.py](https://discordpy.readthedocs.io/en/stable/).
- Bot je určen pro zasílání notifikací o změnách v rozvrhu ze systému [Bakaláři](https://bakalari.cz/).
- Bot sbírá data z veřejného rozvrhu [Bakawebu](https://bakalari.sosasou.cz/bakaweb/timetable/public).

## Konfigurace

1. Vytvořte soubor `config.json` v kořenovém adresáři bota.
2. Do souboru vložte následující:
```json
{
    "token": "token_bota",
    "timetable_url": "https://bakalari.skola.cz/bakaweb/Timetable/Public/Actual/Class/4U",
    "next_week_timetable_url": "https://bakalari.skola.cz/bakaweb/Timetable/Public/Next/Class/4U",
    "notification_channel_id": ID_kanálu_pro_notifikace,
    "role_id": ID_role_pro_notifikace,
    "status": "status_bota"
}
```
3. Vyplňte
    - `token` - token vašeho bota
    - `timetable_url` - odkaz na aktuální rozvrh
    - `next_week_timetable_url` - odkaz na rozvrh na příští týden
    - `notification_channel_id` - ID kanálu, kam se budou posílat notifikace
    - `role_id` - ID role, která bude mít možnost posílat notifikace
    - `status` - status bota
4. Nainstalovat závislosti pomocí `pip install -r requirements.txt`.

## Příkazy

- `/status <status>` - nastaví status Právě hraje.

## Verze vydání
- ### [v1.0.0](https://github.com/MortikCZ/Bakalaricek/releases/tag/v1.0.0)
  - První release

