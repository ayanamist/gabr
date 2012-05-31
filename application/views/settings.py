from application import app
from ..lib import decorators

@app.route("/settings/")
@decorators.templated()
def settings():
    pass