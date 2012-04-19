"""
defines getter's for all the redis
keys we're going to be using
"""

class AttrDict(dict):
    def __getattr__(self, a):
        print 'getting: %s' % a
        try:
            r = self[a]
        except IndexError:
            raise AttributeError(a)
        return r

keys = AttrDict({

        # hash holding info about tweet
        'tweet_data':lambda id: 'tweets:%s' % id,

        # hash holding info about tweets embed data
        'tweet_embed_data': lambda source, id:
                                'tweets:embed_data:%s:%s' % (id,source),

        # ordered set of tweet id's w/ weight as timestamp
        # key's are defined by search string
        'tweet_search_set': lambda ss: 'tweets:search_set:%s' % ss
})
