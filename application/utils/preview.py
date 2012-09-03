import re
# All functions should return a tuple containing a thumbnail and a full image url.

_instagram_regex = re.compile(r"(http(?:s)?://(?:instagram\.com|instagr\.am)?/p/[a-z0-9\-_]+/)", re.I)

def media_instagram(url):
    matched = _instagram_regex.match(url)
    if matched:
        return "%smedia/?size=m" % matched.group(0), "%smedia/?size=l" % matched.group(0)

_sina_regex = re.compile(r"(http(?:s)?://ww(?:\d+)?\.sinaimg\.cn/([a-z]+)/[a-z0-9]+\.[a-z]+)", re.I)

def media_sina(url):
    matched = _sina_regex.match(url)
    if matched:
        return ("%s%s%s" % (url[:matched.start(2)], t, url[matched.end(2):]) for t in ("small", "large"))

_twitpic_regex = re.compile(r"(http(?:s)?://twitpic\.com/([0-9a-z]+)/)", re.I)

def media_twitpic(url):
    matched = _twitpic_regex.match(url)
    if matched:
        return ("%sshow/%s/%s" % (url[:matched.start(2)], t, url[matched.start(2):]) for t in ("thumb", "large"))

_imgly_regex = re.compile(r"(http(?:s)?://img\.ly/([0-9a-z]+)/)", re.I)

def media_imgly(url):
    matched = _imgly_regex.match(url)
    if matched:
        return ("%sshow/%s/%s" % (url[:matched.start(2)], t, url[matched.start(2):]) for t in ("medium", "full"))
