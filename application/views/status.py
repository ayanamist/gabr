import flask

from application import app
from ..lib import decorators

@app.route("/status/<int:id>")
@decorators.templated("timeline.html")
def status(id):
    pass


@app.route("/status/<int:id>/reply", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_reply.html")
def status_reply(id):
    return {}


@app.route("/status/<int:id>/replyall")
@decorators.login_required
@decorators.templated("status_reply.html")
def status_replyall(id):
    return {}


@app.route("/status/<int:id>/retweet", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("status_retweet.html")
def status_retweet(id):
    return {}


@app.route("/status/<int:id>/favorite", methods=["POST"])
@decorators.login_required
@decorators.templated("timeline.html")
def status_favorite(id):
    return {}


@app.route("/status/<int:id>/unfavorite", methods=["POST"])
@decorators.login_required
@decorators.templated("timeline.html")
def status_unfavorite(id):
    return {}


@app.route("/status/<int:id>/delete", methods=["GET", "POST"])
@decorators.login_required
@decorators.templated("timeline.html")
def status_delete(id):
    return {}

