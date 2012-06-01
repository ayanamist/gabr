from application import app
from ..lib import decorators

@app.route("/user/<screen_name>")
@decorators.templated("user_show.html")
def user(screen_name):
    return {}
