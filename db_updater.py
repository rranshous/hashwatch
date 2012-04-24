"""
consumers new tweet / new embed details events
and updates the redis DB tracking tweets
"""

import redis
from lib.revent import ReventClient
import time
import sys
from keys import keys
from lib.config import config

# setup our config
if 'production' in sys.argv:
    config.setup('./production.ini')
else:
    config.setup('./development.ini')

NS = 'db_updater'
redis_host = config.get('redis_host')
redis_db = config.get('redis_db')

rc = redis.Redis(redis_host,
                 db=redis_db)

# we're going to subscribe
event_filter = '^new_.*_oembed_details$|^new_tweet$'
revent = ReventClient(channel_key = NS,
                      filter_string = event_filter,
                      redis_host = redis_host,
                      redis_db = redis_db,
                      verified = True,
                      verify_timeout = 60)

def handle_new_tweet(tweet_data):
    """
    updates / adds tweet data to DB
    """

    assert tweet_data.get('id'), "Tweet Must have ID"
    assert tweet_data.get('search_string'), "Tweet must have search string"

    # check for this tweet already being tracked
    set_key = keys.tweet_search_set(tweet_data.get('search_string'))
    tweet_id = tweet_data.get('id')
    found = rc.zrank(set_key, tweet_id)
    print 'set key: %s' % set_key
    print 'found: %s' % found

    if not found:

        # set main hash
        key = keys.tweet_data(tweet_data.get('id'))
        rc.hmset(key, tweet_data)

        # add to our weighted set
        # keep the value as the id and the weight
        print 'adding: %s' % tweet_id
        rc.zadd(set_key, tweet_id, tweet_id)

        # fire event that tweet was added to db
        revent.fire('new_tweet_saved', tweet_data)

        return True

    return False

def handle_new_oembed_details(embed_data):
    """
    updates the twitter's data w/ the embed data
    """

    source = embed_data.get('oembed_source').strip()
    tweet_id = embed_data.get('tweet_id')

    assert tweet_id, "Can only handle tweets"
    assert embed_data.get('html'), "Need HTML for embedding"
    assert source, "Need to know where this came from"

    print 'new oembed details: %s %s' % (source, len(embed_data))

    # store all the data we received
    key = keys.tweet_embed_data(source,tweet_id)
    r = rc.hmset(key, embed_data)

    # we are giving preference to embedly data,
    # so also update the tweet's data w/ the embedly html
    if source == 'embedly':
        print 'embedly found, updating tweet data'
        key = keys.tweet_data(tweet_id)
        r = rc.hset(key, 'embed_html', embed_data.get('html'))

    # fire event that oembed has been saved
    revent.fire('new_oembed_details_saved', embed_data)

    return True

def run():
    """
    pulls data from events, stores in DB
    """

    while True:

        # get event, blah
        event_name, event_data = revent.get_event(block=True, timeout=5)

        if event_name is not None:
            print 'received: %s' % event_name

            if event_name.endswith('_oembed_details'):
                handle_new_oembed_details(event_data)

            elif event_name == 'new_tweet':
                handle_new_tweet(event_data)

            # and we're done
            assert revent.verify_msg(event_name, event_data), \
                    "Could not verify %s" % event_name

if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception, ex:
            raise
            time.sleep(60*2)

