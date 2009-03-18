{% extends "templates/library-base.t" %}

{% block title %}{{ genre.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
    {{ genre.name }}
    </p>
    <p>
        <table>
        {% for album in album_list %}
            <tr><td>
                <a href="/library/music/byalbum/{{album.id}}/">{{ album.name }}</a> by 
                <a href="/library/music/byartist/{{album.artist.id}}/">{{ album.artist.name }}</a></td>
            </tr>
        {% endfor %}
        </table>
    </p>
</div>
{% endblock %}
