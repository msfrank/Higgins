{% extends "templates/base.t" %}

{% block stylesheet %}{% endblock %}

{% block title %}Browse by genre{% endblock %}

{% block content %}
<div>
    <p>
    Browsing by Genre
    </p>
    <p>
        <ul>
        {% for genre in genre_list %}
            <li><a href="/browse/bygenre/{{genre.id}}/">{{ genre.name }}</a></li>
        {% endfor %}
        </ul>
    </p>
</div>
{% endblock %}
