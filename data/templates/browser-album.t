{% extends "base.t" %}

{% block title %}{{ album.name }{% endblock %}

{% block content %}
<div>
    <p>
    {{ album.name }}
    <br/>
    by <a href="/browse/byartist/{{ album.artist.id }}">{{ album.artist }}</a>
    <br/>
    {{ album.genre }}
    </p>
    <p>
        <table>
        {% for song in song_list %}
            <tr>
                <td>{{ song.track_number }}</td>
                <td><a href="/browse/bysong/{{song.id}}">{{ song.name }}</a></td>
            </tr>
        {% endfor %}
        </table>
    </p>
</div>
{% endblock %}
