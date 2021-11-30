import os
from datetime import date, datetime
from functools import wraps

from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, redirect, abort, session, url_for, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

import processor
from form import CreateNewSection, ContactForm
from notifications_center import Notifications

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", None)
# app.config['SERVER_NAME'] = 'localhost:5000'
ckeditor = CKEditor(app)
Bootstrap(app)
oauth = OAuth(app)


# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL1", "sqlite:///cv.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# GOOGLE Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

EMAIL_ACCOUNT = os.environ.get("EMAIL_ACCOUNT")


class CvContent(db.Model):
    __tablename__ = "section"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    description = db.Column(db.Text)
    body = db.Column(db.Text, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


db.create_all()

year = date.today().strftime("%Y")
now = datetime.now()
current_time = now.strftime("%H:%M")
notifications = Notifications()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if user["email"] != EMAIL_ACCOUNT:
            return abort(403, description="Only Luis, the admin has access to these resources.")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/", methods=["POST", "GET"])
def landing():
    user = session.get("user")
    all_sections = CvContent.query.all()
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        notifications.send_message(name, email, subject, message)
        return redirect(url_for("landing"))

    return render_template("index.html", year=year, sections=all_sections, user=user, form=form, email_account=EMAIL_ACCOUNT)


@app.route("/admin-update-resume/<int:section_id>", methods=["POST", "GET"])
@admin_only
def update(section_id):
    section = CvContent.query.get(section_id)
    edit_form = CreateNewSection(
        section_title=section.title,
        section_description=section.description,
        section_body=section.body
    )
    if edit_form.validate_on_submit():
        section.title = edit_form.section_title.data
        section.description = edit_form.section_description.data
        section.body = edit_form.section_body.data
        db.session.commit()
        return redirect(url_for("landing"))
    return render_template("cv_content.html", form=edit_form, section_id=section_id)


@app.route("/login")
def login():
    try:
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url=GOOGLE_DISCOVERY_URL,
            client_kwargs={
                "scope": "openid email profile"
            }
        )

        # Redirect to google_auth function
        redirect_uri = url_for("callback", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except ConnectionError:
        return abort(503, description="There has been a problem contacting Google, try again later.")


@app.route("/callback")
def callback():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    if user:
        session["user"] = user

    return redirect(url_for('landing'))


@app.route("/chatbot", methods=["POST", "GET"])
def chatbot():
    return render_template("chatbot.html", time=current_time)


@app.route("/get", methods=["POST", "GET"])
def chat_bot_response():
    user_text = request.args.get("msg")
    return processor.chatbot_response(user_text)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("landing"))


@app.route("/cookies-policy")
def cookies():
    return render_template("cookies-policy.html")


@app.route("/privacy-policy")
def privacy():
    return render_template("privacy-policy.html")


if __name__ == "__main__":
    app.run(debug=True)

