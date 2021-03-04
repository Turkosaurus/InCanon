# InCanon
RPG notebook for players and GMs

Based, in part, on final submission to CS50x

---

## Summary
"InCanon" uses a relational database to collaboratively build a compendium of
all the people, places, items, and quests that animate a role-playing campaign setting.

Players and Game Masters can join their own shared campaign in which everyone
views the index of notable entries as their home page, and anyone can add new information.

Database schema are available on scratchpad.txt.

## Features
- Security
    - passwords only stored as hashed values, never plaintext
    - input sanitation to guard against SQL injection attacks

- Persistent Database
    - user data
    - campaign data
    - site feedback

## Technologies Used
- Flask
    - Python
    - WSGI
    - Gunicorn

- Database
    - Sqlite3
    - Postgres 

---

# TODOs

## Bugs
- ~~Place association handling need to be updated in some routes of application.py or the corresponding templates~~

## Needed Impovements
- Ablity to edit existing information
    1. quests
    2. people
    3. the rest

## Upcoming & Feature Requests
- Bonds and Grudges
- Dice roller
- Import bulk data into campaign
    - seed new campaign with CSV data (alternately, expand new campaign creation pages)
    - external "chat logs"

## Someday Maybe
- Live timeline of events
    - timeline search
- Virtual Tabletop environment integration