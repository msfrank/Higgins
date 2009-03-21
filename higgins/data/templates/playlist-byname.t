{% extends "templates/library-base.t" %}

{% block stylesheet %}{% endblock %}

{% block title %}Browse playlists{% endblock %}

{% block library_content %}
<div>
    <p>
    Browsing playlists
    </p>
    <p>
        <ul>
        {% for playlist in pl_list %}
            <li><a href="/library/playlists/{{playlist.id}}/">{{ playlist.name }}</a></li>
        {% endfor %}
        </ul>
    </p>
</div>
{% endblock %}
