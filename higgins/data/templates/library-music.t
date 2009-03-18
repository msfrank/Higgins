{% extends "templates/library-base.t" %}

{% block stylesheet %}
<link href="/static/css/browse.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Browse music{% endblock %}

{% block library_content %}
<div id="browse">
    <span id="browse-title">Browse Your Music</span>
    <ul id="browse-list">
        <li><a id="browse-byartist" href="/library/music/artists/">By Artist</a></li>
        <li><a id="browse-bygenre" href="/library/music/genres/">By Genre</a></li>
        <li><a id="browse-bytags" href="/library/music/tags/">By Tag</a></li>
    </ul>
</div>

<div id="latest">
    <span id="latest-title">Latest Song Additions</span>
    {% if latest_list %}
    <ol id="latest-list">
    {% for song in latest_list %}
        <li>
            <a href="/library/music/bysong/{{ song.id }}/">{{ song.name }}</a> by
            <a href="/library/music/byartist/{{song.artist.id }}/">{{ song.artist.name }}</a>
        </li>
    {% endfor %}
    </ol>
    {% else %}
        <p>No data for newest additions.</p>
    {% endif %}
</div>

<div id="popular">
    <span id="popular-title">Most Popular Selections</span>
    {% if popular_list %}
    <ul>
        {% for song in popular_list %}
        <li id="popular-list">
            <a href="/library/music/bysong/{{ song.id }}/">{{ song.name }}</a> by
            <a href="/library/music/byartist/{{song.artist.id }}/">{{ song.artist.name }}</a>
        </li>
    {% endfor %}
    </ul>
    {% else %}
        <p>No data for most popular songs.</p>
    {% endif %}
</div>
{% endblock %}
