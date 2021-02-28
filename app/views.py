from datetime import datetime

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from . import app


db = SQLAlchemy(app)



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #TODO login logic. 
        email = request.form["email"]
        password = request.form["password"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
#@login_required
def logout():
    #logout_user()
    return redirect("/login")


@app.route("/poses/")
def poses():
    return render_template("poses.html")

@app.route("/addprompt/", methods=["GET", "POST"])
def addprompt():
    if request.method == "POST":
        flash(f'Prompt added!')
        return render_template("addprompt.html")
    else:
        return render_template("addprompt.html")

@app.route("/prompts/", methods=["GET", "POST"])
def prompts():

    randomPrompt = "This is a prompt"
    category = "Weddings"

    if request.method == "POST":
        if request.form.get("randomQuote"):
            #flash(f'This was from a button press')
            return render_template("prompts.html", prompt = randomPrompt, category = category)
    else:
        #flash(f'This is from a regular press')
        return render_template("prompts.html", prompt = randomPrompt, category = category)

@app.route("/addsession/", methods=["GET", "POST"])
def addsession():
    if request.method == "POST":
        flash(f'Session saved!')
        return render_template("addsession.html")
    else:
        return render_template("addsession.html")

@app.route("/sessions/")
def sessions():
    return render_template("sessions.html")

@app.route("/weather/")
def weather():
    return render_template("weather.html")




# @app.route("/api/data")
# def get_data():
#     return app.send_static_file("data.json")
