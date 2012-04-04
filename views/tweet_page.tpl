
<html>

<head><title>${search_string}</title></head>

<body>
    <h1>${search_string}</h1>
    % for embed_html in tweet_data:
    ${embed_html}
    % endfor
    <div class="nav">
        <a href="/${max(0,tweet_offset-page_size)}/">Prev</a>
        <a href="/${tweet_offset+page_size}/">Next</a>
    </div>
</body>

</html>
