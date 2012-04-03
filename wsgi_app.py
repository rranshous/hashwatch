

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
from bottle import view as _view
from bottle import get, install, run, Bottle, route, \
                   mako_view
import redis

from keys import keys
from lib.configsmash import ConfigSmasher

# read in our config
if 'production' in sys.argv:
    config = ConfigSmasher(['./production.ini']).smash()
else:
    config = ConfigSmasher(['./development.ini']).smash()

# are we in debug mode?
DEBUG = config.get('debug')
bottle.debug(DEBUG)
log.debug('debug?: %s',DEBUG)

# setup our redis client
rc = redis.Redis(config.get('redis_host'))

# create our application
application = Bottle()

# default page
@application.route('/')
@application.route('/<tweet_offset>/<page_size>/')
@mako_view('tweet_page')
def tweet_page(tweet_offset=0, page_size=20):
    """
    gets page worth of tweet data, returns data for template
    """

    # respect max page size
    page_size = max(page_size, int(config.get('max_page_size')))

    log.debug('tweet_page: %s %s', tweet_offset, page_size)

    # get our search term from config
    search_string = config.get('search_string')

    # pull the tweets from redis
    key = keys.tweet_search_set(search_string)
    tweet_data = rc.sort(key,
                         by='nosort',
                         start=tweet_offset,
                         num=page_size,
                         get='tweets:*')

    log.debug('tweet data: %s', tweet_data)

    # return the data for the template
    return dict(
        tweet_data = tweet_data,
        tweet_offset = tweet_offset,
        page_size = page_size
    )


if __name__ == '__main__':
    log.debug('starting')
    run(application,
        host=config.get('host'),
        port=config.get('port'),
        reloader=True if DEBUG else False
    )
