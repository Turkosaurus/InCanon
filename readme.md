# InCanon
RPG notebook for players and GMs

Based, in part, on final submission to CS50x

---

## Summary
"InCanon" uses a relational database to collaboratively build a compendium of all the people, places, items, and quests that animate a role-playing campaign setting.

Players and Game Masters can join their own shared campaign in which everyone views the index of notable entries as their home page, and anyone can add new information.

To provide context for database associations, original database schema are available on scratchpad.txt.

## Features
- Security
    - passwords only stored as hashed values, never plaintext
    - input sanitation to guard against SQL injection attacks

- Persistent Database
    - user data
        - capmaign affiliation
        - login data
    - campaign data
        - party affiliation
        - people
        - places
        - items
        - quests
    - site feedback
        - custom error logging

## Technologies Used
- Web stack
    - Python
    - Flask
    - WSGI via Gunicorn

- Database
    - Sqlite3 (local development)
    - Postgres (cloud based via Heroku)

---

# TODOs

## In Development
- convert welcome.html to bs4
- delete archived html files
- delete `application.py` print debugger statements
- cange error handling to funtion rather than direct error page render (diagnostic logging)
```
def error(errcode, errmsg, user):
    try: log error in db/errors or db/activity
finally:
    render_template("error.html", errcode=errcode, errmsg=errmsg)
```
- translate place names to place ids in all handling
- hotlink whole homepage
- filter homepage by current location by...?

## Upcoming & Feature Requests
- add "notes" appendations to exisiting "description"
    - separate table: note_id | note | player_id | campaign_id
- Bonds and Grudges
- Dice roller
- Import bulk data into campaign
    - seed new campaign with CSV data (alternately, expand new campaign creation pages)
    - external "chat logs"

## Someday Maybe
- messenger
- Live timeline of events
    - timeline search
- Virtual Tabletop environment integration

## Bugs