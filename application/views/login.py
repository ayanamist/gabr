import flask

from application import app

@app.route("/login")
def login():
    data = {
        "title": "Login",
        }
    return flask.render_template("login.html", **data)


@app.route("/oauth", methods=["POST"])
def oauth_login():
    app_password = app.config["INVITE_CODE"]
    if (app_password and app_password == flask.request.form.get("invitecode")) or (not app_password):
        pass
    else:
        flask.redirect(flask.url_for("login"))


@app.route("/oauth_callback")
def oauth_callback():
    pass

