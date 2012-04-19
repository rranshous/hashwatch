"""
we are going to consume new tweet events
and fire off the embed info for those tweets
"""

import oembed
from lib.revent import ReventClient
import time

# setup our oEmbeded client
consumer = oembed.OEmbedConsumer()
endpoint_url = 'https://api.twitter.com/1/statuses/oembed.json'
endpoint = oembed.OEmbedEndpoint(endpoint_url, ['*'])
consumer.addEndpoint(endpoint)

NS = 'embeder'
redis_host = '127.0.0.1'
revent = ReventClient(channel_key = NS,
                      events_to_watch = ['new_tweet'],
                      redis_host = redis_host,
                      verified = True,
                      verify_timeout = 60)

def get_tweet_oembed_data(tweet_data):
    """
    Queries twitter for tweets oEmbed data, returns it as dict
    """

    print 'handling tweet data: %s' % tweet_data.get('id')

    # get the embed data for the tweet
    # pass tweet id instead of it's URL since we'd have to build the url
    embed_result = consumer.embed('',id=tweet_data.get('id'))
    assert embed_result, "No oEmbeded response for %s" % tweet_data.get('id')
    embed_data = embed_result.getData()
    print 'got embed data: %s' % tweet_data.get('id')
    return embed_data


def run():
    """
    waits for new tweet events, produces new_embed_details events
    """

    # loop waiting for events
    while True:

        event_name, tweet_data = revent.get_event(block=True, timeout=5)

        # did we get something?
        if event_name is not None:

            # find the embed data
            embed_data = get_tweet_oembed_data(tweet_data)

            # inject in some of our twitter data so that they events
            # can be associated
            embed_data['tweet_id'] = tweet_data.get('id')

            # fire off the event
            revent.fire('new_oembed_details', embed_data)

            # and we're done
            assert revent.verify_msg(event_name, tweet_data), \
                    "Could not verify: %s" % event_name

if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception, ex:
            print 'EXCEPTION: %s' % ex
            time.sleep(60*2)
