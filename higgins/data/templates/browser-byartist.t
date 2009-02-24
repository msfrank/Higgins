{% extends "base.t" %}

{% block stylesheet %}{% endblock %}

{% block title %}Browse by artist{% endblock %}

{% block content %}
<div>
    <p>
    Browsing by Artist
    </p>
    <p>
        <ul>
        {% for artist in artist_list %}
            <li><a href="/browse/byartist/{{artist.id}}/">{{ artist.name }}</a></li>
        {% endfor %}
        </ul>
    </p>
</div>
{% endblock %}
