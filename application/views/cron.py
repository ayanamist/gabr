import urllib

from google.appengine.api import urlfetch

from application import app
from application import utils

@app.route("/cron/<sid>")
def cron(sid):
    hub_url = "http://pubsubhubbub.appspot.com"
    url = utils.abs_url_for("home_rss", sid=sid)
    urlfetch.fetch(hub_url, payload=urllib.urlencode({"hub.url": url, "hub.mode": "publish"}), method="POST")
    return ""
