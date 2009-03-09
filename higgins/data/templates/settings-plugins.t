{% extends "settings-base.t" %}

{% block title %}Edit Services{% endblock %}

{% block settings_content %}
    <p id="higgins-settings-description">
        All available services are listed below.  Checked services are currently running.
        To disable a service, uncheck it and click the Update Services button.  To configure
        a specific service, click on its Settings link.
    </p>
    <p>
    <form id="higgins-settings-form" method="post" action="">
        <table id="higgins-settings-plugins">{% for plugin in plugins %}
            <tr>
                <td>
                    <input type="checkbox"
                           name="{{plugin.name}}"
                           value="enabled"{% if plugin.running %} checked="true"{% endif %} />
                </td>
                <td>
                    <span class="higgins-settings-plugin-name">{{plugin.pretty_name}}</span>
                    <br/>
                    <span class="higgins-settings-plugin-descripton">{{plugin.description}}<span>
                </td>
                <td>
                    {% ifnotequal plugin.configs None %}<a href="{{plugin.name}}/">Settings</a>{% endifnotequal %}
                </td>
            </tr>
        {% endfor %}</table>
        <p>
            <input id="higgins-settings-submit" type="submit" value="Update Services"/>
        </p>
    </form>
    </p>
{% endblock %}
