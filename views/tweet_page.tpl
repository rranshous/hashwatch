
<html>

<head>
    <title>${search_string}</title>
    <style>
        body { 
            background: url("/static/subtle_color.png") repeat scroll 0 0 transparent;
        }
        #embeds {
            width: 550px;
            margin: 0 auto;
        }
        #embeds > div {
            margin: 18px 0;
            box-shadow: 4px 4px black;
            border: 1px solid black;
        }
    </style>
</head>

<body>
    <h1>${search_string}</h1>
    <div class="nav">
        <b>Page ${max(1,tweet_offset / page_size)}</b>
        <a href="/${max(0,tweet_offset-page_size)}/">Prev</a>
        <a href="/${tweet_offset+page_size}/">Next</a>
    </div>
    <div id="embeds">
        % for embed_html in tweet_data:
        ${embed_html}
        % endfor
    </div>
    <div class="nav">
        <b>Page ${max(1,tweet_offset / page_size)}</b>
        <a href="/${max(0,tweet_offset-page_size)}/">Prev</a>
        <a href="/${tweet_offset+page_size}/">Next</a>
    </div>
</body>

</html>
