import os
from flask import Flask, redirect, url_for, render_template, flash, session
from flask_wtf import FlaskForm
import pyshorteners
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

#####SQLite######
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(base_dir,"data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app,db)

class UrlT(db.Model):
    id = db.Column(db.Integer ,primary_key=True)
    url_origo = db.Column(db.Text)
    url_shortened = db.Column(db.Text)
    def __init__(self,url_origo,url_shortened):
        self.url_origo = url_origo
        self.url_shortened = url_shortened
    def __repr__(self):
        return f"{self.url_shortened}"

#####Form######
app.config["SECRET_KEY"] = "dev"
class UrlForm(FlaskForm):
    url = StringField("Place for url: ",validators=[DataRequired()], render_kw={"placeholder": "https://"})
    submit = SubmitField("Short URL")

###############
@app.route("/", methods=["GET","POST"])
def index():
    form = UrlForm()
    shortener = pyshorteners.Shortener()
    selected_rows = UrlT.query.all()[::-1]
    if form.validate_on_submit():
        url_origo = form.url.data
        url_shortened = shortener.tinyurl.short(url_origo)
        new_row = UrlT(url_origo,url_shortened)
        db.session.add(new_row)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("index.html",form=form,selected_rows = selected_rows)
