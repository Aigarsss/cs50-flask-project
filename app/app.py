from flask import Flask, render_template, request, redirect, flash
# secret_key
import secrets

#db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, desc, asc
from sqlalchemy.sql.expression import func
from datetime import date

#hashing
from werkzeug.security import generate_password_hash, check_password_hash

#user logins
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# for sunset/sunrise time requests
import json 
import urllib.request
import requests

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)


ENV = 'dev'
    
if ENV == 'dev':
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/flaskphoto'
else:
    app.config['DEBUG'] = False
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/flaskphoto'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(80))


    def __init__(self, email, password):
        self.email = email
        self.password = password

    # def __repr__(self):
    #     return '<User %r>' % self.email

class Prompt(db.Model):

    __tablename__ = 'prompts'

    id = db.Column(db.Integer, primary_key = True)
    prompt = db.Column(db.String(500))
    category = db.Column(db.String(20))
    userid = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, prompt, category, userid):
        self.prompt = prompt
        self.category = category
        self.userid = userid

class Session(db.Model):

    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    phone = db.Column(db.String(30))
    category = db.Column(db.String(20))
    date = db.Column(db.Date())
    location = db.Column(db.String(30))
    email = db.Column(db.String(120))
    comment = db.Column(db.String(500))
    userid = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self, name, phone, category, date, location, email, comment, userid):
        self.name = name
        self.phone = phone
        self.category = category
        self.date = date
        self.location = location
        self.email = email
        self.comment = comment
        self.userid = userid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from datetime import datetime

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    #https://www.youtube.com/watch?v=8aTnmsDMldY&ab_channel=PrettyPrinted
    if request.method == "POST":

        email = request.form['email']
        password = request.form['password'] 
        passwordHashed = generate_password_hash(password, method='sha256') 
        passwordrepeat = request.form['passwordrepeat'] 

        if password != passwordrepeat:
            flash(f'Fields need to be the same!')
            return render_template("register.html")

        if db.session.query(User).filter(User.email == email).count() == 0:
            data = User(email, passwordHashed)
            db.session.add(data)
            db.session.commit()
            flash(f'Registration succesfull!')
            return redirect("/")
        flash(f'email already exists. Log in')
        return render_template("register.html")

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.getlist("remember") 

        if len(remember) == 1:
            rememberStatus = True
        else:
            rememberStatus = False

        user = db.session.query(User).filter(User.email == email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember = rememberStatus)
                flash(f'Welcome back {email}, remember set to {rememberStatus}!')
                return redirect("/")
            else:
                flash(f'Wrong password!')
                return render_template("login.html")
        flash(f'User doesnt exist!')       
        return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "POST":
        password = request.form["password"]
        passwordHashed = generate_password_hash(password, method='sha256')
        userid = current_user.id

        currentUser = User.query.filter_by(id=userid).first()
        currentUser.password = passwordHashed
        db.session.commit()

        flash(f'Password updated!')       
        return redirect("/")
    else:
        return render_template("changepassword.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route("/poses/")
@login_required
def poses():
    

    return render_template("poses.html")

@app.route("/addprompt/", methods=["GET", "POST"])
@login_required
def addprompt():
    if request.method == "POST":
        prompt = request.form['textarea']
        category = request.form['category']
        user = current_user.id

        if prompt:
            data = Prompt(prompt, category, user)
            db.session.add(data)
            db.session.commit()
            flash(f'Prompt added!')
            return render_template("addprompt.html")
        flash(f'Provide a Prompt!')
        return render_template("addprompt.html")
        
    else:
        return render_template("addprompt.html")

@app.route("/prompts/", methods=["GET", "POST"])
@login_required
def prompts():

    data = db.session.query(Prompt).order_by(func.random()).first()
    randomPrompt = data.prompt
    category = data.category

    if request.method == "POST":
        if request.form.get("randomQuote"):
            return render_template("prompts.html", prompt = randomPrompt, category = category)
    else:
        return render_template("prompts.html", prompt = randomPrompt, category = category)

@app.route("/addsession/", methods=["GET", "POST"])
@login_required
def addsession():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['number']
        category = request.form['category']
        date = request.form['date']
        location = request.form['location']
        email = request.form['email']
        coomment = request.form['comment']
        userid = current_user.id

        if name and date:
            data = Session(name, phone, category, date, location, email, coomment, userid)
            db.session.add(data)
            db.session.commit()
            flash(f'Session saved!')
            return render_template("addsession.html")
        else:
            flash(f'Name and date are mandatory!')
            return render_template("addsession.html")
    else:
        return render_template("addsession.html")

@app.route("/sessions/")
@login_required
def sessions():
    data = db.session.query(Session).filter(Session.date > date.today()).order_by(asc(Session.date))

    return render_template("sessions.html", data = data)

@app.route("/weather/", methods=["GET", "POST"])
@login_required
def weather():
    # sunrise api https://api.met.no/weatherapi/sunrise/2.0/documentation
    # open street maps https://nominatim.org/release-docs/develop/api/Overview/
    # https://nominatim.openstreetmap.org/search.php?q=riga&format=json

    offset = "+02:00" #hrdcoded to Latvia

    if request.method == "POST":

        if not request.form['location']:
            lat = "56.948322076480686" #Riga by default
            lon = "24.120530235484104" #Riga by default
            displayName = "Riga (Default)"
        else:
            location = request.form['location'].encode("ascii", errors="ignore").decode() #remove non-ascii. not great, not terrible
            link = "https://nominatim.openstreetmap.org/search.php?q=" + location + "&format=json"
            
            locationRequest = urllib.request.urlopen(link).read()
            locationJson = json.loads(locationRequest)

            lat = locationJson[0]['lat']
            lon = locationJson[0]['lon']
            displayName = locationJson[0]['display_name']

        if not request.form['date']:
            sunDate = str(date.today())
        else:
            sunDate = request.form['date']

        # Sun data
        sunReq = urllib.request.urlopen("https://api.met.no/weatherapi/sunrise/2.0/.json?lat=" + lat + "&lon=" + lon + "&date=" + sunDate + "&offset=" + offset).read()
        sunJson = json.loads(sunReq)

        sunData = {
            "sunrise": str(sunJson['location']['time'][0]['sunrise']['time'])[11:19],
            "sunset": str(sunJson['location']['time'][0]['sunset']['time'])[11:19]
        }

        return render_template("weather.html", sunData = sunData, date = sunDate, displayName = displayName)

    else:
        lat = "56.948322076480686" #Riga by default
        lon = "24.120530235484104" #Riga by default
        displayName = "Riga (Default)"
        sunDate = str(date.today())

        sunReq = urllib.request.urlopen("https://api.met.no/weatherapi/sunrise/2.0/.json?lat=" + lat + "&lon=" + lon + "&date=" + sunDate + "&offset=" + offset).read()
        sunJson = json.loads(sunReq)

        sunData = {
            "sunrise": str(sunJson['location']['time'][0]['sunrise']['time'])[11:19],
            "sunset": str(sunJson['location']['time'][0]['sunset']['time'])[11:19]
        }

        return render_template("weather.html", sunData = sunData, date = sunDate, displayName = displayName)


# @app.route("/api/data")
# def get_data():
#     return app.send_static_file("data.json")


if __name__ == '__main__':
    app.run()

