import os
from flask import Flask, render_template, request, redirect, url_for, session
from logging_hook import init_logger, flask_request_hook, log_event

from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Initialize logging
init_logger()

# OAuth Blueprints
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/oauth/google/authorized"
)
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    scope="user:email",
    redirect_url="/oauth/github/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login/google")
app.register_blueprint(github_bp, url_prefix="/login/github")

# Log every request
@app.before_request
def before_request():
    flask_request_hook(request)

# Home page
@app.route("/")
def home():
    user = session.get("user")
    if user:
        return render_template("home.html", user=user)
    return redirect(url_for("login"))

# Login form & OAuth options
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "email": request.form["email"],
            "name": request.form["name"],
            "gender": request.form["gender"],
            "profession": request.form["profession"]
        }
        session["user"] = data
        log_event("form_login", data, user_id=data["email"])
        return redirect(url_for("home"))
    return render_template("login.html")

# Google OAuth callback
@app.route("/oauth/google/authorized")
def google_authorized():
    resp = google.get("/oauth2/v2/userinfo")
    info = resp.json()
    user = {
        "email": info["email"],
        "name": info.get("name"),
        "gender": None,
        "profession": None,
        "provider": "google"
    }
    session["user"] = user
    log_event("oauth_login", {"provider": "google", "info": info}, user_id=info["email"])
    return redirect(url_for("home"))

# GitHub OAuth callback
@app.route("/oauth/github/authorized")
def github_authorized():
    resp = github.get("/user")
    info = resp.json()
    emails = github.get("/user/emails").json()
    primary_email = next((e["email"] for e in emails if e.get("primary")), None)
    user = {
        "email": primary_email,
        "name": info.get("name") or info.get("login"),
        "gender": None,
        "profession": None,
        "provider": "github"
    }
    session["user"] = user
    log_event("oauth_login", {"provider": "github", "info": info}, user_id=primary_email)
    return redirect(url_for("home"))

# Sign out
@app.route("/logout")
def logout():
    user = session.pop("user", None)
    if user:
        log_event("user_logout", {"email": user.get("email")}, user_id=user.get("email"))
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)