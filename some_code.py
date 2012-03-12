

api = twitter.Api()
search_results =

api.GetSearch(self, term=None, geocode=None, since_id=None, per_page=15, page=1, lang='en', show_user='true', query_users=False)

consumer = oembed.OEmbedConsumer()
endpoint = oembed.OEmbedEndpoint('https://api.twitter.com/1/statuses/oembed.json',['https://twitter.com/*'])
consumer.addEndpoint(endpoint)
