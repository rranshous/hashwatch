

"""
simple wsgi app which produces a paged html
output of tweets
"""


class TweetPage:
    def GET(self, tweet_offset=0, page_size=20):

        # respect max page size
        page_size = max(page_size, config.get('max_page_size')

        # get our search term from config
        search_string = config.get('search_string')

        # pull the tweets from redis
        key = keys.tweet_search_set(search_string)
        tweet_data = rc.sort(key=key,
                             by='nosort',
                             limit=(tweet_offset,
                                    tweet_offset + page_size),
                             get='tweets:*')

        # render our template
        template = template_lookup.get_template('tweet_page.mako')
        html = template.render(tweet_data=tweet_data,
                               tweet_offset=tweet_offset,
                               page_size=page_size)

        # return our html to the client
        return html
