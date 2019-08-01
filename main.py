"""
###########################
# ---- Helpful Links ---- #
###########################

1. SQL Alchemy          https://flask-sqlalchemy.palletsprojects.com/en/2.x/
2. Exploring Flask      http://exploreflask.com/en/latest/index.html
3. HTML Guides          https://www.w3schools.com/html/
"""


#####################
# ---- Imports ---- #
#####################


from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from os import urandom
from functions import *


###########################################
# ---- App and Database configuration ---- #
###########################################


app = Flask(__name__)
app.config["DEBUG"] = True

# - The connection string on the following line will need to be configured to work with the Database. - #
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://____:____@localhost:8889/____"

app.config["SQLALCHEMY_ECHO"] = True
app.secret_key = urandom(16)
db = SQLAlchemy(app)


####################
# ---- Models ---- #
####################


class ClassName_Many(db.Model):

    # -- Table Columns -- #

    # - Primary Key - #
    id = db.Column(db.Integer, primary_key=True)

    # - Other Columns - #
    attribute_one = db.Column(db.String(120), nullable=False)
    attribute_two = db.Column(db.Text, nullable=False)

    # - One-to-Many Connector Attribute - #
    other_class = db.relationship("ClassName_One", backref="this-class", lazy=True)

    def __init__(self, attribute_one, attribute_two):
        
        self.attribute_one = attribute_one
        self.attribute_two = attribute_two

class ClassName_One(db.Model):

    # -- Table Columns -- #

    # - Primary Key - #
    id = db.Column(db.Integer, primary_key=True)

    # - Other Columns - #
    attribute_one = db.Column(db.String(120), nullable=False)
    attribute_two = db.Column(db.Text, nullable=False)

    # - One-to-Many Connector Attribute - #
    other_class_id = db.Column(db.Integer, db.ForeignKey("class-name.id"), nullable=False)


############################
# ---- Route Handlers ---- #
############################


# -- Rerouting Controller -- #
@app.before_request
def require_login():

    # - The allowed routes are routes that can be viewed when not logged in. - #
    allowed_routes = ["login", "signup", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

# -- Index Controller -- #
@app.route("/")
def index():
    return render_template(
        "index.html",
        title="homepage_title"
        )

# -- Login Controller -- #
@app.route("/login", methods=["GET", "POST"])
def login():

    # - This block is for GET requests, when the login page is loaded normally. - #
    if request.method == "GET":

        # - Just render the template normally. - #
        return render_template(
            "login.html",
            title = "Log In"
        )

    # - This block is for POST requests, when the 'Log In' button is clicked. - #
    elif request.method == "POST":

        # - First, pull the username and password from the form and place them into variables. - #
        username = request.form["username"]
        password = request.form["password"]

        # - If either of those fields is left blank, - #
        if not (username and password):
            username_error = ""
            password_error = ""
            if not username:
                username_error = "Enter a username."
            if not password:
                password_error = "Enter a password."

            # - Rerender the template, having added the appropriate error messages. - #
            return render_template(
                "login.html",
                title = "Log In",
                username = username,
                username_error = username_error,
                password_error = password_error
            )

        # - Obtain the User data from the database and place it in a variable. - #
        user = ClassName_One.query.filter_by(username = username).first()

        # - If the given username is not in the database, - #
        if not user:

            # - Rerender the login template, and display a username error. - #
            return render_template(
                "login.html",
                title = "Log In",
                username_error = "Impossible. Perhaps the archives are incomplete."
            )

        # - If the password given does not match the password for that username, - #
        if user.password != password:

            # - Rerender the login template, display a password error, and retain the username. - #
            return render_template(
                "login.html",
                title = "Log In",
                password_error = "That's the wrong password.",
                username = username
            )

        # - If the username and password data match, begin a session with that user! - #
        session["username"] = username

        # - Once the session is active, redirect to the /newpost handler. - #
        return redirect(
            "/newpost"
        )

# -- Account Creation Controller -- #
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # - This block is for POST requests, when the 'Sign Up' button is clicked. - #
    if request.method == "POST":

        # - First, pull the username, password, and password confirmation from the form and place them into variables. - #
        username = request.form["username"]
        password = request.form["password"]
        passconfirm = request.form["pass_confirm"]

        # - Then instantiate a dictionary that will hold error messages. - #
        errors = {
            "username": "",
            "password": "",
            "pass_confirm": "",
        }

        # - Then, use validation functions to determine the given data's validity. - #
        signup_dict = validate_signup(
            username,
            password,
            passconfirm
            )

        # - If any entries failed validation, adjust the error message value accordingly. - #
        if not signup_dict["valid_username"]:
            errors["username"] = "Please enter a valid username, between 3 and 20 characters, with no spaces."
        if not signup_dict["valid_password"]:
            errors["password"] = "Don't forget your password!"
        if not signup_dict["passwords_match"]:
            errors["pass_confirm"] = "Make sure your passwords match."

        # - If no errors were generated, - #
        if list(errors.values()) == ["", "", ""]:

            # - and if the given username doesn't already exist, - #
            existing_user = ClassName_One.query.filter_by(username = username).first()
            if not existing_user:

                # - create a new user, add that user to a new session, and redirect to the /newpost handler. Congrats! - #
                new_user = ClassName_One(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                return redirect(
                    "/newpost"
                )

            # - If the given username already exists, start the process over and display the appropriate error. - #
            else:
                return render_template(
                    "signup.html",
                    title = "Create An Account",
                    username_error = "User with this username already exists."
                )

        # - If any errors were generated, - #
        else:

            # - rerender the template and display the appropriate errors. - #
            return render_template(
                "signup.html",
                title = "Create An Account",
                username_error = errors["username"],
                password_error = errors["password"],
                passconfirm_error = errors["pass_confirm"],
                username = username
            )

    # - This block is for GET requests, when the login page is loaded normally. - #
    elif request.method == "GET":
        return render_template(
            "signup.html",
            title = "Create An Account"
        )

# -- Logout Controller -- #
@app.route("/logout")
def logout():

    # - Remove the username from the session, and redirect to the home page. - #
    del session["username"]
    return redirect("/")


if __name__ == "__main__":
    app.run()