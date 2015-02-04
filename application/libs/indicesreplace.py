from __future__ import absolute_import

import bisect


class IndicesReplace(object):
    def __init__(self, s):
        self.original_s = s
        self._str_list = list()
        self._str_indices = [0]

    def __unicode__(self):
        if self._str_list:
            result = list()
            for i, s in enumerate(self._str_list):
                result.append(self.original_s[self._str_indices[i * 2]:self._str_indices[i * 2 + 1]])
                result.append(s)
            result.append(self.original_s[self._str_indices[-1]:])
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
