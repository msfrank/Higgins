{% extends "templates/library-base.t" %}

{% block title %}{{ album.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
    {{ album.name }}
    <br/>
    by <a href="/library/music/byartist/{{ album.artist.id }}/">{{ album.artist }}</a>
    <br/>
    {{ album.genre }}
    </p>
    <p>
        <table>
        {% for song in song_list %}
            <tr>
                <td>{{ song.track_number }}</td>
                <td><a href="/library/music/bysong/{{song.id}}/">{{ song.name }}</a></td>
            </tr>
        {% endfor %}
        </table>
    </p>
</div>
{% endblock %}
