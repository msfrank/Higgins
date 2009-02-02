{% extends "base.t" %}

{% block stylesheet %}
    <link href="/static/css/settings.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Settings{% endblock %}

{% block subnav %}
    <table id="higgins-settings-nav">
        <tr>
            <td>
                <span class="higgins-settings-nav-item">
                    <a href="/settings/services/">Services</a>
                </span>
            </td>
            {% for item in config_items %}<td>
                <span class="higgins-settings-nav-item">
                    <a href="/settings/{{item.name}}/">{{item.config.config_name}}</a>
                </span>
            </td>
        {% endfor %}</tr>
    </table>
{% endblock %}
{% block content %}
    <div id="higgins-settings-content">
{% block settings_content %}{% endblock %}
    </div>
{% endblock %}
