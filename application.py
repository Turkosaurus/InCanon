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


# https://devcenter.heroku.com/articles/heroku-postgresql#local-setup
# import os
# import psycopg2

# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')



""" Database Helper Functions """
def get_ac_id():
    # Query for active campaign
    return db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])

def get_people():
    # Get active campaign's ID
    ac_id = get_ac_id()
    # Select all characters in active campaign
    return db.execute("SELECT * FROM characters WHERE campaign_id=:ac_id", ac_id=ac_id[0]['activecampaign_id'])

def get_places():
    # Get active campaign's ID
    ac_id = get_ac_id()
    # Select all places in active campaign
    return db.execute("SELECT * FROM places WHERE campaign_id=:ac_id", ac_id=ac_id[0]['activecampaign_id'])

def get_items():
    # Get active campaign's ID
    ac_id = get_ac_id()
    # Select all items in active campaign
    return db.execute("SELECT * FROM items WHERE campaign_id=:ac_id", ac_id=ac_id[0]['activecampaign_id'])

def get_quests():
    # Get active campaign's ID
    ac_id = get_ac_id()
    # Select all quests in active campaign
    return db.execute("SELECT * FROM quests WHERE campaign_id=:ac_id", ac_id=ac_id[0]['activecampaign_id'])



""" MAIN PAGES """
""" Campaign Functions """
@app.route("/")
@login_required
def index():

    # Identify user data
    user = db.execute("SELECT * FROM users WHERE id=:user_id", user_id=session["user_id"])

    # TODO replace with get_campaign()?
    # Get active campaign name
    campaign = db.execute("SELECT * FROM campaigns WHERE campaign_id=:active",
                                active=user[0]['activecampaign_id'])

    # Redirect to campaign choices if none is active
    if not campaign:
        return redirect("/campaigns")

    else:

        # Request current campaign's data
        ac_id = get_ac_id()
        people = get_people()
        places = get_places()
        items = get_items()
        quests = get_quests()

        # Select all players in active campaign for display
        players = db.execute("SELECT * FROM users WHERE id IN (SELECT user_id FROM parties WHERE campaign_id=:ac_id)",
                            ac_id=ac_id[0]['activecampaign_id'])

        # Render campaign summary page
        return render_template("index.html", campaign=campaign, people=people, places=places, items=items, quests=quests, players=players)


