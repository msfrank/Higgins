{% extends "templates/library-base.t" %}

{% block stylesheet %}{% endblock %}

{% block title %}Browse by genre{% endblock %}

{% block library_content %}
<div>
    <p>
    Browsing by Genre
    </p>
    <p>
        <ul>
        {% for genre in genre_list %}
            <li><a href="/library/music/bygenre/{{genre.id}}/">{{ genre.name }}</a></li>
        {% endfor %}
        </ul>
    </p>
</div>
{% endblock %}
