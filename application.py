import os
import random
import sqlalchemy

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

## Old version
# Configure local sqlite database
# db = SQL("sqlite:///canon.db")

# Configure Heroku Postgres database
db = SQL(os.getenv('DATABASE_URL'))

# Use local Postgres DB
# https://devcenter.heroku.com/articles/heroku-postgresql#local-setup
# import os
# import psycopg2
# DATABASE_URL = os.environ['DATABASE_URL']
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

""" Type Conversions """
def nonone(s):
    if s is None:
        return ''
    else:
        return str(s)


""" Misc Helper Functions """
def loginuser():
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                        username=request.form.get("username"))

    # Ensure username exists
    if len(rows) != 1:
        return render_template("register.html", errmsg="Username not found.")

    # Ensure username exists and password is correct
    if not check_password_hash(rows[0]["hash"], request.form.get("password")):
        return render_template("error.html", errcode=403, errmsg="Incorrect password.")

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # Store login timestamp
    db.execute("INSERT INTO activity (user_id, action) VALUES (:user_id, :action)", user_id=session["user_id"], action="login")



""" Database Helper Functions """
def get_ac_id():
    # Query for active campaign
    tmp = db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])
    return tmp[0]['activecampaign_id']

def get_people(ac_id):
    # Select all characters in active campaign
    return db.execute("SELECT * FROM characters WHERE campaign_id=:ac_id", ac_id=ac_id)

def get_places(ac_id):
    # Select all places in active campaign
    return db.execute("SELECT * FROM places WHERE campaign_id=:ac_id", ac_id=ac_id)

def get_items(ac_id):
    # Select all items in active campaign
    return db.execute("SELECT * FROM items WHERE campaign_id=:ac_id", ac_id=ac_id)

def get_quests(ac_id):
    # Select all quests in active campaign
    return db.execute("SELECT * FROM quests WHERE campaign_id=:ac_id", ac_id=ac_id)



""" MAIN PAGES """
""" Campaign Functions """
@app.route("/")
@login_required
def index():

    # Identify user data
    user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])

    # Get active campaign name
    campaign = db.execute("SELECT * FROM campaigns WHERE campaign_id=:active",
                                active=user[0]['activecampaign_id'])

    # Redirect to campaign choices if none is active
    if not campaign:
        return redirect("/campaigns")

    else:

        # Request current campaign's data
        ac_id = get_ac_id()
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        quests = get_quests(ac_id)

        # Select all players in active campaign for display
        players = db.execute("SELECT * FROM users WHERE id IN (SELECT user_id FROM parties WHERE campaign_id=:ac_id)",
                            ac_id=ac_id)

        # Render campaign summary page
        return render_template("index.html", campaign=campaign, people=people, places=places, items=items, quests=quests, players=players)


