import flask

from application import app

@app.route("/login")
def login():
    data = {
        "title": "Login",
    }
    return flask.render_template("login.html", **data)

@app.route("/oauth", methods="POST")
def oauth_login():
    pass

@app.route("/oauth_callback")
def oauth_callback():
    pass