"""
consumers new tweet / new embed details events
and updates the redis DB tracking tweets
"""

import redis
from lib.revent import ReventClient
import time
from keys import keys

NS = 'db_updater'
redis_host = '127.0.0.1'
rc = redis.Redis(redis_host)
filter_string = ReventClient.build_filter_string('new_tweet',
                                                 'new_embed_details')
revent = ReventClient(channel_key = NS,
                      filter_string = 'new_tweet',
                      auto_create_channel = True,
                      redis_host = redis_host,
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
    if int(rc.zcount(set_key,tweet_data.get('id'),tweet_data.get('id'))) > 0:

        # set main hash
        key = keys.tweet_data(tweet_data.get('id'))
        rc.hmset(key, tweet_data)

        # add to our weighted set
        return rc.zadd(set_key, '1', tweet_data.get('id'))

        # fire event that tweet was added to db
        revent.fire('new_tweet_saved', tweet_data)

def handle_new_oembed_details(embed_data):
    """
    updates the twitter's data w/ the embed data
    """

    assert embed_data.get('tweet_id'), "Can only handle tweets"
    assert embed_data.get('html'), "Need HTML for embedding"

    key = keys.tweet_data(tweet_data.get('id'))
    r = rc.hset(key, 'embed_html', embed_data.get('html'))

    # fire event that oembed has been saved
    revent.fire('new_oembed_details_saved', embed_data)

    return r

def run():
    """
    pulls data from events, stores in DB
    """

    while True:

        # get event, blah
        event_name, event_data = revent.get_event(block=True, timeout=5)

        if event_name is not None:

            print 'handling: %s' % event_name

            # push event details to handler
            handler = globals().get('handle_%s' % event_name)
            assert handler, "No handler for %s" % event_name
            handler(event_data)

            # and we're done
            assert revent.verify_msg(event_name, event_data), \
                    "Could not verify %s" % event_name

if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception, ex:
            print 'EXCEPTION: %s' % ex
            time.sleep(60*2)

