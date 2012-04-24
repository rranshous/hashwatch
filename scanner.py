
"""
We scan twitter for tweets containing a given
hash tag.

We publish events when we find them
"""

import twitter
import redis
from lib.revent import ReventClient
from lib.config import config
import sys

# setup our config
if 'production' in sys.argv:
    config.setup('./production.ini')
else:
    config.setup('./development.ini')

redis_host = config.get('redis_host')
redis_db = config.get('redis_db')

twitter_api = twitter.Api()

NS = 'tweet_scanner'
rc = redis.Redis(redis_host,
                 db=redis_db)
revent = ReventClient(redis_host = redis_host,
                      redis_db = redis_db)

def tweet_search(search_string, since_tweet_id=None):
    """
    yields up tweet data matching search string since tweet id.

    Pages intelligently.

    returns tweet data as dict
    """

    print 'searching: %s %s' % (search_string, since_tweet_id)

    responses = True
    page = 1

    # keep pulling and yielding tweet data until there
    # aint no more
    while responses:
        print 'page: %s' % page
        responses = twitter_api.GetSearch(search_string,
                                          since_id = since_tweet_id,
                                          per_page = 50,
                                          page = page)
        for response in reversed(responses):
            yield response.AsDict()

        page += 1


def get_last_tweet_id(search_string):
    """ returns last tweets id (from redis) """
    return rc.get('%s:last_tweet_id:%s' % (NS, search_string))

def set_last_tweet_id(search_string, tweet_id):
    """ sets last tweet id (in redis) """
    # only set if higher than currently set
    last_tweet_id = get_last_tweet_id(search_string) or 0
    if int(tweet_id) > int(last_tweet_id):
        print 'setting: %s' % tweet_id
        rc.set('%s:last_tweet_id:%s' % (NS, search_string), tweet_id)
    return True

def run(search_string):
    """
    Scans twitter for tweets containing target hash.
    fires revent events for each tweet found.

    searches for new tweets since last run
    """

    # where did we stop last time?
    last_tweet_id = get_last_tweet_id(search_string)

    print 'last id: %s' % last_tweet_id

    # go through the tweet data matching the hash
    for tweet_data in tweet_search(search_string, last_tweet_id):

        # add in to the data the search string
        tweet_data['search_string'] = search_string

        # let the world (our network at least) know about tweet
        print 'firing: %s' % tweet_data.get('id')
        revent.fire('new_tweet', tweet_data)

        # set the last tweet id in case we are done running
        set_last_tweet_id(search_string, tweet_data.get('id'))

if __name__ == '__main__':
    # we should get the target string
    import sys
    print 'args: %s' % sys.argv
    assert len(sys.argv) > 1, "Please specify search string"
    search_string = sys.argv[1]
    run(search_string)