# TODO change location in db to place_name or place_id; better yet, have function to convert between them
@app.route("/people", methods=["GET", "POST"])
@login_required
def people():

    # Query for active campaign
    ac_id = get_ac_id()

    if request.method == 'GET':

        # Request current campaign's data
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        quests = get_quests(ac_id)

        # Render people page
        return render_template("people.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        name = name.strip()
        place = request.form.get("place")
        description = request.form.get("description")

        # Insert given data
        db.execute("INSERT INTO characters (campaign_id, name, location, description) \
                    VALUES (:ac_id, :name, :location, :description)",
                    ac_id=ac_id, name=name, location=place, description=description)

        return redirect("/people")


@app.route("/places", methods=["GET", "POST"])
@login_required
def places():

    # Identify active campaign
    ac_id = get_ac_id()

    if request.method == 'GET':

        # Request current campaign's data
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        quests = get_quests(ac_id)

        # Render places page
        return render_template("places.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        name = name.strip()
        description = request.form.get("description")
        description = description.strip()

        # Insert given data
        db.execute("INSERT INTO places (name, campaign_id, description) VALUES (:name, :ac_id, :description)",
                    name=name, ac_id=ac_id, description=description)

        return redirect("/places")


@app.route("/items", methods=["GET", "POST"])
@login_required
def items():

    # Identify active campaign
    ac_id = get_ac_id()
    
    if request.method == 'GET':

        # Request current campaign's data
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        quests = get_quests(ac_id)

        # Render people page
        return render_template("items.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses, sanitize leading and trailing spaces
        name = request.form.get("name")
        name = name.strip()
        place = request.form.get("place")
        description = request.form.get("description")
        description = description.strip()

        # Insert given data
        db.execute("INSERT INTO items (name, campaign_id, description, place_name) \
                    VALUES (:name, :ac_id, :description, :place_name)",
                    name=name, ac_id=ac_id, description=description, place_name=place)

        return redirect("/items")


@app.route("/quests", methods=["GET", "POST"])
@login_required
def quests():

    # Identify active campaign
    ac_id = get_ac_id()

    if request.method == 'GET':

        # Request current campaign's data
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        quests = get_quests(ac_id)

        # Render people page
        return render_template("quests.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        name = name.strip()
        place_name = request.form.get("place")
        description = request.form.get("description")

        # Insert given data
        db.execute("INSERT INTO quests (name, campaign_id, place_name, description) VALUES (:name, :ac_id, :place_name, :description)",
                    name=name, ac_id=ac_id, place_name=place_name, description=description)

        return redirect("/quests")



""" More Detail and Deletion """
# When top level items are clicked
@app.route("/more/<kind>/<selection>/", methods=["POST", "GET"])
@login_required
def more(kind, selection):

    # Get current campaign id
    ac_id = get_ac_id()

    # Display details for the chosen selection
    if request.method == 'GET':
        print(f"GET GET GET GET GET GET GET GET GET GET GET GET ")

        # Request current campaign's data
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)
        
        print(f"kind:{kind}")
        print(f"selection:{selection}")

        if kind == "place":
            data = db.execute("SELECT * FROM places WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            print(data)
            return render_template("more.html", kind=kind, selection=selection, people=people, places=places, items=items, place=data)

        if kind == "person":
            data = db.execute("SELECT * FROM characters WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            print(data)
            return render_template("more.html", kind=kind, selection=selection, people=people, places=places, items=items, person=data)

        if kind == "item":
            data = db.execute("SELECT * FROM items WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            print(data)
            return render_template("more.html", kind=kind, selection=selection, people=people, places=places, items=items, item=data)

        if kind == "quest":
            data = db.execute("SELECT * FROM quests WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            print(data)
            return render_template("more.html", kind=kind, selection=selection, people=people, places=places, items=items, quest=data)
    
    # Update selection on POST
    else:
        if kind == "place":
            description = nonone(request.form.get("description"))
            
            # Ensure permissions, reject if thing not in requestor's active campaign
            place_campaign_id = db.execute("SELECT place_id, campaign_id FROM places WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            pc_id = place_campaign_id[0]['campaign_id']
            place_id = place_campaign_id[0]['place_id']
            if ac_id != pc_id:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect updates
            else:
                if description:
                    db.execute("UPDATE places SET description=:description WHERE place_id=:place_id", description=description, place_id=place_id)
            return redirect("/places")

        if kind == "person":
            name = nonone(request.form.get("name"))
            place = nonone(request.form.get("place"))
            description = nonone(request.form.get("description"))

            # Ensure permissions, reject if thing not in requestor's active campaign
            character_campaign_id = db.execute("SELECT character_id, campaign_id FROM characters WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            cc_id = character_campaign_id[0]['campaign_id']
            character_id = character_campaign_id[0]['character_id']
            if ac_id != cc_id:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect updates
            else:
                if name:
                    db.execute("UPDATE characters SET name=:name WHERE character_id=:character_id", name=name, character_id=character_id)
                if place:
                    db.execute("UPDATE characters SET location=:place WHERE character_id=:character_id", place=place, character_id=character_id)
                if description:
                    db.execute("UPDATE characters SET description=:description WHERE character_id=:character_id", description=description, character_id=character_id)
            return redirect("/people")

        if kind == "item":
            name = nonone(request.form.get("name"))
            place = nonone(request.form.get("place"))
            description = nonone(request.form.get("description"))

            # Ensure permissions, reject if thing not in requestor's active campaign
            item_campaign_id = db.execute("SELECT item_id, campaign_id FROM items WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            ic_id = item_campaign_id[0]['campaign_id']
            item_id = item_campaign_id[0]['item_id']
            if ac_id != ic_id:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect updates
            else:
                if name:
                    db.execute("UPDATE items SET name=:name WHERE item_id=:item_id", name=name, item_id=item_id)
                if place:
                    db.execute("UPDATE items SET place_name=:place WHERE item_id=:item_id", place=place, item_id=item_id)
                if description:
                    db.execute("UPDATE items SET description=:description WHERE item_id=:item_id", description=description, item_id=item_id)
            return redirect("/items")

        if kind == "quest":
            name = nonone(request.form.get("name"))
            place = nonone(request.form.get("place"))
            description = nonone(request.form.get("description"))

            # Ensure permissions, reject if thing not in requestor's active campaign
            quest_campaign_id = db.execute("SELECT quest_id, campaign_id FROM quests WHERE name=:selection AND campaign_id=:ac_id", selection=selection, ac_id=ac_id)
            qc_id = quest_campaign_id[0]['campaign_id']
            quest_id = quest_campaign_id[0]['quest_id']
            if ac_id != qc_id:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect updates
            else:
                if name:
                    db.execute("UPDATE quests SET name=:name WHERE quest_id=:quest_id", name=name, quest_id=quest_id)
                if place:
                    db.execute("UPDATE quests SET place_name=:place WHERE quest_id=:quest_id", place=place, quest_id=quest_id)
                if description:
                    db.execute("UPDATE quests SET description=:description WHERE quest_id=:quest_id", description=description, quest_id=quest_id)
            return redirect("/quests")

        else:
            return render_template("error.html", errcode=400, errmsg="A unexpected request was made.")


@app.route("/delete/<kind>/<selection>/", methods=["POST"])
@login_required
def delete(kind, selection):

    if request.method == 'POST':

        # Request current campaign's data
        ac_id = get_ac_id()
        people = get_people(ac_id)
        places = get_places(ac_id)
        items = get_items(ac_id)

        # PEOPLE
        if kind == "person":

            # Ensure permissions
            character_campaign_id = db.execute("SELECT campaign_id FROM characters WHERE name=:selection", selection=selection)
            ccid = character_campaign_id[0]['campaign_id']
            if ac_id != ccid:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect deletion
            else:
                db.execute("DELETE FROM characters WHERE name=:selection AND campaign_id=:character_campaign_id", selection=selection, character_campaign_id=ccid)
                return redirect("/people")    

        # PLACES
        if kind == "place":

            # Ensure permissions
            place_campaign_id = db.execute("SELECT campaign_id FROM places WHERE name=:selection", selection=selection)
            pcid = place_campaign_id[0]['campaign_id']
            if ac_id != pcid:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect deletion
            else:
                db.execute("DELETE FROM places WHERE name=:selection AND campaign_id=:place_campaign_id", selection=selection, place_campaign_id=pcid)
                return redirect("/places")    


        # ITEMS
        if kind == "item":

            # Ensure permissions
            item_campaign_id = db.execute("SELECT campaign_id FROM items WHERE name=:selection", selection=selection)
            icid = item_campaign_id[0]['campaign_id']
            if ac_id != icid:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect deletion
            else:
                db.execute("DELETE FROM items WHERE name=:selection AND campaign_id=:item_campaign_id", selection=selection, item_campaign_id=icid)
                return redirect("/items")    

        # QUEST
        if kind == "quest":

            # Ensure permissions
            quest_campaign_id = db.execute("SELECT campaign_id FROM quests WHERE name=:selection", selection=selection)
            qcid = quest_campaign_id[0]['campaign_id']
            if ac_id != qcid:
                return render_template("error.html", errcode=403, errmsg="Users may only edit entries from their current campaign")

            # Effect deletion
            else:
                db.execute("DELETE FROM quests WHERE name=:selection AND campaign_id=:quest_campaign_id", selection=selection, quest_campaign_id=qcid)
                return redirect("/quests")

    else:
        return render_template("error.html", errcode=405, errmsg="Method not allowed.")



""" ADMIN PAGES """
""" Login & Campaigns """
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Serve registration page
    if request.method == 'GET':
        return render_template("register.html")

    # Process submitted form responses on POST
    else:

        # Error Checking
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", errcode=403, errmsg="Username required.")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html", errcode=403, errmsg="Password required.")

        # Ensure password and password confirmation match
        if request.form.get("password") != request.form.get("passwordconfirm"):
            return render_template("error.html", errcode=403, errmsg="Passwords must match.")

        # Ensure minimum password length
        if len(request.form.get("password")) < 8:
            return render_template("error.html", errcode=403, errmsg="Password must be at least 8 characters.")

        # Store the hashed username and password
        username = request.form.get("username")
        hashedpass = generate_password_hash(request.form.get("password"))

        # Check if username is already taken
        if not db.execute("SELECT username FROM users WHERE username LIKE (?)", username):

            # Add the username and login user
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashedpass)",
                        username=username, hashedpass=hashedpass)
            loginuser()
            allcampaigns=db.execute("SELECT name FROM campaigns")
            return render_template('welcome.html', allcampaigns=allcampaigns)

        else:
            return render_template("error.html", errcode=403, errmsg="Username invalid or already taken.")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", errcode=400, errmsg="Username required.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", errcode=400, errmsg="Password required.")

        # Login user
        loginuser()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Store logout timestamp
    db.execute("INSERT INTO activity (user_id, action) VALUES (:user_id, :action)", user_id=session["user_id"], action="logout")

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/campaigns", methods=["GET", "POST"])
@login_required
def campaigns():

    # Serve data relating to active campaign
    if request.method == 'GET':

        # Query for user's current active campaign id
        users = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Current Campaign name
        active = db.execute("SELECT name FROM campaigns WHERE campaign_id=:activecampaign_id",
                            activecampaign_id=users[0]['activecampaign_id'])

        ac_id=get_ac_id()

        # Query for all joined campaigns, for "Change Active Campaign" selector
        campaigns = db.execute("SELECT name FROM campaigns WHERE campaign_id IN (SELECT campaign_id FROM parties WHERE user_id=:user_id)", \
                                user_id=session["user_id"])

        # Select all player names in active campaign
        players = db.execute("SELECT username FROM users WHERE id IN (SELECT user_id FROM parties WHERE campaign_id=:ac_id)",
                            ac_id=ac_id)

        # TODO change so that not all campaigns are always visible
        # TODO require typing campaign name in form, or using campaign_id number
        # Select every possible campaign to join
        allcampaigns = db.execute("SELECT name FROM campaigns;")

        # If user has no active campaign, redirect to welcome
        if not active:
            allcampaigns=db.execute("SELECT name FROM campaigns")
            return render_template('welcome.html', allcampaigns=allcampaigns, users=users)

        # Go to campaign selection screen
        else:
            print(players)
            return render_template("campaigns.html", active=active, campaigns=campaigns, players=players, allcampaigns=allcampaigns, )

    else:
        # Capture posted values; if "None" convert to ''; else pass as str(value)
        changecampaign = nonone(request.form.get("change_campaign"))
        joincampaign = nonone(request.form.get("join_campaign"))
        codeword_given = nonone(request.form.get("codeword"))

        # Query for chosen campaign's data
        campaigns = db.execute("SELECT * FROM campaigns WHERE name=:joincampaign",joincampaign=joincampaign)

        # Check for change_campaign submission; if none, proceed to check for join_campaign
        if not changecampaign:
            print(f"no changecampaign")

            # Check for join_campaign submission; if none redirect back to campaigns
            if not joincampaign:
                print(f"no joincampaign")

                # Redirect back to "/campaigns" when no data submitted
                return redirect("/campaigns")

            # Join request exists; proceed to verify, then implement join
            else:
                print(f"joincampaign found")
                # Verify codeword
                # If password is incorrect
                codeword_actual = campaigns[0]['codeword']
                if codeword_given != codeword_actual:
                    return render_template("error.html", errcode=403, errmsg="Codeword incorrect.")

                # On success, join them to the campaign
                else:
                    # Add to campaign (update parties to include association)
                    db.execute("INSERT INTO parties (campaign_id, user_id) VALUES (:campaign_id, :user_id)", campaign_id=campaigns[0]['campaign_id'], user_id=session["user_id"])

                    # Set that campaign as active (update users to indicate active campaign)
                    db.execute("UPDATE users SET activecampaign_id=:newactive WHERE id=:user_id", newactive=campaigns[0]['campaign_id'], user_id=session["user_id"])
                    return redirect("/")

        # Change request exists; proceed to verify, then implement change
        else:
            # Fetch campaign ID from campaign name
            newactiveid = db.execute("SELECT campaign_id FROM campaigns WHERE name=:newactive", newactive=changecampaign)
            print(f"changing to campaign {newactiveid}")

            # Update user's new active campaign ID
            db.execute("UPDATE users SET activecampaign_id=:newactiveid WHERE id=:user_id", newactiveid=newactiveid[0]['campaign_id'], user_id=session["user_id"])

            return redirect("/")


@app.route("/newcampaign", methods=["GET", "POST"])
@login_required
def newcampaign():
    if request.method == 'GET':
        return render_template("newcampaign.html")

    # Process submission on 'POST'
    else:
        name=request.form.get("name")
        name=name.strip()
        codeword=request.form.get("codeword")

        # Add campaign to database
        db.execute("INSERT INTO campaigns (name, codeword) VALUES (:name, :codeword)",
                    name=name, codeword=codeword)

        # Obtain new campaign's id
        campaign_id=db.execute("SELECT campaign_id FROM campaigns WHERE name=:name", name=name)
        campaign_id=campaign_id[0]['campaign_id']

        # Have user joined into campaign
        db.execute("INSERT INTO parties (campaign_id, user_id) VALUES (:campaign_id, :user_id)",
                    campaign_id=campaign_id, user_id=session["user_id"])

        # Set that campaign as current active for that user
        db.execute("UPDATE users SET activecampaign_id=:campaign_id WHERE id=:user_id",
                    campaign_id=campaign_id, user_id=session["user_id"])

        # TODO have a first campaign new message how to flash here
        return redirect("/")



""" Miscellaneous """
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == 'GET':
        return render_template("feedback.html")

    # When feedback is submitted on 'POST'
    else:
        feedback = request.form.get("feedback")

        # TODO capture user name when feedback is given from logged in users
        # Not logged in
        db.execute("INSERT INTO feedback (note) VALUES (:feedback)",
                    feedback=feedback)
        return render_template("thankyou.html")


@app.route("/help", methods=["GET"])
def help():
    if request.method == 'GET':
        return render_template("help.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/roll", methods=["GET", "POST"])
def roll():

    # Display dice roll page on GET
    if request.method == 'GET':
        return render_template("roll.html")

    if request.method == 'POST':
        qty = request.form.get("qty")
        die = request.form.get("die")
        mod = request.form.get("mod")

    # Set qty to 1 if none given, else make int
    if not qty:
        qty = 1
    else:
        qty = int(qty)

    # Set mod to 0 if none given, else make int
    if not mod:
        mod = 0
    else:
        mod = int(mod)

    # Initalize list for all rolls and totals including mods

    rolls = []
    totals = []
    # Loop once for each die roll
    for i in range(qty):
        print(rolls)
        print(totals)
        # Append roll result to list
        rolls.append(random.randint(1, die))

        # Add modifier, append to totals list
        total = rolls[i] + mod
        totals.append(total)

        # Testing, print results
        print(f"Roll {i}: {rolls[i]} + {mod} = {rolls[i] + mod}")

    return render_template("roll.html", rolls=rolls, totals=totals, mod=mod)



""" Error handling """
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()

    # # Set error variables and store in db
    # errcode=e.code
    # errmsg=e.name

    # # Log some errors in db
    # userwerr=db.execute("SELECT username FROM users where id=:user_id", user_id=session['user_id'])
    # db.execute("INSERT INTO errors (code, message, userwerr) \
    #                         VALUES (:errcode, :errmsg, :userwerr)", \
    #                         errcode=errcode, errmsg=errmsg, userwerr=userwerr[0]['username'])

    # return render_template("error.html", errcode=errcode, errmsg=errmsg)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)