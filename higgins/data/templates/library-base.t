{% extends "templates/base.t" %}

{% block stylesheet %}
    <link href="/static/css/browse.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Library{% endblock %}

{% block subnav %}
    <table id="higgins-base-subnav">
        <tr>
            <td>
                <span class="higgins-base-subnav-item">
                    <a href="/library/music/">Music</a>
                </span>
            </td>
            <td>
                <span class="higgins-base-subnav-item">
                    <a href="/library/playlist/">Playlists</a>
                </span>
            </td>
        </tr>
    </table>
{% endblock %}
{% block content %}
    <div id="higgins-library-content">{% block library_content %}{% endblock %}
    </div>
{% endblock %}