@app.route("/people", methods=["GET", "POST"])
@login_required
def people():
    if request.method == 'GET':

        # Request current campaign's data
        people = get_people()
        places = get_places()
        items = get_items()
        quests = get_quests()

        # Render people page
        return render_template("people.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        place = request.form.get("place")
        description = request.form.get("description")

        # Query for active campaign
        ac_id = db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Insert given data
        db.execute("INSERT INTO characters (campaign_id, name, location, description) \
                    VALUES (:ac_id, :name, :location, :description)",
                    ac_id=ac_id[0]['activecampaign_id'], name=name, location=place, description=description)

        return redirect("/people")


@app.route("/places", methods=["GET", "POST"])
@login_required
def places():
    if request.method == 'GET':

        # Request current campaign's data
        people = get_people()
        places = get_places()
        items = get_items()
        quests = get_quests()

        # Render people page
        return render_template("places.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        description = request.form.get("description")

        # Query for active campaign
        ac_id = db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Insert given data
        db.execute("INSERT INTO places (name, campaign_id, description) VALUES (:name, :ac_id, :description)",
                    name=name, ac_id=ac_id[0]['activecampaign_id'], description=description)

        return redirect("/places")


#TODO improve location handling
@app.route("/items", methods=["GET", "POST"])
@login_required
def items():
    if request.method == 'GET':

        # Request current campaign's data
        people = get_people()
        places = get_places()
        items = get_items()
        quests = get_quests()

        # Render people page
        return render_template("items.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        place = request.form.get("place")
        description = request.form.get("description")

        # Query for active campaign
        ac_id = db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Insert given data
        # todo rename location to acknowledge foreign key relationship
        db.execute("INSERT INTO items (name, campaign_id, description) \
                    VALUES (:name, :ac_id, :description)",
                    name=name, ac_id=ac_id[0]['activecampaign_id'], description=description)

        return redirect("/items")


#TODO correct place_id and location name errors
@app.route("/quests", methods=["GET", "POST"])
@login_required
def quests():
    if request.method == 'GET':

        # Request current campaign's data
        people = get_people()
        places = get_places()
        items = get_items()
        quests = get_quests()

        print(session)

        # Render people page
        return render_template("quests.html", people=people, places=places, items=items, quests=quests)

    # Process posted content
    else:

        # Capture submitted responses
        name = request.form.get("name")
        place = request.form.get("place")
        description = request.form.get("description")

        # Query for active campaign
        ac_id = db.execute("SELECT activecampaign_id FROM users WHERE id=:user_id", user_id=session["user_id"])

        # Insert given data
        db.execute("INSERT INTO quests (name, campaign_id, place_id, description) VALUES (:name, :ac_id, :place_id, :description)",
                    name=name, ac_id=ac_id[0]['activecampaign_id'], place_id=place, description=description)

        return redirect("/quests")



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

            # Add the username
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashedpass)",
                        username=username, hashedpass=hashedpass)
            return redirect("/")

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

        # Query for all joined campaigns, for "Change Active Campaign" selector
        campaigns = db.execute("SELECT name FROM campaigns WHERE campaign_id IN (SELECT campaign_id FROM parties WHERE user_id=:user_id)", \
                                user_id=session["user_id"])

        # # Testing
        # print(f"users: {users}")
        # print(f"active: {active}")
        # print(f"campaigns: {campaigns}")
        # print(active)

        # If user has no active campaign
        if not active:
            return render_template("welcome.html", users=users)

        else:
            return render_template("campaigns.html", campaigns=campaigns, active=active)

    else:
        # Requested campaign change
        newactive = request.form.get("change_campaign")

        newactiveid = db.execute("SELECT campaign_id FROM campaigns WHERE name=:newactive", newactive=newactive)

        # Update user's new active campaign
        db.execute("UPDATE users SET activecampaign_id=:newactiveid WHERE id=:user_id", newactiveid=newactiveid[0]['campaign_id'], user_id=session["user_id"])

        # Select that new active campaign
        active = db.execute("SELECT name FROM campaigns WHERE campaign_id = (SELECT activecampaign_id FROM users WHERE id=:user_id)", user_id=session["user_id"])
        print("active:")
        print(active)

        campaigns = db.execute("SELECT name FROM campaigns WHERE campaign_id = \
                                (SELECT campaign_id FROM parties WHERE user_id = :user_id)", \
                                user_id=session["user_id"])
        return redirect("/")


@app.route("/newcampaign", methods=["GET", "POST"])
@login_required
def newcampaign():
    if request.method == 'GET':
        return render_template("newcampaign.html")

    # Process submission on 'GET'
    else:
        name=request.form.get("name")
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

        return redirect("/")


@app.route("/joincampaign", methods=["GET", "POST"])
@login_required
def joincampaign():

    # Allow users to submit choice to join all active campaigns
    if request.method == 'GET':
        # TODO, prevent multiple signups by only selecing campaigns someone is not in
        campaigns = db.execute("SELECT name FROM campaigns;")
        print(campaigns)
        return render_template("joincampaign.html", campaigns=campaigns)

    #
    else:
        # Store submitted data
        joincampaign = request.form.get("joincampaign")
        codeword_given = request.form.get("codeword")

        # Query database for required information
        campaigns = db.execute("SELECT * FROM campaigns WHERE name=:joincampaign",joincampaign=joincampaign)
        print(campaigns)

        # If no campaign choice is made
        if not joincampaign:
            return render_template("error.html", errcode=400, errmsg="Campaign choice required.")

        # If password is incorrect
        codeword_actual = campaigns[0]['codeword']
        if codeword_given != codeword_actual:
            return render_template("error.html", errcode=403, errmsg="Codeword incorrect.")

        # On success, add them to the campaign
        else:
            # Update parties to include association
            db.execute("INSERT INTO parties (campaign_id, user_id) VALUES (:campaign_id, :user_id)", campaign_id=campaigns[0]['campaign_id'], user_id=session["user_id"])

            # Update users to indicate active campaign
            db.execute("UPDATE users SET activecampaign_id=:newactive WHERE id=:user_id", newactive=campaigns[0]['campaign_id'], user_id=session["user_id"])
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
    return render_template("error.html", errmsg=e.name, errcode=e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)