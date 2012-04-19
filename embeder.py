"""
we are going to consume new tweet events
and fire off the embed info for those tweets
"""

import lib.oembed as oembed
from lib.revent import ReventClient
import time
import os.path

# TODO: consolidate oembed consumers

# read in our secret embedly key
HERE = os.path.abspath(os.path.dirname(__file__))
key_file_path = os.path.abspath(os.path.join(HERE,'./embedly_key.txt'))
with open(key_file_path,'r') as fh:
    EMBEDLY_KEY = fh.readline().strip()

# setup our oEmbeded client for twitter
twitter_embed_consumer = oembed.OEmbedConsumer()
endpoint_url = 'https://api.twitter.com/1/statuses/oembed.json'
endpoint = oembed.OEmbedEndpoint(endpoint_url, ['*'])
twitter_embed_consumer.addEndpoint(endpoint)

# setup oembed client for embedly
embedly_embed_consumer = oembed.OEmbedConsumer()
endpoint_url = 'http://api.embed.ly/1/oembed'
endpoint = oembed.OEmbedEndpoint(endpoint_url, ['*'])
embedly_embed_consumer.addEndpoint(endpoint)

NS = 'embeder'
redis_host = '127.0.0.1'
revent = ReventClient(channel_key = NS,
                      events_to_watch = ['new_tweet'],
                      redis_host = redis_host,
                      verified = True,
                      verify_timeout = 60)

def get_twitter_embed_data(tweet_data):
    """
    Queries twitter for tweets oEmbed data, returns it as dict
    """

    print 'getting twitter embed data: %s' % tweet_data.get('id')
    # get the embed data for the tweet
    # pass tweet id instead of it's URL since we'd have to build the url
    embed_result = twitter_embed_consumer.embed('',id=tweet_data.get('id'))
    assert embed_result, "No oEmbeded response for %s" % tweet_data.get('id')
    embed_data = embed_result.getData()
    return embed_data

def get_embedly_embed_data(twitter_embed_data):
    """
    Queries embedly for extra HTML to embed along side the tweet
    """

    print 'getting embedly embed data: %s' % twitter_embed_data.get('url')
    embed_result = embedly_embed_consumer.embed(twitter_embed_data.get('url'),
                                                key=EMBEDLY_KEY)
    assert embed_result, \
            "No Embedly response for %s" % twitter_embed_data.get('url')
    embed_data = embed_result.getData()
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

            # find the embed data from twitter
            # if will contain the URL we need to get the
            # embedly data
            twitter_embed_data = get_twitter_embed_data(tweet_data)

            # inject in some of our twitter data so that they events
            # can be associated
            twitter_embed_data['tweet_id'] = tweet_data.get('id')

            # got the twitter data !
            revent.fire('new_twitter_oembed_details', twitter_embed_data)

            # now hit up embedly
            embedly_embed_data = get_embedly_embed_data(twitter_embed_data)

            # fire off the events
            revent.fire('new_embedly_oembed_details', embedly_embed_data)

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
