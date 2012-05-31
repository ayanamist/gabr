import flask

from application import app
from ..lib import decorators

@app.route("/status/<int:id>")
@decorators.templated("timeline")
def status(id):
    pass


@app.route("/status/<int:id>/reply", methods=["GET", "POST"])
@decorators.login_required
def status_reply(id):
    return ""


@app.route("/status/<int:id>/retweet", methods=["GET", "POST"])
@decorators.login_required
def status_retweet(id):
    return ""


@app.route("/status/<int:id>/favorite", methods=["POST"])
@decorators.login_required
def status_favorite(id):
    return ""


@app.route("/status/<int:id>/unfavorite", methods=["POST"])
@decorators.login_required
def status_unfavorite(id):
    return ""


@app.route("/status/<int:id>/delete", methods=["GET", "POST"])
@decorators.login_required
def status_favorite(id):
    return ""

