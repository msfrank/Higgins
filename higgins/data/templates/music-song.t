{% extends "templates/library-base.t" %}

{% block title %}{{ song.name }}{% endblock %}

{% block library_content %}
<div>
    <p id="song-title">{{ song.name }}</p>
    <br>
    from the album <a href="/library/music/byalbum/{{ song.album.id }}/">{{song.album }}</a>
    by <a href="/library/music/byartist/{{ song.artist.id }}/">{{ song.artist }}</a>
    </p>
</div>
{% endblock %}
