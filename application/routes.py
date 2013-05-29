from __future__ import absolute_import

from werkzeug import import_string, cached_property

from application import app


class LazyView(object):
    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit(".", 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)


def url(url_rule, import_name, **options):
    view = LazyView("application.views." + import_name)
    app.add_url_rule(url_rule, view_func=view, **options)


url("/login", "login.login", methods=["GET", "POST"])
url("/logout", "login.logout")

url("/rss", "rss.rss_url")
url("/rss/<sid>", "rss.home_rss")

url("/post", "status.status_post", methods=["GET", "POST"])
url("/status/<status_id>", "status.status")
url("/status/<status_id>/reply", "status.status_reply", methods=["GET", "POST"])
url("/status/<status_id>/replyall", "status.status_replyall")
url("/status/<status_id>/retweet", "status.status_retweet", methods=["GET", "POST"])
url("/status/<status_id>/favorite", "status.status_favorite")
url("/status/<status_id>/unfavorite", "status.status_unfavorite")
url("/status/<status_id>/delete", "status.status_delete", methods=['GET', 'POST'])

url("/", "timeline.home_timeline")
url("/connect", "timeline.connect_timeline")
url("/activity", "timeline.activity_timeline")
url("/search", "timeline.search_tweets")
url("/user/<screen_name>/favorites", "timeline.user_favorites")

url("/user/<screen_name>", "user.user")
url("/user/<screen_name>/follow", "user.user_follow")
url("/user/<screen_name>/unfollow", "user.user_unfollow")
url("/user/<screen_name>/block", "user.user_block")
url("/user/<screen_name>/unblock", "user.user_unblock")
url("/user/<screen_name>/reportspam", "user.user_reportspam")
