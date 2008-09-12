{% extends "base.t" %}

{% block title %}{{ genre.name }{% endblock %}

{% block content %}
<div>
    <p>
    {{ genre.name }}
    </p>
    <p>
        <table>
        {% for album in album_list %}
            <tr><td>
                <a href="/browse/byalbum/{{album.id}}">{{ album.name }}</a> by 
                <a href="/browse/byartist/{{album.artist.id}}">{{ album.artist.name }}</a></td>
            </tr>
        {% endfor %}
        </table>
    </p>
</div>
{% endblock %}
