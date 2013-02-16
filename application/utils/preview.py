import re
# All functions should return a tuple containing a thumbnail and a full image url.

_instagram_regex = re.compile(r"(http(?:s)?://(?:instagram\.com|instagr\.am)?/p/[a-z0-9\-_]+/)", re.I)


def media_instagram(url):
    matched = _instagram_regex.match(url)
    if matched:
        return "%smedia/?size=m" % matched.group(0), "%smedia/?size=l" % matched.group(0)


_sina_regex = re.compile(r"(http(?:s)?://ww(\d)\.sinaimg\.cn/([a-z]+)/[a-z0-9]+\.[a-z]+)", re.I)


def media_sina(url):
    matched = _sina_regex.match(url)
    if matched:
        return ("%s%s%s" % (url[:matched.start(2)], t, url[matched.end(2):]) for t in ("small", "large"))


_twitpic_regex = re.compile(r"(http(?:s)?://twitpic\.com/([0-9a-z]+))", re.I)


def media_twitpic(url):
    matched = _twitpic_regex.match(url)
    if matched:
        return ("%sshow/%s/%s" % (url[:matched.start(2)], t, url[matched.start(2):]) for t in ("thumb", "large"))


_imgly_regex = re.compile(r"(http(?:s)?://img\.ly/([0-9a-z]+))", re.I)


def media_imgly(url):
    matched = _imgly_regex.match(url)
    if matched:
        return ("%sshow/%s/%s" % (url[:matched.start(2)], t, url[matched.start(2):]) for t in ("medium", "full"))


_yfrog_regex = re.compile(r"(http(?:s)?://yfrog\.com/[0-9a-z]+)", re.I)


def media_yfrog(url):
    matched = _yfrog_regex.match(url)
    if matched:
        return ("%s:%s" % (matched.group(0), t) for t in ("iphone", "medium"))


_plixi_regex = re.compile(r"(http://(?:lockerz|plixi)?\.com/[ps]/[0-9]+)", re.I)


def media_plixi(url):
    matched = _plixi_regex.match(url)
    if matched:
        return ("http://api.plixi.com/api/tpapi.svc/imagefromurl?url=%s&size=%s" % (matched.group(0), t) for t in (
            "mobile", "big"))


_twimg_regex = re.compile(r"(http(?:s)?://pbs.twimg.com/media/[A-Za-z0-9\._]+)", re.I)


def media_twimg(url):
    matched = _twimg_regex.match(url)
    if matched:
        return ("%s:%s" % (matched.group(0), t) for t in ("small", "large"))