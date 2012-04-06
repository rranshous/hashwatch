

"""
simple wsgi app which produces a paged html
output of tweets
"""

import sys
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

import bottle
from bottle import MakoTemplate
from bottle import view as _view
from bottle import get, install, run, Bottle, route, \
                   mako_view, request
import redis

from keys import keys
from lib.configsmash import ConfigSmasher

# read in our config
if 'production' in sys.argv:
    config = ConfigSmasher(['./production.ini']).smash()
else:
    config = ConfigSmasher(['./development.ini']).smash()


def get_search_string():
    """
    returns the search string for the request
    will give priority to config, than start
    inspecting request details to figure it out
    """

    # check config
    search_string = config.get('search_string')

    # if we didn't get it from the config,
    # than lets check the request
    if not search_string:
        # the project assumes here the search
        # string is the host (w/o the TLD)
        host = request.environ.get('HTTP_HOST',
                request.environ.get('SERVER_NAME'))

        # in case we are on a subdomain, and strip the TLD
        # ex: twitterstuff.mydomain.net
        search_string = host.split('.')[-1]

    return search_string


# are we in debug mode?
DEBUG = config.get('debug')
bottle.debug(DEBUG)
log.debug('debug?: %s',DEBUG)

# setup our redis client
rc = redis.Redis(config.get('redis_host'),
                 config.get('redis_db'))

# create our application
application = Bottle()

# update bottle's mako views to be utf8
MakoTemplate.output_encoding = 'utf-8'
MakoTemplate.input_encoding = 'utf-8'
#MakoTemplate.default_filters = ['decode.utf8']

# default page
@application.route('/')
@application.route('/<tweet_offset>/')
@application.route('/<tweet_offset>/<page_size>')
@mako_view('tweet_page')
def tweet_page(tweet_offset=0, page_size=20):
    """
    gets page worth of tweet data, returns data for template
    """

    # respect max page size
    page_size = max(page_size, int(config.get('max_page_size')))
    tweet_offset = int(tweet_offset)

    log.debug('tweet_page: %s %s', tweet_offset, page_size)

    # get our search term
    search_string = get_search_string()

    # pull the tweets from redis
    key = keys.tweet_search_set(search_string)
    tweet_data = rc.sort(key,
                         start=tweet_offset,
                         num=page_size,
                         get='tweets:*->embed_html',
                         desc=True)

    # the tweet data is going to be ut8 encoded
    tweet_data = [x.decode('utf-8') for x in tweet_data]

    log.debug('tweet data: %s', tweet_data)

    # return the data for the template
    return dict(
        tweet_data = tweet_data,
        tweet_offset = tweet_offset,
        page_size = page_size,
        search_string = search_string
    )


if __name__ == '__main__':
    log.debug('starting')
    run(application,
        host=config.get('host'),
        port=config.get('port'),
        reloader=True if DEBUG else False
    )
