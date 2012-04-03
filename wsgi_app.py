

"""
simple wsgi app which produces a paged html
output of tweets
"""

from bottle import view as _view
from bottle import get, install, run, Bottle

from keys import keys
from configsmash import ConfigSmasher

import logging
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

DEBUG = True

# read in our config
if 'production' in sys.arg:
    config = ConfigSmasher(['production.ini']).smash()
else:
    config = ConfigSmasher(['development.ini']).smash()

# update the application to include plugins
install('redis')

# update the view decorator to use mako templates
# and define the lookup dir
def view(template,**kwargs):
    if not 'template_lookup' in kwargs:
        kwargs['template_lookup'] = 'templates/'
    return _view(template,**kwargs)


# default page
@get('/')
@get('/<tweet_offset>/<page_size>/')
@view('tweet_page')
def tweet_page(tweet_offset=0, page_size=20, rdb=None):
    """
    gets page worth of tweet data, returns data for template
    """

    # respect max page size
    page_size = max(page_size, config.get('max_page_size'))

    log.debug('tweet_page: %s %s', tweet_offset, page_size)

    # get our search term from config
    search_string = config.get('search_string')

    # pull the tweets from redis
    key = keys.tweet_search_set(search_string)
    tweet_data = rdb.sort(key=key,
                          by='nosort',
                          limit=(tweet_offset,
                                 tweet_offset + page_size),
                          get='tweets:*')

    log.debug('tweet data: %s', tweet_data)

    # return the data for the template
    return dict(
        tweet_data = tweet_data,
        tweet_offset = tweet_offset,
        page_size = page_size
    )

# create our application
application = Bottle()

if __name__ == '__main__':
    log.debug('starting')
    run(app,
        host=config.get('host'),
        port=config.get('port')
    )
