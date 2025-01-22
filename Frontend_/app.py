import joblib
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pandas as pd
import pickle
import requests
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])





@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")


@app.route('/terms')
def terms():
    return render_template("tc.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")
    return render_template('signup.html', form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/disindex")

def disindex():
    return render_template("disindex.html")

@app.route('/predicttrans', methods=["POST"])
def predicttrans():
    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        print(to_predict_list) 
        print(type(to_predict_list))  
    # print('['trans'][-1]['trans'][-1]['trans'][-1]['trans'][-1]', ['trans'][-1]) 
    # print('manu', int(to_predict_list['trans'][-1]))
    if int(to_predict_list['trans'][-1]) == 1:
        prediction = "This is the fraudlent transaction "
    else:
        prediction = "This is the Normal transaction"
    return render_template("prediction_result.html", prediction_text=prediction)


@app.route("/prediction")
@login_required
def liver():
    return render_template("prediction.html")

@app.route('/disaster-recovery')
def disaster_recovery():
    return render_template('initiate_dr.html') 


@app.route('/start_server', methods=['POST'])
def start_server():
    try:
        # Set maintenance mode off in Flask 2
        response = requests.post('http://127.0.0.1:5000/set_maintenance_mode/off')
        
        # Redirect to Flask 2's index page
        return redirect('http://127.0.0.1:8000/')  # Redirect to Flask 2's index route
    except requests.exceptions.RequestException as e:
        return f"Error activating normal mode: {e}"

@app.route('/stop_server', methods=['POST'])
def stop_server():
    try:
        # Set maintenance mode on in Flask 2
        response = requests.post('http://127.0.0.1:5000/set_maintenance_mode/on')
        
        # Redirect to Flask 2's index page
        return redirect('http://127.0.0.1:8000/')  # Redirect to Flask 2's index route
    except requests.exceptions.RequestException as e:
        return f"Error activating maintenance mode: {e}"



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context(): 
        db.create_all()
        app.run(port=8000,debug=True)

