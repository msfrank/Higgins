{% extends "templates/base.t" %}

{% block stylesheet %}
    <link href="/static/css/song.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}{{ song.name }}{% endblock %}

{% block content %}
<div>
    <p id="song-title">{{ song.name }}</p>
    <br>
    from the album <a href="/browse/byalbum/{{ song.album.id }}/">{{song.album }}</a>
    by <a href="/browse/byartist/{{ song.artist.id }}/">{{ song.artist }}</a>
    </p>
</div>
{% endblock %}
