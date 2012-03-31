"""
defines getter's for all the redis
keys we're going to be using
"""

class AttrDict(dict):
    def __getattribute__(self, a):
        r = self.__getitem__(a)
        if r:
            return r
        return dict.__getattribute__(self, a)

keys = AttrDict({

        # hash holding info about tweet
        'tweet_data':lambda id: 'tweets:%s' % id<

        # ordered set of tweet id's w/ weight as timestamp
        # key's are defined by search string
        'tweet_search_set': lambda ss: 'tweets:search_set:%s' % ss
})
