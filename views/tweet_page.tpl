
<html>

<head><title>Tweet Page ${(tweet_offset or 1) / page_size}</title></head>

<body>
    % for td in tweet_data:
    ${td.embed_html}
    <hr/>
    % endfor
</body>

</html>
