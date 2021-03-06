{% extends "templates/base.t" %}

{% block stylesheet %}
    <link href="/static/css/settings.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Settings{% endblock %}

{% block subnav %}
    <table id="higgins-base-subnav">
        <tr>
            <td>
                <span class="higgins-base-subnav-item">
                    <a href="/settings/plugins/">Plugins</a>
                </span>
            </td>
            {% for item in config_items %}<td>
                <span class="higgins-base-subnav-item">
                    <a href="/settings/{{item.name}}/">{{item.config.pretty_name}}</a>
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
