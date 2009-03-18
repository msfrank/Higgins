{% extends "templates/library-base.t" %}

{% block title %}{{ artist.name }}{% endblock %}

{% block library_content %}
<div>
    <p>
    {{ artist.name }}
    </p>
    <p>
        <table>
        {% for album in album_list %}
            <tr>
                <td>{{ album.release_date }}</td>
                <td><a href="/library/music/byalbum/{{album.id}}/">{{ album.name }}</a></td>
            </tr>
        {% endfor %}
        </table>
    </p>

</div>
{% endblock %}
