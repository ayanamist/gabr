import bisect

import flask

class IndicesReplace(object):
    def __init__(self, s, auto_escape=True):
        self.original_s = s
        self._str_list = list()
        self._str_indices = [0]
        self.escape = auto_escape

    def _escape(self, s):
        if self.escape:
            return flask.escape(s)
        else:
            return s

    def __unicode__(self):
        if self._str_list:
            result = list()
            for i, s in enumerate(self._str_list):
                result.append(self._escape(self.original_s[self._str_indices[i * 2]:self._str_indices[i * 2 + 1]]))
                result.append(s)
            result.append(self._escape(self.original_s[self._str_indices[-1]:]))
            return u"".join(result)
        else:
            return unicode(self.original_s)

    def __str__(self):
        return unicode(self).encode("UTF8")

    def replace_indices(self, start, stop, replace_text):
        i = bisect.bisect(self._str_indices, start)
        self._str_indices.insert(i, start)
        self._str_indices.insert(i + 1, stop)
        self._str_list.insert(i // 2, replace_text)
        return self
