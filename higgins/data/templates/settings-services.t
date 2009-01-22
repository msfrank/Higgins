{% extends "base.t" %}

{% block stylesheet %}
    <link href="/static/css/settings.css" rel="stylesheet" type="text/css" media="screen"/>
{% endblock %}

{% block title %}Edit Services{% endblock %}

{% block content %}
<p id="higgins-settings-description">
    All available services are listed below.  Checked services are currently running.
    To disable a service, uncheck it and click the Update Services button.  To configure
    a specific service, click on its Settings link.
</p>
<p>
<form id="higgins-settings-form" method="post" action="">
    <table id="higgins-settings-services">{% for item in service_items %}
        <tr>
            <td>
                <input type="checkbox"
                       name="{{item.name}}"
                       value="enabled"{% if item.service.running %} checked="true"{% endif %} />
            </td>
            <td>
                <span class="higgins-settings-service-name">{{item.service.name}}</span>
                <br/>
                <span class="higgins-settings-service-descripton">{{item.service.description}}<span>
            </td>
            <td>
                {% if item.config %}<a href="{{item.name}}/">Settings</a>{% endif %}
            </td>
        </tr>
    {% endfor %}</table>
    <p>
        <input id="higgins-settings-submit" type="submit" value="Update Services"/>
    </p>
</form>
</p>
{% endblock %}
